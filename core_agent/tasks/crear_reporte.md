---
type: task_recipe
title: "Receta: Crear un Reporte"
description: "Procedimiento para generar un dashboard Streamlit interactivo con chart_builder conectado a DuckDB"
resource: "reports/{dominio}.py"
tags: [reporte, streamlit, plotly, dashboard, chart_builder]
timestamp: "2026-07-11"
---

# Receta: Crear un Reporte

Sigue estos pasos para generar un reporte Streamlit interactivo conectado a DuckDB.

## Paso 1 — Leer el contexto del cliente

Consultar `memoria/clientes/<cliente>.md`, sección **"Reporte Principal"** para conocer las visualizaciones requeridas.

Consultar `memoria/metricas/<dominio>.md` para usar las fórmulas correctas en las queries SQL.

## Paso 2 — Crear el archivo del reporte

Crear `reports/<dominio>.py` con la siguiente estructura:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from core_agent.skills.chart_builder import (
    inject_css, sidebar_logo, page_header, kpi,
    barras, linea, pie, scatter, treemap, heatmap,
)
from core_agent.skills import duckdb_client as db

st.set_page_config(page_title="<Dominio> — MalayAI", layout="wide")
inject_css()
sidebar_logo()
page_header("<Dominio>", "<subtítulo descriptivo>")

# ── Filtros en sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    opciones = db.query("SELECT DISTINCT <columna> FROM <dominio> ORDER BY 1")["<columna>"].to_list()
    seleccion = st.multiselect("<Filtro>", opciones, default=opciones)

# ── Carga de datos ─────────────────────────────────────────────────────────────
df = db.query(f"""
    SELECT * FROM <dominio>
    WHERE <columna> IN ({", ".join(f"'{v}'" for v in seleccion)})
""")

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Métrica 1", df["col1"].sum(), icon="📊")
with c2: kpi("Métrica 2", df["col2"].mean(), icon="📈")

# ── Gráficos ──────────────────────────────────────────────────────────────────
st.plotly_chart(barras(df, x="categoria", y="valor", titulo="Título"), use_container_width=True)

# ── Tabla detalle ─────────────────────────────────────────────────────────────
with st.expander("Ver datos completos"):
    st.dataframe(df, use_container_width=True)
```

## Paso 3 — Registrar en app.py

Agregar la nueva página en `app.py`:

```python
# En la sección de páginas
nuevo = st.Page("reports/<dominio>.py", title="<Dominio>", icon="<emoji>")

# En st.navigation
pg = st.navigation({"Analítica": [..., nuevo]}, position="hidden")

# En la sección de sidebar
st.page_link(nuevo, label="<Dominio>", icon="<emoji>")
```

## Paso 4 — Verificar el reporte

```bash
uv run main.py deploy <dominio>   # reporte individual
uv run main.py deploy             # app unificada con todos los dominios
```

## Paso 5 — Registrar en la bitácora

Agregar una entrada en `memoria/log.md` describiendo el reporte creado y las visualizaciones incluidas.

## Vínculos

- **Paso anterior:** [Crear un ETL](./crear_etl.md) — carga los datos en DuckDB
- **Paso anterior:** [Validar Calidad](./validar_calidad.md) — asegura que los datos son correctos antes del deploy
