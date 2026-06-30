# Receta: Crear un Reporte

Sigue estos pasos para generar un reporte HTML estático con Marimo conectado a DuckDB.

## Paso 1 — Leer el contexto del cliente

Consultar `memoria/clientes/<cliente>.md`, sección **"Reporte Principal"** para conocer las visualizaciones requeridas.

Consultar `memoria/metricas/<dominio>.md` para usar las fórmulas correctas en las queries SQL.

## Paso 2 — Crear el archivo del reporte

Crear `reports/<dominio>.py` con la siguiente estructura:

```python
import marimo as mo
import duckdb
import polars as pl

# Conexión a DuckDB
conn = duckdb.connect("data/local.duckdb", read_only=True)

app = mo.App()

@app.cell
def titulo():
    return mo.md("# Reporte de <Dominio>")

@app.cell
def kpi_ingresos():
    df = conn.execute("""
        SELECT
            DATE_TRUNC('month', fecha::DATE) AS mes,
            SUM(precio_unitario * cantidad) AS ingresos_totales
        FROM ventas
        WHERE estado = 'completado'
        GROUP BY 1
        ORDER BY 1
    """).pl()
    return mo.ui.table(df)

@app.cell
def top_productos():
    df = conn.execute("""
        SELECT
            nombre_producto,
            SUM(cantidad) AS unidades_vendidas
        FROM ventas
        WHERE estado = 'completado'
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 5
    """).pl()
    return mo.ui.table(df)

if __name__ == "__main__":
    app.run()
```

## Paso 3 — Probar el reporte en modo interactivo

```bash
uv run marimo edit reports/<dominio>.py
```

Verificar que todas las celdas renderizan correctamente.

## Paso 4 — Exportar a HTML estático

El comando `deploy` en el CLI ejecuta:

```bash
uv run marimo export html reports/<dominio>.py -o reports/<dominio>.html
```

## Paso 5 — Verificar el deploy

```bash
uv run main.py deploy
```

La consola debe indicar la ruta del archivo HTML generado.

## Paso 6 — Registrar en la bitácora

Agregar una entrada en `memoria/log.md` describiendo el reporte creado y las visualizaciones incluidas.
