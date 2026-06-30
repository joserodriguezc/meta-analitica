"""
Reporte interactivo de ventas — Streamlit + Plotly.
KPIs y gráficos basados en memoria/metricas/ventas.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.chart_builder import (
    inject_css, sidebar_logo, page_header, barras, linea, pie, kpi
)

st.set_page_config(
    page_title="Ventas · MalayAI",
    page_icon="📈",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

inject_css()
sidebar_logo()
st.sidebar.title("Filtros")

meses = db.query("SELECT DISTINCT mes FROM ventas ORDER BY mes").to_series().to_list()
mes_labels = [m.strftime("%B %Y").capitalize() for m in meses]
sel_meses = st.sidebar.multiselect("Meses", mes_labels, default=mes_labels)
meses_sel = [m for m, l in zip(meses, mes_labels) if l in sel_meses]

categorias = db.query("SELECT DISTINCT categoria FROM ventas ORDER BY categoria").to_series().to_list()
sel_cats = st.sidebar.multiselect("Categorías", categorias, default=categorias)

canales = db.query("SELECT DISTINCT COALESCE(canal, 'sin canal') AS canal FROM ventas ORDER BY canal").to_series().to_list()
sel_canales = st.sidebar.multiselect("Canales", canales, default=canales)

# ── Filtro base ────────────────────────────────────────────────────────────────

if not meses_sel or not sel_cats or not sel_canales:
    st.warning("Selecciona al menos un valor en cada filtro.")
    st.stop()

meses_sql = ", ".join(f"'{m}'" for m in meses_sel)
cats_sql   = ", ".join(f"'{c}'" for c in sel_cats)
canales_sql = ", ".join(f"'{c}'" for c in sel_canales)

where = f"""
    estado = 'completado'
    AND mes IN ({meses_sql})
    AND categoria IN ({cats_sql})
    AND COALESCE(canal, 'sin canal') IN ({canales_sql})
"""

# ── Título ────────────────────────────────────────────────────────────────────

page_header("Reporte de Ventas", "Cliente Demo S.A. · MalayAI Arnés Analítico")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

total = db.query(f"""
    SELECT
        SUM(ingreso_linea)                                      AS ingresos,
        COUNT(DISTINCT id_orden)                                AS ordenes,
        ROUND(SUM(ingreso_linea) / COUNT(DISTINCT id_orden), 0) AS ticket,
        SUM(cantidad)                                           AS unidades
    FROM ventas WHERE {where}
""").to_dicts()[0]

mensual = db.query(f"""
    SELECT mes,
        SUM(ingreso_linea)                                      AS ingresos,
        COUNT(DISTINCT id_orden)                                AS ordenes,
        ROUND(SUM(ingreso_linea) / COUNT(DISTINCT id_orden), 0) AS ticket
    FROM ventas WHERE {where}
    GROUP BY mes ORDER BY mes
""").to_dicts()

ult = mensual[-1] if mensual else {}
ant = mensual[-2] if len(mensual) >= 2 else None

def _delta(actual, anterior):
    if not anterior or anterior == 0:
        return None
    pct = (actual - anterior) / anterior * 100
    return f"{pct:+.1f}%"

def _clp(v):
    return f"${v:,.0f}".replace(",", ".")

st.subheader("Total Acumulado")
c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Ingresos Totales", _clp(total["ingresos"] or 0))
with c2: kpi("Ticket Promedio", _clp(total["ticket"] or 0))
with c3: kpi("Órdenes", str(int(total["ordenes"] or 0)))
with c4: kpi("Unidades Vendidas", str(int(total["unidades"] or 0)))

if ult:
    mes_label = ult["mes"].strftime("%B %Y").capitalize()
    st.subheader(f"Último Período — {mes_label}")
    c1, c2, c3 = st.columns(3)
    with c1: kpi("Ingresos del Mes", _clp(ult["ingresos"]), _delta(ult["ingresos"], ant["ingresos"] if ant else None))
    with c2: kpi("Ticket Promedio", _clp(ult["ticket"]), _delta(ult["ticket"], ant["ticket"] if ant else None))
    with c3: kpi("Órdenes del Mes", str(int(ult["ordenes"])), _delta(ult["ordenes"], ant["ordenes"] if ant else None))

st.divider()

# ── Gráficos fila 1: Evolución mensual ────────────────────────────────────────

df_mensual = db.query(f"""
    SELECT
        mes,
        strftime(mes, '%b %Y')                                  AS periodo,
        SUM(ingreso_linea)                                      AS Ingresos,
        COUNT(DISTINCT id_orden)                                AS Ordenes
    FROM ventas WHERE {where}
    GROUP BY mes, periodo ORDER BY mes
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        barras(df_mensual, x="periodo", y="Ingresos", titulo="Ingresos por Mes"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        linea(df_mensual, x="periodo", y="Ordenes", titulo="Evolución de Órdenes"),
        use_container_width=True,
    )

# ── Gráficos fila 2: Categoría y Canal ────────────────────────────────────────

df_cat = db.query(f"""
    SELECT categoria AS Categoría, SUM(ingreso_linea) AS Ingresos
    FROM ventas WHERE {where}
    GROUP BY categoria ORDER BY Ingresos DESC
""")

df_canal = db.query(f"""
    SELECT COALESCE(canal, 'sin canal') AS Canal, SUM(ingreso_linea) AS Ingresos
    FROM ventas WHERE {where}
    GROUP BY canal ORDER BY Ingresos DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        pie(df_cat, nombres="Categoría", valores="Ingresos", titulo="Ingresos por Categoría"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        pie(df_canal, nombres="Canal", valores="Ingresos", titulo="Ingresos por Canal"),
        use_container_width=True,
    )

# ── Gráfico fila 3: Top productos ─────────────────────────────────────────────

df_top = db.query(f"""
    SELECT
        nombre_producto AS Producto,
        SUM(cantidad)      AS Unidades,
        SUM(ingreso_linea) AS Ingresos
    FROM ventas WHERE {where}
    GROUP BY nombre_producto
    ORDER BY Ingresos DESC LIMIT 10
""")

st.plotly_chart(
    barras(df_top, x="Producto", y="Ingresos", titulo="Top 10 Productos por Ingresos"),
    use_container_width=True,
)

# ── Tabla detalle ─────────────────────────────────────────────────────────────

with st.expander("Ver tabla de evolución mensual"):
    st.dataframe(
        df_mensual.select(["periodo", "Ingresos", "Ordenes"]).to_pandas(),
        use_container_width=True,
    )