"""
App unificada MalayAI — punto de entrada multi-dominio.
Levanta con: uv run main.py deploy  (o streamlit run app.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from core_agent.skills.chart_builder import LOGO_PATH, inject_css

st.set_page_config(
    page_title="MalayAI Analytics",
    page_icon="📊",
    layout="wide",
)

inject_css()

# ── Logo y branding en sidebar ─────────────────────────────────────────────────

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    st.markdown(
        '<p style="text-align:center;color:#64748B;font-size:0.72rem;'
        'letter-spacing:0.5px;text-transform:uppercase;margin-top:4px;">'
        "Arnés Analítico</p>",
        unsafe_allow_html=True,
    )
    st.divider()

# Marca logo y CSS como ya renderizados para que los reportes no los dupliquen
st.session_state["_logo_rendered"] = True

# ── Navegación ─────────────────────────────────────────────────────────────────

ventas       = st.Page("reports/ventas.py",       title="Ventas",        icon="📈")
inventario   = st.Page("reports/inventario.py",   title="Inventario",    icon="📦")
campanas     = st.Page("reports/campanas.py",      title="Campañas",      icon="📣")
devoluciones = st.Page("reports/devoluciones.py", title="Devoluciones",  icon="↩️")

pg = st.navigation(
    {"Analítica": [ventas, inventario, campanas, devoluciones]},
    position="sidebar",
)

pg.run()
