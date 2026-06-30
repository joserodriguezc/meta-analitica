"""
ETL de inventario — carga inventario CSV a DuckDB aplicando transformaciones
según memoria/metricas/inventario.md.
"""
import polars as pl
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/inventario_agosto.csv")
TABLE_NAME = "inventario"
PK = "id_producto"


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns([
            pl.col("fecha_actualizacion").cast(pl.Date),
            pl.col("stock_actual").cast(pl.Int32),
            pl.col("stock_minimo").cast(pl.Int32),
            pl.col("precio_costo").cast(pl.Float64),
            pl.col("precio_venta").cast(pl.Float64),
            pl.col("estado").str.to_lowercase(),
        ])
        # Columnas calculadas según memoria/metricas/inventario.md
        .with_columns([
            (pl.col("stock_actual") * pl.col("precio_costo")).alias("valor_stock"),
            ((pl.col("precio_venta") - pl.col("precio_costo")) / pl.col("precio_venta") * 100)
                .round(1).alias("margen_bruto"),
            (pl.col("stock_actual") < pl.col("stock_minimo")).alias("bajo_minimo"),
            (pl.col("stock_actual") / pl.col("stock_minimo")).round(2).alias("cobertura"),
        ])
    )


def run(archivo: str | None = None, acumular: bool = False):
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    print(f"  Leyendo {ruta}...")
    df_raw = extract(archivo)

    print(f"  Transformando {len(df_raw)} filas...")
    df_clean = transform(df_raw)

    if acumular:
        insertadas, omitidas = db.append_new_rows(df_clean, TABLE_NAME, pk=PK)
        total = db.row_count(TABLE_NAME)
        print(f"  Modo acumular: {insertadas} productos nuevos, {omitidas} ya existían.")
        print(f"  Total en '{TABLE_NAME}': {total} productos.")
    else:
        filas = db.load_table(df_clean, TABLE_NAME, replace=True)
        print(f"  Tabla '{TABLE_NAME}' reemplazada: {filas} productos.")


if __name__ == "__main__":
    run()