"""
Reporte interactivo de inventario — Streamlit + Plotly.
KPIs y gráficos basados en memoria/metricas/inventario.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.chart_builder import (
    inject_css, sidebar_logo, page_header, barras, treemap, pie, kpi
)

st.set_page_config(
    page_title="Inventario · MalayAI",
    page_icon="📦",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

inject_css()
sidebar_logo()
st.sidebar.title("Filtros")

categorias = db.query("SELECT DISTINCT categoria FROM inventario ORDER BY categoria").to_series().to_list()
sel_cats = st.sidebar.multiselect("Categorías", categorias, default=categorias)

bodegas = db.query("SELECT DISTINCT bodega FROM inventario ORDER BY bodega").to_series().to_list()
sel_bodegas = st.sidebar.multiselect("Bodegas", bodegas, default=bodegas)

estados = db.query("SELECT DISTINCT estado FROM inventario ORDER BY estado").to_series().to_list()
sel_estados = st.sidebar.multiselect("Estado", estados, default=estados)

mostrar_quiebre = st.sidebar.toggle("Solo productos en riesgo", value=False)

if not sel_cats or not sel_bodegas or not sel_estados:
    st.warning("Selecciona al menos un valor en cada filtro.")
    st.stop()

cats_sql    = ", ".join(f"'{c}'" for c in sel_cats)
bodegas_sql = ", ".join(f"'{b}'" for b in sel_bodegas)
estados_sql = ", ".join(f"'{e}'" for e in sel_estados)

where = f"categoria IN ({cats_sql}) AND bodega IN ({bodegas_sql}) AND estado IN ({estados_sql})"
if mostrar_quiebre:
    where += " AND bajo_minimo = true"

# ── Título ────────────────────────────────────────────────────────────────────

page_header("Reporte de Inventario", "Cliente Demo S.A. · MalayAI Arnés Analítico")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

def _clp(v):
    return f"${v:,.0f}".replace(",", ".")

totales = db.query(f"""
    SELECT
        SUM(valor_stock)                           AS valor_inventario,
        COUNT(*)                                   AS total_productos,
        SUM(CASE WHEN bajo_minimo THEN 1 END)      AS en_riesgo,
        ROUND(AVG(margen_bruto), 1)                AS margen_promedio,
        SUM(CASE WHEN estado='agotado' THEN 1 END) AS agotados
    FROM inventario WHERE {where}
""").to_dicts()[0]

c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi("Valor Inventario", _clp(totales["valor_inventario"] or 0))
with c2: kpi("Total Productos", str(int(totales["total_productos"] or 0)))
with c3: kpi("En Riesgo", str(int(totales["en_riesgo"] or 0)))
with c4: kpi("Margen Promedio", f"{totales['margen_promedio'] or 0:.1f}%")
with c5: kpi("Agotados", str(int(totales["agotados"] or 0)))

st.divider()

# ── Gráficos fila 1: Treemap + Margen por categoría ───────────────────────────

df_cat = db.query(f"""
    SELECT categoria AS Categoría, SUM(valor_stock) AS Valor, COUNT(*) AS Productos
    FROM inventario WHERE {where}
    GROUP BY categoria ORDER BY Valor DESC
""")

df_margen = db.query(f"""
    SELECT categoria AS Categoría, ROUND(AVG(margen_bruto), 1) AS Margen
    FROM inventario WHERE {where}
    GROUP BY categoria ORDER BY Margen DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        treemap(df_cat, path=["Categoría"], valores="Valor", titulo="Valor de Inventario por Categoría"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        barras(df_margen, x="Categoría", y="Margen", titulo="Margen Bruto Promedio % por Categoría"),
        use_container_width=True,
    )

# ── Gráficos fila 2: Distribución por estado + Cobertura ─────────────────────

df_estado = db.query(f"""
    SELECT estado AS Estado, COUNT(*) AS Productos
    FROM inventario WHERE {where}
    GROUP BY estado
""")

df_cob = db.query(f"""
    SELECT nombre_producto AS Producto, ROUND(cobertura, 2) AS Cobertura
    FROM inventario WHERE {where} AND estado != 'descontinuado'
    ORDER BY cobertura ASC LIMIT 10
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        pie(df_estado, nombres="Estado", valores="Productos", titulo="Distribución por Estado"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        barras(df_cob, x="Producto", y="Cobertura", titulo="Cobertura de Stock (menor = más urgente)"),
        use_container_width=True,
    )

# ── Tabla de alertas ──────────────────────────────────────────────────────────

st.subheader("Productos bajo Stock Mínimo")
df_quiebre = db.query(f"""
    SELECT
        id_producto         AS SKU,
        nombre_producto     AS Producto,
        categoria           AS Categoría,
        bodega              AS Bodega,
        stock_actual        AS Stock,
        stock_minimo        AS Mínimo,
        ROUND(cobertura, 2) AS Cobertura
    FROM inventario
    WHERE bajo_minimo = true AND {where}
    ORDER BY cobertura ASC
""")

if df_quiebre.is_empty():
    st.success("Sin alertas de quiebre para los filtros seleccionados.")
else:
    st.dataframe(df_quiebre.to_pandas(), use_container_width=True)

# ── Tabla completa ─────────────────────────────────────────────────────────────

with st.expander("Ver todos los productos"):
    df_all = db.query(f"""
        SELECT id_producto AS SKU, nombre_producto AS Producto,
               categoria AS Categoría, bodega AS Bodega,
               stock_actual AS Stock, stock_minimo AS Mínimo,
               estado AS Estado,
               ROUND(margen_bruto, 1) AS "Margen %",
               ROUND(cobertura, 2)    AS Cobertura
        FROM inventario WHERE {where}
        ORDER BY categoria, nombre_producto
    """)
    st.dataframe(df_all.to_pandas(), use_container_width=True)