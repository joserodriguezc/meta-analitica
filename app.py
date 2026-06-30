"""
App unificada MalayAI — punto de entrada multi-dominio.
Levanta con: uv run main.py deploy  (o streamlit run app.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from core_agent.skills.chart_builder import LOGO_PATH

st.set_page_config(
    page_title="MalayAI Analytics",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📊",
    layout="wide",
)

# ── Navegación ─────────────────────────────────────────────────────────────────

ventas      = st.Page("reports/ventas.py",      title="Ventas",       icon="📈")
inventario  = st.Page("reports/inventario.py",  title="Inventario",   icon="📦")
campanas    = st.Page("reports/campanas.py",     title="Campañas",     icon="📣")
devoluciones = st.Page("reports/devoluciones.py", title="Devoluciones", icon="↩️")

pg = st.navigation(
    {"Analítica": [ventas, inventario, campanas, devoluciones]},
    position="sidebar",
)

# ── Logo en sidebar (encima del menú) ─────────────────────────────────────────

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    st.caption("MalayAI Lab · Arnés Analítico")
    st.divider()

# Marca que el logo ya está renderizado para que sidebar_logo() no lo duplique
st.session_state["_logo_rendered"] = True

pg.run()