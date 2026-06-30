"""
Validaciones de calidad para todas las tablas del proyecto.
Esquemas basados en memoria/metricas/*.md.
"""
import pandera.polars as pa
import polars as pl
from typing import Optional
from core_agent.skills import duckdb_client as db

# ── VENTAS ────────────────────────────────────────────────────────────────────

ESTADOS_VENTAS = ["completado", "cancelado", "pendiente"]
CANALES_VALIDOS = ["online", "tienda", "marketplace"]

schema_ventas = pa.DataFrameSchema(
    columns={
        "id_orden": pa.Column(str, nullable=False, unique=True),
        "fecha": pa.Column(
            pl.Date, nullable=False,
            checks=pa.Check(lambda x: x.year >= 2020, element_wise=True,
                            error="Fecha anterior al año 2020"),
        ),
        "id_producto": pa.Column(str, nullable=False),
        "nombre_producto": pa.Column(str, nullable=False),
        "categoria": pa.Column(str, nullable=False),
        "cantidad": pa.Column(pl.Int32, nullable=False,
                              checks=pa.Check.greater_than(0, error="Cantidad debe ser mayor a 0")),
        "precio_unitario": pa.Column(pl.Float64, nullable=False,
                                     checks=pa.Check.greater_than(0, error="Precio unitario debe ser mayor a 0")),
        "estado": pa.Column(str, nullable=False,
                            checks=pa.Check.isin(ESTADOS_VENTAS, error=f"Estado debe ser uno de: {ESTADOS_VENTAS}")),
        "canal": pa.Column(str, nullable=True,
                           checks=pa.Check(lambda x: x is None or x in CANALES_VALIDOS,
                                           element_wise=True, error=f"Canal debe ser uno de: {CANALES_VALIDOS}")),
        "id_sesion": pa.Column(str, nullable=True),
        "ingreso_linea": pa.Column(pl.Float64, nullable=False,
                                   checks=pa.Check.greater_than(0, error="Ingreso por línea debe ser positivo")),
        "mes": pa.Column(pl.Date, nullable=False),
    },
    name="ventas",
)

# ── INVENTARIO ────────────────────────────────────────────────────────────────

ESTADOS_INVENTARIO = ["activo", "agotado", "descontinuado"]

schema_inventario = pa.DataFrameSchema(
    columns={
        "id_producto": pa.Column(str, nullable=False, unique=True),
        "nombre_producto": pa.Column(str, nullable=False),
        "categoria": pa.Column(str, nullable=False),
        "stock_actual": pa.Column(
            pl.Int32, nullable=False,
            checks=pa.Check.greater_than_or_equal_to(0, error="Stock actual no puede ser negativo"),
        ),
        "stock_minimo": pa.Column(
            pl.Int32, nullable=False,
            checks=pa.Check.greater_than(0, error="Stock mínimo debe ser mayor a 0"),
        ),
        "precio_costo": pa.Column(
            pl.Float64, nullable=False,
            checks=pa.Check.greater_than(0, error="Precio costo debe ser mayor a 0"),
        ),
        "precio_venta": pa.Column(
            pl.Float64, nullable=False,
            checks=pa.Check.greater_than(0, error="Precio venta debe ser mayor a 0"),
        ),
        "bodega": pa.Column(str, nullable=False),
        "fecha_actualizacion": pa.Column(pl.Date, nullable=False),
        "estado": pa.Column(
            str, nullable=False,
            checks=pa.Check.isin(ESTADOS_INVENTARIO, error=f"Estado debe ser uno de: {ESTADOS_INVENTARIO}"),
        ),
        "valor_stock": pa.Column(pl.Float64, nullable=False),
        "margen_bruto": pa.Column(pl.Float64, nullable=False),
        "bajo_minimo": pa.Column(pl.Boolean, nullable=False),
        "cobertura": pa.Column(pl.Float64, nullable=False),
    },
    name="inventario",
)

# ── MOTOR ─────────────────────────────────────────────────────────────────────

SCHEMAS = {
    "ventas": schema_ventas,
    "inventario": schema_inventario,
}


def _formatear_errores(errores: pa.errors.SchemaErrors) -> str:
    casos = errores.failure_cases
    lineas = ["", "  ERRORES ENCONTRADOS:", "  " + "-" * 40]
    for row in casos.to_dicts():
        check = row.get("check", "?")
        col = row.get("column", "?")
        valor = row.get("failure_case", "?")
        idx = row.get("index", "?")
        lineas.append(f"  [fila {idx}] columna '{col}': {check} — valor: {valor!r}")
    return "\n".join(lineas)


def run(tabla: Optional[str] = None):
    tablas = [tabla] if tabla else list(SCHEMAS.keys())

    for nombre in tablas:
        print(f"\nValidando tabla '{nombre}'...")

        if not db.table_exists(nombre):
            print(f"  ERROR: La tabla '{nombre}' no existe en DuckDB.")
            print(f"  Ejecuta primero: uv run main.py etl {nombre}")
            raise SystemExit(1)

        if nombre not in SCHEMAS:
            print(f"  AVISO: No hay esquema definido para '{nombre}'. Saltando.")
            continue

        df = db.query(f"SELECT * FROM {nombre}")

        try:
            SCHEMAS[nombre].validate(df, lazy=True)
            filas = db.row_count(nombre)
            print(f"  OK: {filas} filas validadas sin errores.")

        except pa.errors.SchemaErrors as e:
            n_errores = len(e.failure_cases)
            print(f"  FALLO: {n_errores} error(es) de calidad detectado(s).")
            print(_formatear_errores(e))
            raise SystemExit(1)


if __name__ == "__main__":
    run()