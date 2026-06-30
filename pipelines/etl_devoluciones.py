"""
ETL de devoluciones — carga devoluciones CSV a DuckDB aplicando transformaciones
según memoria/metricas/devoluciones.md.

Modos:
  reemplazar (default): recrea la tabla completa desde el archivo.
  acumular:             inserta solo filas nuevas (deduplica por id_devolucion).
"""
import polars as pl
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/devoluciones_q3_2026.csv")
TABLE_NAME = "devoluciones"
PK = "id_devolucion"


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns([
            pl.col("fecha_devolucion").cast(pl.Date),
            pl.col("cantidad_devuelta").cast(pl.Int32),
            pl.col("precio_unitario").cast(pl.Float64),
            pl.col("reembolso").cast(pl.Float64),
            pl.col("motivo").str.to_lowercase(),
            pl.col("estado").str.to_lowercase(),
            pl.col("canal_devolucion").str.to_lowercase(),
        ])
        # Columnas derivadas según memoria/metricas/devoluciones.md
        .with_columns([
            (pl.col("cantidad_devuelta") * pl.col("precio_unitario"))
                .alias("valor_devolucion"),
            pl.col("fecha_devolucion").dt.truncate("1mo").alias("mes"),
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
        print(f"  Modo acumular: {insertadas} devoluciones nuevas, {omitidas} ya existían.")
        print(f"  Total en '{TABLE_NAME}': {total} devoluciones.")
    else:
        filas = db.load_table(df_clean, TABLE_NAME, replace=True)
        print(f"  Tabla '{TABLE_NAME}' reemplazada: {filas} devoluciones.")


if __name__ == "__main__":
    run()