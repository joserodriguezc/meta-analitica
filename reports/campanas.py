"""
Reporte interactivo de campañas — Streamlit + Plotly.
KPIs y gráficos basados en memoria/metricas/campanas.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.chart_builder import (
    sidebar_logo, barras, scatter, pie, kpi
)

st.set_page_config(
    page_title="Campañas · MalayAI",
    page_icon="📣",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

sidebar_logo()
st.sidebar.title("Filtros")

canales = db.query("SELECT DISTINCT canal FROM campanas ORDER BY canal").to_series().to_list()
sel_canales = st.sidebar.multiselect("Canal", canales, default=canales)

estados = db.query("SELECT DISTINCT estado FROM campanas ORDER BY estado").to_series().to_list()
sel_estados = st.sidebar.multiselect("Estado", estados, default=estados)

if not sel_canales or not sel_estados:
    st.warning("Selecciona al menos un valor en cada filtro.")
    st.stop()

canales_sql = ", ".join(f"'{c}'" for c in sel_canales)
estados_sql = ", ".join(f"'{e}'" for e in sel_estados)
where = f"canal IN ({canales_sql}) AND estado IN ({estados_sql})"

# ── Título ────────────────────────────────────────────────────────────────────

st.title("Reporte de Campañas")
st.caption("Cliente Demo S.A. · MalayAI Arnés Analítico")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

def _clp(v):
    return f"${v:,.0f}".replace(",", ".")

totales = db.query(f"""
    SELECT
        COUNT(*)                            AS campanas,
        SUM(presupuesto)                    AS presupuesto_total,
        SUM(gasto_real)                     AS gasto_total,
        SUM(conversiones)                   AS conversiones,
        SUM(ingresos_atribuidos)            AS ingresos,
        ROUND(AVG(CASE WHEN roas IS NOT NULL THEN roas END), 2) AS roas_promedio,
        ROUND(AVG(CASE WHEN roi  IS NOT NULL THEN roi  END), 1) AS roi_promedio,
        ROUND(AVG(CASE WHEN ctr  IS NOT NULL THEN ctr  END), 2) AS ctr_promedio
    FROM campanas WHERE {where}
""").to_dicts()[0]

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Inversión Total", _clp(totales["gasto_total"] or 0))
with c2: kpi("Ingresos Atribuidos", _clp(totales["ingresos"] or 0))
with c3: kpi("ROAS Promedio", f"{totales['roas_promedio'] or 0:.2f}x")
with c4: kpi("Conversiones", str(int(totales["conversiones"] or 0)))

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("ROI Promedio", f"{totales['roi_promedio'] or 0:.1f}%")
with c2: kpi("CTR Promedio", f"{totales['ctr_promedio'] or 0:.2f}%")
with c3: kpi("Campañas", str(int(totales["campanas"] or 0)))
with c4: kpi("Presupuesto Total", _clp(totales["presupuesto_total"] or 0))

st.divider()

# ── Gráficos fila 1: ROAS por canal + Scatter inversión vs ROAS ───────────────

df_canal = db.query(f"""
    SELECT
        canal AS Canal,
        ROUND(AVG(roas), 2)             AS ROAS,
        SUM(gasto_real)                 AS Inversión,
        SUM(conversiones)               AS Conversiones
    FROM campanas WHERE {where} AND roas IS NOT NULL
    GROUP BY canal ORDER BY ROAS DESC
""")

df_scatter = db.query(f"""
    SELECT
        nombre_campana  AS Campaña,
        canal           AS Canal,
        gasto_real      AS Inversión,
        roas            AS ROAS,
        conversiones    AS Conversiones
    FROM campanas WHERE {where} AND roas IS NOT NULL
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        barras(df_canal, x="Canal", y="ROAS", titulo="ROAS Promedio por Canal"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        scatter(
            df_scatter, x="Inversión", y="ROAS",
            titulo="Inversión vs ROAS por Campaña",
            size="Conversiones", color="Canal",
            hover=["Campaña", "Conversiones"],
        ),
        use_container_width=True,
    )

# ── Gráficos fila 2: ROI por campaña + Donut por canal ────────────────────────

df_roi = db.query(f"""
    SELECT nombre_campana AS Campaña, ROUND(roi, 1) AS ROI
    FROM campanas WHERE {where} AND roi IS NOT NULL
    ORDER BY ROI DESC
""")

df_pie_canal = db.query(f"""
    SELECT canal AS Canal, SUM(ingresos_atribuidos) AS Ingresos
    FROM campanas WHERE {where}
    GROUP BY canal ORDER BY Ingresos DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        barras(df_roi, x="Campaña", y="ROI", titulo="ROI % por Campaña"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        pie(df_pie_canal, nombres="Canal", valores="Ingresos", titulo="Ingresos Atribuidos por Canal"),
        use_container_width=True,
    )

# ── Tabla completa ─────────────────────────────────────────────────────────────

with st.expander("Ver tabla completa de campañas"):
    df_all = db.query(f"""
        SELECT
            id_campana      AS ID,
            nombre_campana  AS Campaña,
            canal           AS Canal,
            estado          AS Estado,
            presupuesto     AS Presupuesto,
            gasto_real      AS Gasto,
            ROUND(ejecucion_presupuesto, 1) AS "Ejec %",
            conversiones    AS Conv,
            ROUND(roas, 2)  AS ROAS,
            ROUND(roi, 1)   AS "ROI %",
            ROUND(ctr, 2)   AS "CTR %"
        FROM campanas WHERE {where}
        ORDER BY ROAS DESC NULLS LAST
    """)
    st.dataframe(df_all.to_pandas(), use_container_width=True)