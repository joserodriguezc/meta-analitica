"""
App unificada MalayAI — punto de entrada multi-dominio.
Levanta con: uv run main.py deploy  (o streamlit run app.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from core_agent.skills.chart_builder import inject_css, _render_sidebar_brand

st.set_page_config(
    page_title="MalayAI Analytics",
    page_icon="📊",
    layout="wide",
)

inject_css()

# ── Páginas ────────────────────────────────────────────────────────────────────

ventas       = st.Page("reports/ventas.py",       title="Ventas",       icon="📈")
inventario   = st.Page("reports/inventario.py",   title="Inventario",   icon="📦")
campanas     = st.Page("reports/campanas.py",      title="Campañas",     icon="📣")
devoluciones = st.Page("reports/devoluciones.py", title="Devoluciones", icon="↩️")
envios       = st.Page("reports/envios.py",        title="Envíos",       icon="🚚")

# position="hidden" para controlar el orden del sidebar manualmente
pg = st.navigation(
    {"Analítica": [ventas, inventario, campanas, devoluciones, envios]},
    position="hidden",
)

# ── Sidebar: logo → nav → (filtros añadidos por cada reporte) ─────────────────

_render_sidebar_brand()

with st.sidebar:
    st.markdown(
        '<p style="color:#475569;font-size:0.65rem;font-weight:700;'
        'text-transform:uppercase;letter-spacing:0.8px;'
        'padding:0 0.5rem;margin-bottom:4px;">Analítica</p>',
        unsafe_allow_html=True,
    )
    st.page_link(ventas,       label="Ventas",       icon="📈")
    st.page_link(inventario,   label="Inventario",   icon="📦")
    st.page_link(campanas,     label="Campañas",     icon="📣")
    st.page_link(devoluciones, label="Devoluciones", icon="↩️")
    st.page_link(envios,       label="Envíos",       icon="🚚")
    st.divider()

st.session_state["_logo_rendered"] = True

pg.run()
