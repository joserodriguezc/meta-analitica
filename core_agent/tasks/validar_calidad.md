# Receta: Validar Calidad de Datos

Sigue estos pasos para crear o actualizar validaciones de calidad sobre una tabla en DuckDB.

## Paso 1 — Leer el esquema esperado

Consultar `memoria/metricas/<dominio>.md`, sección **"Esquema Esperado de Datos Crudos"** y **"Reglas de Negocio"**.

## Paso 2 — Leer los datos desde DuckDB

```python
import duckdb
import polars as pl

conn = duckdb.connect("data/local.duckdb")
df = conn.execute("SELECT * FROM <dominio>").pl()
conn.close()
```

## Paso 3 — Definir el esquema Pandera

Crear o actualizar `pipelines/calidad.py` con la siguiente estructura:

```python
import pandera.polars as pa
import polars as pl
import duckdb
from pathlib import Path

DB_PATH = Path("data/local.duckdb")

# Definir esquema según memoria/metricas/<dominio>.md
schema = pa.DataFrameSchema(
    columns={
        "id_orden": pa.Column(str, nullable=False, unique=True),
        "fecha": pa.Column(str, nullable=False),
        "cantidad": pa.Column(int, pa.Check.greater_than(0)),
        "precio_unitario": pa.Column(float, pa.Check.greater_than(0)),
        "estado": pa.Column(str, pa.Check.isin(["completado", "cancelado", "pendiente"])),
    }
)

def run():
    conn = duckdb.connect(str(DB_PATH))
    df = conn.execute("SELECT * FROM ventas").pl()
    conn.close()

    try:
        schema.validate(df, lazy=True)
        print("Calidad OK: todos los datos son válidos.")
    except pa.errors.SchemaErrors as e:
        print("Errores de calidad encontrados:")
        print(e.failure_cases)
        raise SystemExit(1)

if __name__ == "__main__":
    run()
```

## Paso 4 — Verificar

```bash
uv run main.py test
```

La consola debe mostrar `Calidad OK` o listar los errores encontrados con detalle de fila y columna.

## Paso 5 — Criterio de bloqueo

Si `main.py test` retorna código de salida 1, el comando `deploy` no debe ejecutarse.
Este comportamiento ya está implementado en `main.py`.
