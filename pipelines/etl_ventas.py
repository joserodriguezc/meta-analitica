"""
ETL de ventas — carga ventas_demo.csv a DuckDB aplicando transformaciones
según memoria/metricas/ventas.md.
"""
import polars as pl
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/ventas_demo.csv")
TABLE_NAME = "ventas"


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        # Normalizar tipos
        .with_columns([
            pl.col("fecha").cast(pl.Date),
            pl.col("cantidad").cast(pl.Int32),
            pl.col("precio_unitario").cast(pl.Float64),
            pl.col("estado").str.to_lowercase(),
            pl.col("canal").str.to_lowercase(),
        ])
        # Columna calculada: ingreso por línea
        .with_columns(
            (pl.col("precio_unitario") * pl.col("cantidad")).alias("ingreso_linea")
        )
        # Columna: mes para agregaciones
        .with_columns(
            pl.col("fecha").dt.truncate("1mo").alias("mes")
        )
    )


def load(df: pl.DataFrame) -> int:
    return db.load_table(df, TABLE_NAME, replace=True)


def run(archivo: str | None = None):
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    print(f"  Leyendo {ruta}...")
    df_raw = extract(archivo)

    print(f"  Transformando {len(df_raw)} filas...")
    df_clean = transform(df_raw)

    filas = load(df_clean)
    print(f"  Tabla '{TABLE_NAME}' cargada: {filas} filas.")


if __name__ == "__main__":
    run()
