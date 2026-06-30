# Receta: Crear un ETL

Sigue estos pasos en orden para crear un nuevo pipeline de ingesta de datos.

## Paso 1 — Leer el contexto de negocio

Antes de escribir código, leer:
- `memoria/index.md` para identificar el dominio
- `memoria/metricas/<dominio>.md` para conocer el esquema esperado y las reglas de negocio
- `memoria/clientes/<cliente>.md` para entender la fuente de datos

## Paso 2 — Verificar la fuente de datos

Confirmar que el archivo de entrada existe en `data/raw/`.

```python
# Verificar con DuckDB
import duckdb
conn = duckdb.connect()
conn.execute("SELECT * FROM read_csv_auto('data/raw/<archivo>.csv') LIMIT 5").df()
```

## Paso 3 — Crear el script ETL

Crear el archivo `pipelines/etl_<dominio>.py` con la siguiente estructura:

```python
import duckdb
import polars as pl
from pathlib import Path

RAW_PATH = Path("data/raw/<archivo>.csv")
DB_PATH = Path("data/local.duckdb")
TABLE_NAME = "<dominio>"

def extract() -> pl.DataFrame:
    """Lee el archivo crudo sin modificarlo."""
    return pl.read_csv(RAW_PATH)

def transform(df: pl.DataFrame) -> pl.DataFrame:
    """Aplica transformaciones según memoria/metricas/<dominio>.md."""
    # Filtrar cancelados, normalizar tipos, etc.
    return df

def load(df: pl.DataFrame) -> None:
    """Carga el DataFrame transformado en DuckDB."""
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(f"CREATE OR REPLACE TABLE {TABLE_NAME} AS SELECT * FROM df")
    conn.close()

def run():
    df = extract()
    df = transform(df)
    load(df)
    print(f"ETL completado: {len(df)} filas cargadas en tabla '{TABLE_NAME}'")

if __name__ == "__main__":
    run()
```

## Paso 4 — Registrar en el CLI

Agregar la invocación del nuevo ETL en `main.py` dentro del comando `etl`:

```python
from pipelines.etl_<dominio> import run as etl_<dominio>
etl_<dominio>()
```

## Paso 5 — Verificar

```bash
uv run main.py etl
```

La consola debe mostrar la cantidad de filas cargadas sin errores.

## Paso 6 — Registrar en la bitácora

Agregar una entrada en `memoria/log.md` con la fecha y descripción del ETL creado.
