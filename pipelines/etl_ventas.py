"""
ETL de ventas — carga ventas a DuckDB aplicando transformaciones
según memoria/metricas/ventas.md.

Modos:
  reemplazar (default): recrea la tabla completa desde el archivo.
  acumular:             inserta solo filas nuevas (deduplica por id_orden).
"""
import polars as pl
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/ventas_demo.csv")
TABLE_NAME = "ventas"
PK = "id_orden"


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns([
            pl.col("fecha").cast(pl.Date),
            pl.col("cantidad").cast(pl.Int32),
            pl.col("precio_unitario").cast(pl.Float64),
            pl.col("estado").str.to_lowercase(),
            pl.col("canal").str.to_lowercase(),
        ])
        .with_columns(
            (pl.col("precio_unitario") * pl.col("cantidad")).alias("ingreso_linea")
        )
        .with_columns(
            pl.col("fecha").dt.truncate("1mo").alias("mes")
        )
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
        print(f"  Modo acumular: {insertadas} filas nuevas insertadas, {omitidas} ya existían.")
        print(f"  Total acumulado en '{TABLE_NAME}': {total} filas.")
    else:
        filas = db.load_table(df_clean, TABLE_NAME, replace=True)
        print(f"  Tabla '{TABLE_NAME}' reemplazada: {filas} filas.")


if __name__ == "__main__":
    run()