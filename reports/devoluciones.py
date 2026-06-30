"""
Reporte interactivo de devoluciones — Streamlit + Plotly.
KPIs y gráficos basados en memoria/metricas/devoluciones.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from core_agent.skills import duckdb_client as db
from core_agent.skills.chart_builder import (
    inject_css, sidebar_logo, page_header, barras, linea, pie, heatmap, kpi
)

st.set_page_config(
    page_title="Devoluciones · MalayAI",
    page_icon="↩️",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

inject_css()
sidebar_logo()
st.sidebar.title("Filtros")

motivos = db.query("SELECT DISTINCT motivo FROM devoluciones ORDER BY motivo").to_series().to_list()
sel_motivos = st.sidebar.multiselect("Motivo", motivos, default=motivos)

estados = db.query("SELECT DISTINCT estado FROM devoluciones ORDER BY estado").to_series().to_list()
sel_estados = st.sidebar.multiselect("Estado", estados, default=estados)

canales = db.query("SELECT DISTINCT canal_devolucion FROM devoluciones ORDER BY canal_devolucion").to_series().to_list()
sel_canales = st.sidebar.multiselect("Canal", canales, default=canales)

categorias = db.query("SELECT DISTINCT categoria FROM devoluciones ORDER BY categoria").to_series().to_list()
sel_cats = st.sidebar.multiselect("Categoría", categorias, default=categorias)

if not sel_motivos or not sel_estados or not sel_canales or not sel_cats:
    st.warning("Selecciona al menos un valor en cada filtro.")
    st.stop()

motivos_sql  = ", ".join(f"'{m}'" for m in sel_motivos)
estados_sql  = ", ".join(f"'{e}'" for e in sel_estados)
canales_sql  = ", ".join(f"'{c}'" for c in sel_canales)
cats_sql     = ", ".join(f"'{c}'" for c in sel_cats)

where = f"""
    motivo IN ({motivos_sql})
    AND estado IN ({estados_sql})
    AND canal_devolucion IN ({canales_sql})
    AND categoria IN ({cats_sql})
"""

# ── Título ────────────────────────────────────────────────────────────────────

page_header("Reporte de Devoluciones", "Cliente Demo S.A. · MalayAI Arnés Analítico")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

def _clp(v):
    return f"${v:,.0f}".replace(",", ".")

totales = db.query(f"""
    SELECT
        COUNT(*)                                                        AS total,
        COUNT(*) FILTER (WHERE estado = 'aprobada')                     AS aprobadas,
        COUNT(*) FILTER (WHERE estado = 'pendiente')                    AS pendientes,
        ROUND(COUNT(*) FILTER (WHERE estado = 'aprobada') * 100.0 / COUNT(*), 1) AS tasa_aprobacion,
        SUM(reembolso)                                                  AS reembolso_total,
        ROUND(AVG(reembolso) FILTER (WHERE estado = 'aprobada'), 0)    AS reembolso_promedio,
        SUM(cantidad_devuelta)                                          AS unidades
    FROM devoluciones WHERE {where}
""").to_dicts()[0]

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Total Solicitudes", str(int(totales["total"] or 0)))
with c2: kpi("Tasa Aprobación", f"{totales['tasa_aprobacion'] or 0:.1f}%")
with c3: kpi("Reembolso Total", _clp(totales["reembolso_total"] or 0))
with c4: kpi("Reembolso Promedio", _clp(totales["reembolso_promedio"] or 0))

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Aprobadas", str(int(totales["aprobadas"] or 0)))
with c2: kpi("Pendientes", str(int(totales["pendientes"] or 0)))
with c3: kpi("Unidades Devueltas", str(int(totales["unidades"] or 0)))
with c4: kpi("Rechazadas", str(int(totales["total"] or 0) - int(totales["aprobadas"] or 0) - int(totales["pendientes"] or 0)))

st.divider()

# ── Gráficos fila 1: Donut motivo + Donut estado ──────────────────────────────

df_motivo = db.query(f"""
    SELECT motivo AS Motivo, COUNT(*) AS Solicitudes
    FROM devoluciones WHERE {where}
    GROUP BY motivo ORDER BY Solicitudes DESC
""")

df_canal = db.query(f"""
    SELECT canal_devolucion AS Canal, COUNT(*) AS Solicitudes
    FROM devoluciones WHERE {where}
    GROUP BY canal_devolucion ORDER BY Solicitudes DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        pie(df_motivo, nombres="Motivo", valores="Solicitudes", titulo="Solicitudes por Motivo"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        pie(df_canal, nombres="Canal", valores="Solicitudes", titulo="Solicitudes por Canal de Devolución"),
        use_container_width=True,
    )

# ── Gráficos fila 2: Evolución mensual + Reembolso por categoría ──────────────

df_mensual = db.query(f"""
    SELECT
        mes,
        strftime(mes, '%b %Y')                                          AS Período,
        COUNT(*)                                                        AS Solicitudes,
        SUM(reembolso)                                                  AS Reembolso
    FROM devoluciones WHERE {where}
    GROUP BY mes, Período ORDER BY mes
""")

df_cat = db.query(f"""
    SELECT categoria AS Categoría, SUM(reembolso) AS Reembolso, COUNT(*) AS Solicitudes
    FROM devoluciones WHERE {where} AND estado = 'aprobada'
    GROUP BY categoria ORDER BY Reembolso DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        linea(df_mensual, x="Período", y="Solicitudes", titulo="Evolución Mensual de Solicitudes"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        barras(df_cat, x="Categoría", y="Reembolso", titulo="Reembolso Aprobado por Categoría"),
        use_container_width=True,
    )

# ── Heatmap categoría × motivo ────────────────────────────────────────────────

df_heat = db.query(f"""
    SELECT categoria AS Categoría, motivo AS Motivo, COUNT(*) AS Solicitudes
    FROM devoluciones WHERE {where}
    GROUP BY categoria, motivo
""")

st.plotly_chart(
    heatmap(df_heat, x="Motivo", y="Categoría", valores="Solicitudes",
            titulo="Solicitudes por Categoría y Motivo"),
    use_container_width=True,
)

# ── Tabla detalle ──────────────────────────────────────────────────────────────

with st.expander("Ver tabla de devoluciones"):
    df_all = db.query(f"""
        SELECT
            id_devolucion       AS ID,
            id_orden            AS Orden,
            fecha_devolucion    AS Fecha,
            nombre_producto     AS Producto,
            categoria           AS Categoría,
            cantidad_devuelta   AS Cantidad,
            motivo              AS Motivo,
            estado              AS Estado,
            canal_devolucion    AS Canal,
            reembolso           AS Reembolso
        FROM devoluciones WHERE {where}
        ORDER BY fecha_devolucion DESC
    """)
    st.dataframe(df_all.to_pandas(), use_container_width=True)