"""
ETL de campañas — carga campañas CSV a DuckDB aplicando transformaciones
según memoria/metricas/campanas.md.
"""
import polars as pl
from datetime import date
from pathlib import Path
from core_agent.skills import duckdb_client as db

RAW_PATH_DEFAULT = Path("data/raw/campanas_demo.csv")
TABLE_NAME = "campanas"
PK = "id_campana"

CANALES_VALIDOS = ["email", "redes_sociales", "display", "search", "video"]


def extract(archivo: str | None = None) -> pl.DataFrame:
    ruta = Path("data/raw") / archivo if archivo else RAW_PATH_DEFAULT
    return pl.read_csv(ruta)


def transform(df: pl.DataFrame) -> pl.DataFrame:
    today = date.today()
    return (
        df
        .with_columns([
            pl.col("fecha_inicio").cast(pl.Date),
            pl.col("fecha_fin").cast(pl.Date),
            pl.col("presupuesto").cast(pl.Float64),
            pl.col("gasto_real").cast(pl.Float64),
            pl.col("impresiones").cast(pl.Int64),
            pl.col("clicks").cast(pl.Int64),
            pl.col("conversiones").cast(pl.Int64),
            pl.col("ingresos_atribuidos").cast(pl.Float64),
            pl.col("canal").str.to_lowercase(),
        ])
        # Columnas derivadas según memoria/metricas/campanas.md
        .with_columns([
            pl.when(pl.col("fecha_fin") < pl.lit(today))
                .then(pl.lit("finalizada"))
                .when(pl.col("fecha_inicio") > pl.lit(today))
                .then(pl.lit("futura"))
                .otherwise(pl.lit("activa"))
                .alias("estado"),
            (pl.col("fecha_fin").cast(pl.Int32) - pl.col("fecha_inicio").cast(pl.Int32) + 1)
                .alias("duracion_dias"),
            (pl.col("gasto_real") / pl.col("presupuesto") * 100).round(1)
                .alias("ejecucion_presupuesto"),
            pl.when(pl.col("impresiones") > 0)
                .then((pl.col("clicks") / pl.col("impresiones") * 100).round(2))
                .otherwise(None)
                .alias("ctr"),
            pl.when(pl.col("clicks") > 0)
                .then((pl.col("conversiones") / pl.col("clicks") * 100).round(2))
                .otherwise(None)
                .alias("tasa_conversion"),
            pl.when(pl.col("clicks") > 0)
                .then((pl.col("gasto_real") / pl.col("clicks")).round(0))
                .otherwise(None)
                .alias("cpc"),
            pl.when(pl.col("conversiones") > 0)
                .then((pl.col("gasto_real") / pl.col("conversiones")).round(0))
                .otherwise(None)
                .alias("cpa"),
            pl.when(pl.col("gasto_real") > 0)
                .then((pl.col("ingresos_atribuidos") / pl.col("gasto_real")).round(2))
                .otherwise(None)
                .alias("roas"),
            pl.when(pl.col("gasto_real") > 0)
                .then(((pl.col("ingresos_atribuidos") - pl.col("gasto_real")) / pl.col("gasto_real") * 100).round(1))
                .otherwise(None)
                .alias("roi"),
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
        print(f"  Modo acumular: {insertadas} campañas nuevas, {omitidas} ya existían.")
        print(f"  Total en '{TABLE_NAME}': {total} campañas.")
    else:
        filas = db.load_table(df_clean, TABLE_NAME, replace=True)
        print(f"  Tabla '{TABLE_NAME}' reemplazada: {filas} campañas.")


if __name__ == "__main__":
    run()