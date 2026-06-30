"""
ETL de envíos — carga envios CSV a DuckDB aplicando transformaciones
según memoria/metricas/envios.md.

Modos:
  reemplazar (default): recrea la tabla completa desde el archivo.
  acumular:             inserta solo filas nuevas (deduplica por id_envio).
"""
import polars as pl
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/envios_q3_2026.csv")
TABLE_NAME = "envios"
PK = "id_envio"


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df
        .with_columns([
            pl.col("fecha_despacho").cast(pl.Date),
            pl.col("fecha_entrega_estimada").cast(pl.Date),
            # strict=False para convertir cadenas vacías / nulos en null
            pl.col("fecha_entrega_real").str.to_date(format="%Y-%m-%d", strict=False),
            pl.col("costo_envio").cast(pl.Float64),
            pl.col("peso_kg").cast(pl.Float64),
            pl.col("courier").str.to_lowercase(),
            pl.col("tipo_envio").str.to_lowercase(),
            pl.col("estado").str.to_lowercase(),
        ])
        # Columnas derivadas según memoria/metricas/envios.md
        .with_columns([
            pl.when(pl.col("fecha_entrega_real").is_not_null())
            .then(
                (pl.col("fecha_entrega_real") - pl.col("fecha_entrega_estimada"))
                .dt.total_days()
            )
            .otherwise(None)
            .cast(pl.Int64)
            .alias("dias_retraso"),
            pl.col("fecha_despacho").dt.truncate("1mo").alias("mes"),
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
        print(f"  Modo acumular: {insertadas} envíos nuevos, {omitidas} ya existían.")
        print(f"  Total en '{TABLE_NAME}': {total} envíos.")
    else:
        filas = db.load_table(df_clean, TABLE_NAME, replace=True)
        print(f"  Tabla '{TABLE_NAME}' reemplazada: {filas} envíos.")


if __name__ == "__main__":
    run()
