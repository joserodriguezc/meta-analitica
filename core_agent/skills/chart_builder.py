"""
Helpers de Plotly + CSS premium para reportes Streamlit.
Paleta y estilo basados en la identidad visual MalayAI Lab.
"""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st
from pathlib import Path

LOGO_PATH = Path("assets/malayai_logo.png")

# ── Paleta de marca ────────────────────────────────────────────────────────────
AZUL     = "#3B82F6"   # azul "AI" del logo
CYAN     = "#00D4FF"   # cyan del trazo derecho del logo
PALETA   = [AZUL, CYAN, "#8B5CF6", "#F59E0B", "#10B981", "#EF4444", "#EC4899"]
FONDO    = "#050810"
PANEL    = "#0D1525"
BORDE    = "rgba(59,130,246,0.2)"
TEXTO    = "#E2E8F0"
MUTED    = "#64748B"

# ── CSS ────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
/* Fuente sistema */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif !important;
}

/* Sidebar oscuro con borde azul */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #030610 0%, #07101E 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.15) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #94A3B8 !important;
}

/* Área principal */
.main .block-container {
    padding-top: 1.2rem !important;
    max-width: 1400px !important;
}

/* KPI cards — glow effect */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0D1525 0%, #111B2E 100%) !important;
    border: 1px solid rgba(59,130,246,0.25) !important;
    border-radius: 12px !important;
    padding: 1.1rem 1rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5),
                inset 0 1px 0 rgba(255,255,255,0.04) !important;
    transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s !important;
}
[data-testid="metric-container"]:hover {
    border-color: rgba(0,212,255,0.45) !important;
    box-shadow: 0 4px 32px rgba(0,212,255,0.14),
                inset 0 1px 0 rgba(255,255,255,0.06) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: #F0F9FF !important;
    letter-spacing: -0.3px !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] > div {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* Divider como línea con gradiente */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.35), rgba(0,212,255,0.2), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* Tablas */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(59,130,246,0.15) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Expander */
details {
    border: 1px solid rgba(59,130,246,0.15) !important;
    border-radius: 10px !important;
    background: #080E1A !important;
    padding: 0.25rem 0.5rem !important;
}

/* Multiselect */
[data-baseweb="select"] > div:first-child {
    border-color: rgba(59,130,246,0.3) !important;
    border-radius: 8px !important;
    background: #0A1020 !important;
}

/* Toggle */
[data-testid="stToggle"] label { color: #94A3B8 !important; }

/* Botones y pills de multiselect */
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.2) !important;
    border: 1px solid rgba(59,130,246,0.4) !important;
    border-radius: 6px !important;
}

/* Sidebar título */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #E2E8F0 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

/* Navigation links */
[data-testid="stSidebarNavItems"] a {
    border-radius: 8px !important;
    transition: background 0.15s !important;
}
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(59,130,246,0.1) !important;
}

