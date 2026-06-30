"""
Reporte interactivo de envíos — Streamlit + Plotly.
KPIs y gráficos basados en memoria/metricas/envios.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from core_agent.skills import duckdb_client as db
from core_agent.skills.chart_builder import (
    inject_css, sidebar_logo, page_header, barras, linea, pie, kpi
)

st.set_page_config(
    page_title="Envíos · MalayAI",
    page_icon="🚚",
    layout="wide",
)

# ── Sidebar ────────────────────────────────────────────────────────────────────

inject_css()
sidebar_logo()
st.sidebar.title("Filtros")

couriers = db.query("SELECT DISTINCT courier FROM envios ORDER BY courier").to_series().to_list()
sel_couriers = st.sidebar.multiselect("Courier", couriers, default=couriers)

tipos = db.query("SELECT DISTINCT tipo_envio FROM envios ORDER BY tipo_envio").to_series().to_list()
sel_tipos = st.sidebar.multiselect("Tipo de envío", tipos, default=tipos)

estados = db.query("SELECT DISTINCT estado FROM envios ORDER BY estado").to_series().to_list()
sel_estados = st.sidebar.multiselect("Estado", estados, default=estados)

regiones = db.query("SELECT DISTINCT region_destino FROM envios ORDER BY region_destino").to_series().to_list()
sel_regiones = st.sidebar.multiselect("Región destino", regiones, default=regiones)

if not sel_couriers or not sel_tipos or not sel_estados or not sel_regiones:
    st.warning("Selecciona al menos un valor en cada filtro.")
    st.stop()

def _sql_in(values: list[str]) -> str:
    return ", ".join(f"'{v.replace(chr(39), chr(39)*2)}'" for v in values)

couriers_sql = _sql_in(sel_couriers)
tipos_sql    = _sql_in(sel_tipos)
estados_sql  = _sql_in(sel_estados)
regiones_sql = _sql_in(sel_regiones)

where = f"""
    courier IN ({couriers_sql})
    AND tipo_envio IN ({tipos_sql})
    AND estado IN ({estados_sql})
    AND region_destino IN ({regiones_sql})
"""

# ── Título ────────────────────────────────────────────────────────────────────

page_header("Reporte de Envíos", "Cliente Demo S.A. · MalayAI Arnés Analítico")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────

def _clp(v):
    return f"${v:,.0f}".replace(",", ".")

totales = db.query(f"""
    SELECT
        COUNT(*)                                                                AS total,
        COUNT(*) FILTER (WHERE estado = 'entregado')                            AS entregados,
        COUNT(*) FILTER (WHERE estado = 'retrasado')                            AS retrasados,
        COUNT(*) FILTER (WHERE estado = 'en_transito')                          AS en_transito,
        ROUND(
            COUNT(*) FILTER (WHERE estado = 'entregado') * 100.0 /
            NULLIF(COUNT(*) FILTER (WHERE estado != 'en_transito'), 0), 1
        )                                                                       AS tasa_entrega,
        SUM(costo_envio)                                                        AS costo_total,
        ROUND(AVG(costo_envio), 0)                                              AS costo_promedio,
        ROUND(AVG(dias_retraso) FILTER (WHERE estado = 'retrasado'), 1)        AS dias_retraso_prom
    FROM envios WHERE {where}
""").to_dicts()[0]

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Total Envíos",            str(int(totales["total"] or 0)),            icon="📦")
with c2: kpi("Entrega a Tiempo",        f"{totales['tasa_entrega'] or 0:.1f}%",     icon="✅")
with c3: kpi("Costo Total Envíos",      _clp(totales["costo_total"] or 0),          icon="💰")
with c4: kpi("Costo Promedio",          _clp(totales["costo_promedio"] or 0),       icon="📊")

c1, c2, c3, c4 = st.columns(4)
with c1: kpi("Entregados",              str(int(totales["entregados"] or 0)),        icon="🟢")
with c2: kpi("Retrasados",              str(int(totales["retrasados"] or 0)),        icon="🔴")
with c3: kpi("En Tránsito",             str(int(totales["en_transito"] or 0)),       icon="🔄")
with c4: kpi("Días Retraso Promedio",   f"{totales['dias_retraso_prom'] or 0:.1f} días", icon="⏱️")

st.divider()

# ── Gráficos fila 1: Donut estado + Donut courier ─────────────────────────────

df_estado = db.query(f"""
    SELECT estado AS Estado, COUNT(*) AS Envíos
    FROM envios WHERE {where}
    GROUP BY estado ORDER BY Envíos DESC
""")

df_courier = db.query(f"""
    SELECT courier AS Courier, COUNT(*) AS Envíos
    FROM envios WHERE {where}
    GROUP BY courier ORDER BY Envíos DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        pie(df_estado, nombres="Estado", valores="Envíos", titulo="Distribución por Estado"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        pie(df_courier, nombres="Courier", valores="Envíos", titulo="Envíos por Courier"),
        use_container_width=True,
    )

# ── Gráficos fila 2: Costo por tipo + Envíos por región ───────────────────────

df_tipo = db.query(f"""
    SELECT
        tipo_envio AS "Tipo de Envío",
        ROUND(AVG(costo_envio), 0) AS "Costo Promedio",
        COUNT(*) AS Envíos
    FROM envios WHERE {where}
    GROUP BY tipo_envio ORDER BY "Costo Promedio" DESC
""")

df_region = db.query(f"""
    SELECT region_destino AS Región, COUNT(*) AS Envíos
    FROM envios WHERE {where}
    GROUP BY region_destino ORDER BY Envíos DESC
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        barras(df_tipo, x="Tipo de Envío", y="Costo Promedio",
               titulo="Costo Promedio por Tipo de Envío"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        barras(df_region, x="Región", y="Envíos",
               titulo="Envíos por Región de Destino"),
        use_container_width=True,
    )

# ── Gráfico fila 3: Evolución mensual ─────────────────────────────────────────

df_mensual = db.query(f"""
    SELECT
        mes,
        strftime(mes, '%b %Y')                          AS Período,
        COUNT(*)                                        AS Envíos,
        COUNT(*) FILTER (WHERE estado = 'retrasado')    AS Retrasados,
        SUM(costo_envio)                                AS "Costo Total"
    FROM envios WHERE {where}
    GROUP BY mes, Período ORDER BY mes
""")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(
        linea(df_mensual, x="Período", y="Envíos",
              titulo="Evolución Mensual de Envíos"),
        use_container_width=True,
    )
with col2:
    st.plotly_chart(
        barras(df_mensual, x="Período", y="Costo Total",
               titulo="Costo Total de Envíos por Mes"),
        use_container_width=True,
    )

# ── Tabla detalle ──────────────────────────────────────────────────────────────

with st.expander("Ver tabla de envíos"):
    df_all = db.query(f"""
        SELECT
            id_envio                AS ID,
            id_orden                AS Orden,
            fecha_despacho          AS Despacho,
            fecha_entrega_estimada  AS "Entrega Estimada",
            fecha_entrega_real      AS "Entrega Real",
            courier                 AS Courier,
            tipo_envio              AS Tipo,
            region_destino          AS Región,
            estado                  AS Estado,
            dias_retraso            AS "Días Retraso",
            costo_envio             AS Costo,
            peso_kg                 AS "Peso (kg)"
        FROM envios WHERE {where}
        ORDER BY fecha_despacho DESC
    """)
    st.dataframe(df_all.to_pandas(), use_container_width=True)
