"""
Validaciones de calidad para la tabla ventas.
Esquema basado en memoria/metricas/ventas.md.
"""
import pandera.polars as pa
import polars as pl
from typing import Optional
from core_agent.skills import duckdb_client as db

ESTADOS_VALIDOS = ["completado", "cancelado", "pendiente"]
CANALES_VALIDOS = ["online", "tienda", "marketplace"]

schema_ventas = pa.DataFrameSchema(
    columns={
        "id_orden": pa.Column(
            str,
            nullable=False,
            unique=True,
            description="Identificador único de orden",
        ),
        "fecha": pa.Column(
            pl.Date,
            nullable=False,
            checks=pa.Check(
                lambda x: x.year >= 2020,
                element_wise=True,
                error="Fecha anterior al año 2020",
            ),
            description="Fecha de la transacción",
        ),
        "id_producto": pa.Column(str, nullable=False),
        "nombre_producto": pa.Column(str, nullable=False),
        "categoria": pa.Column(str, nullable=False),
        "cantidad": pa.Column(
            pl.Int32,
            nullable=False,
            checks=pa.Check.greater_than(0, error="Cantidad debe ser mayor a 0"),
        ),
        "precio_unitario": pa.Column(
            pl.Float64,
            nullable=False,
            checks=pa.Check.greater_than(0, error="Precio unitario debe ser mayor a 0"),
        ),
        "estado": pa.Column(
            str,
            nullable=False,
            checks=pa.Check.isin(ESTADOS_VALIDOS, error=f"Estado debe ser uno de: {ESTADOS_VALIDOS}"),
        ),
        "canal": pa.Column(
            str,
            nullable=True,
            checks=pa.Check(
                lambda x: x is None or x in CANALES_VALIDOS,
                element_wise=True,
                error=f"Canal debe ser uno de: {CANALES_VALIDOS}",
            ),
        ),
        "id_sesion": pa.Column(str, nullable=True),
        "ingreso_linea": pa.Column(
            pl.Float64,
            nullable=False,
            checks=pa.Check.greater_than(0, error="Ingreso por línea debe ser positivo"),
        ),
        "mes": pa.Column(pl.Date, nullable=False),
    },
    name="ventas",
)


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
    tablas = [tabla] if tabla else ["ventas"]

    for nombre in tablas:
        print(f"\nValidando tabla '{nombre}'...")

        if not db.table_exists(nombre):
            print(f"  ERROR: La tabla '{nombre}' no existe en DuckDB.")
            print(f"  Ejecuta primero: uv run main.py etl")
            raise SystemExit(1)

        df = db.query(f"SELECT * FROM {nombre}")

        try:
            schema_ventas.validate(df, lazy=True)
            filas = db.row_count(nombre)
            print(f"  OK: {filas} filas validadas sin errores.")

        except pa.errors.SchemaErrors as e:
            n_errores = len(e.failure_cases)
            print(f"  FALLO: {n_errores} error(es) de calidad detectado(s).")
            print(_formatear_errores(e))
            raise SystemExit(1)


if __name__ == "__main__":
    run()