/* Alert boxes */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
</style>
"""


def inject_css() -> None:
    """Inyecta el CSS premium. Llama una sola vez por sesión."""
    if st.session_state.get("_css_injected"):
        return
    st.markdown(_CSS, unsafe_allow_html=True)
    st.session_state["_css_injected"] = True


def sidebar_logo() -> None:
    """Logo en sidebar. No duplica si ya está renderizado por app.py."""
    if st.session_state.get("_logo_rendered"):
        return
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    st.sidebar.markdown("---")


def page_header(titulo: str, subtitulo: str = "") -> None:
    """Banner de cabecera premium con gradiente de marca."""
    sub_html = f'<p style="margin:6px 0 0;color:{MUTED};font-size:0.82rem;">{subtitulo}</p>' if subtitulo else ""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {PANEL} 0%, #111B2E 60%, #0A1628 100%);
        border: 1px solid {BORDE};
        border-radius: 14px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position:absolute; top:0; right:0; width:220px; height:100%;
            background: radial-gradient(ellipse at right center,
                rgba(0,212,255,0.09) 0%, transparent 65%);
            pointer-events:none;
        "></div>
        <div style="
            position:absolute; top:-30px; left:-30px; width:120px; height:120px;
            background: radial-gradient(circle,
                rgba(59,130,246,0.07) 0%, transparent 70%);
            pointer-events:none;
        "></div>
        <h1 style="
            margin:0; padding:0;
            background: linear-gradient(90deg, {AZUL} 0%, {CYAN} 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            background-clip:text;
            font-size:1.75rem; font-weight:700; letter-spacing:-0.4px;
        ">{titulo}</h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ── Plotly base ────────────────────────────────────────────────────────────────

def _base_layout(fig: go.Figure, titulo: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=14, color=TEXTO), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(color=TEXTO, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", size=12),
        margin=dict(l=16, r=16, t=40, b=16),
        legend=dict(
            bgcolor="rgba(13,21,37,0.8)",
            bordercolor=BORDE,
            borderwidth=1,
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor="#111B2E",
            bordercolor=BORDE,
            font=dict(color=TEXTO, size=12),
        ),
        colorway=PALETA,
    )
    fig.update_xaxes(
        gridcolor="rgba(30,45,70,0.7)",
        linecolor="rgba(30,45,70,0.9)",
        tickcolor=MUTED,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        gridcolor="rgba(30,45,70,0.7)",
        linecolor="rgba(30,45,70,0.9)",
        tickcolor=MUTED,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED),
    )
    return fig


# ── Tipos de gráficos ──────────────────────────────────────────────────────────

def barras(df: pl.DataFrame, x: str, y: str, titulo: str = "",
           color: str | None = None, texto: str | None = None) -> go.Figure:
    fig = px.bar(
        df.to_pandas(), x=x, y=y,
        color=color, text=texto,
        color_discrete_sequence=PALETA,
    )
    fig.update_traces(
        textposition="outside",
        marker_line_width=0,
        opacity=0.9,
    )
    return _base_layout(fig, titulo)


def linea(df: pl.DataFrame, x: str, y: str | list[str], titulo: str = "") -> go.Figure:
    fig = px.line(
        df.to_pandas(), x=x, y=y,
        color_discrete_sequence=PALETA,
        markers=True,
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    return _base_layout(fig, titulo)


def pie(df: pl.DataFrame, nombres: str, valores: str, titulo: str = "") -> go.Figure:
    fig = px.pie(
        df.to_pandas(), names=nombres, values=valores,
        color_discrete_sequence=PALETA,
        hole=0.45,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont_size=11,
        marker=dict(line=dict(color=FONDO, width=2)),
        pull=[0.03] * 10,
    )
    return _base_layout(fig, titulo)


def scatter(df: pl.DataFrame, x: str, y: str, titulo: str = "",
            size: str | None = None, color: str | None = None,
            hover: list[str] | None = None) -> go.Figure:
    fig = px.scatter(
        df.to_pandas(), x=x, y=y,
        size=size, color=color, hover_data=hover,
        color_discrete_sequence=PALETA,
    )
    fig.update_traces(marker=dict(line=dict(color=FONDO, width=1)))
    return _base_layout(fig, titulo)


def treemap(df: pl.DataFrame, path: list[str], valores: str, titulo: str = "") -> go.Figure:
    fig = px.treemap(
        df.to_pandas(), path=path, values=valores,
        color_discrete_sequence=PALETA,
    )
    fig.update_traces(
        marker=dict(line=dict(color=FONDO, width=2)),
        textfont=dict(color=TEXTO),
    )
    return _base_layout(fig, titulo)


def heatmap(df: pl.DataFrame, x: str, y: str, valores: str, titulo: str = "") -> go.Figure:
    pivot = df.to_pandas().pivot(index=y, columns=x, values=valores).fillna(0)
    fig = px.imshow(
        pivot,
        color_continuous_scale=[[0, "#0D1525"], [0.5, "#1E3A6E"], [1, CYAN]],
        aspect="auto",
        text_auto=True,
    )
    fig.update_traces(textfont=dict(color=TEXTO, size=11))
    return _base_layout(fig, titulo)


def kpi(label: str, valor: str, delta: str = "") -> None:
    st.metric(label=label, value=valor, delta=delta if delta else None)
