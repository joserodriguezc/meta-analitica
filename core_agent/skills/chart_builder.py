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
AZUL   = "#3B82F6"
CYAN   = "#00D4FF"
PALETA = [AZUL, CYAN, "#8B5CF6", "#F59E0B", "#10B981", "#EF4444", "#EC4899"]
FONDO  = "#050810"
PANEL  = "#0D1525"
BORDE  = "rgba(59,130,246,0.2)"
TEXTO  = "#E2E8F0"
MUTED  = "#64748B"

# ── CSS ────────────────────────────────────────────────────────────────────────
_CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif !important;
}

/* ── Sidebar ─────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #030610 0%, #050D1A 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.12) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #94A3B8 !important; }

/* Nav items — estilo referencia con borde activo izquierdo */
[data-testid="stSidebarNavItems"] {
    padding: 0 0.5rem !important;
}
[data-testid="stSidebarNavItems"] a {
    border-radius: 8px !important;
    padding: 0.55rem 0.85rem !important;
    margin-bottom: 2px !important;
    border-left: 3px solid transparent !important;
    color: #94A3B8 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.6rem !important;
}
[data-testid="stSidebarNavItems"] a:hover {
    background: rgba(59,130,246,0.08) !important;
    border-left-color: #3B82F6 !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebarNavItems"] [aria-current="page"],
[data-testid="stSidebarNavItems"] a[aria-selected="true"] {
    background: rgba(59,130,246,0.12) !important;
    border-left-color: #3B82F6 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* ── Área principal ──────────────────── */
.main .block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1440px !important;
}

/* ── Divider gradiente ───────────────── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.3), rgba(0,212,255,0.15), transparent) !important;
    margin: 1.25rem 0 !important;
}

/* ── Tablas ──────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(59,130,246,0.12) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Expander ────────────────────────── */
details {
    border: 1px solid rgba(59,130,246,0.12) !important;
    border-radius: 10px !important;
    background: #080E1A !important;
    padding: 0.25rem 0.5rem !important;
}

/* ── Multiselect ─────────────────────── */
[data-baseweb="select"] > div:first-child {
    border-color: rgba(59,130,246,0.25) !important;
    border-radius: 8px !important;
    background: #0A1020 !important;
    font-size: 0.85rem !important;
}
[data-baseweb="tag"] {
    background: rgba(59,130,246,0.18) !important;
    border: 1px solid rgba(59,130,246,0.35) !important;
    border-radius: 6px !important;
}

/* ── Alert / Success ─────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Ocultar métricas nativas (usamos cards HTML) ── */
[data-testid="metric-container"] {
    display: none !important;
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
    """Logo pequeño + nombre de app en el sidebar. No duplica si ya existe."""
    if st.session_state.get("_logo_rendered"):
        return
    _render_sidebar_brand()


def _render_sidebar_brand() -> None:
    if LOGO_PATH.exists():
        # Logo centrado a tamaño fijo
        import base64
        img_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        st.sidebar.markdown(
            f"""
            <div style="display:flex;flex-direction:column;align-items:center;
                        padding:1rem 0 0.25rem;">
                <img src="data:image/png;base64,{img_b64}"
                     width="72" style="border-radius:10px;" />
                <span style="color:#E2E8F0;font-size:0.78rem;font-weight:600;
                             letter-spacing:0.3px;margin-top:8px;">MalayAI Lab</span>
                <span style="color:#475569;font-size:0.65rem;
                             letter-spacing:0.5px;">Arnés Analítico</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(
        '<div style="height:1px;background:linear-gradient(90deg,transparent,'
        'rgba(59,130,246,0.3),transparent);margin:0.6rem 0.5rem 0.8rem;"></div>',
        unsafe_allow_html=True,
    )


def page_header(titulo: str, subtitulo: str = "") -> None:
    """Banner de cabecera premium con gradiente de marca."""
    sub_html = (
        f'<p style="margin:6px 0 0;color:{MUTED};font-size:0.82rem;">{subtitulo}</p>'
        if subtitulo else ""
    )
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,{PANEL} 0%,#111B2E 60%,#0A1628 100%);
            border:1px solid {BORDE};
            border-radius:14px;
            padding:1.4rem 1.8rem;
            margin-bottom:1.2rem;
            position:relative;overflow:hidden;
        ">
            <div style="position:absolute;top:0;right:0;width:220px;height:100%;
                background:radial-gradient(ellipse at right center,
                rgba(0,212,255,0.08) 0%,transparent 65%);pointer-events:none;"></div>
            <div style="position:absolute;top:-30px;left:-30px;width:120px;height:120px;
                background:radial-gradient(circle,rgba(59,130,246,0.06) 0%,transparent 70%);
                pointer-events:none;"></div>
            <h1 style="margin:0;padding:0;
                background:linear-gradient(90deg,{AZUL} 0%,{CYAN} 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;
                font-size:1.75rem;font-weight:700;letter-spacing:-0.4px;">{titulo}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(label: str, valor: str, delta: str = "", icon: str = "") -> None:
    """Card KPI con diseño premium (HTML). Reemplaza st.metric."""
    delta_html = ""
    if delta:
        is_pos = not delta.lstrip(" ").startswith("-")
        color  = "#10B981" if is_pos else "#EF4444"
        arrow  = "▲" if is_pos else "▼"
        clean  = delta.lstrip("+-").strip()
        delta_html = (
            f'<div style="display:flex;align-items:center;gap:4px;margin-top:6px;">'
            f'<span style="color:{color};font-size:0.72rem;font-weight:700;">'
            f'{arrow} {clean}</span>'
            f'<span style="color:#334155;font-size:0.68rem;">vs anterior</span>'
            f"</div>"
        )
    icon_html = (
        f'<div style="font-size:1.6rem;opacity:0.55;flex-shrink:0;'
        f'align-self:flex-start;">{icon}</div>'
        if icon else ""
    )
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,#0D1525 0%,#101828 100%);
            border:1px solid rgba(59,130,246,0.18);
            border-radius:14px;
            padding:1.1rem 1.3rem;
            position:relative;overflow:hidden;
            transition:border-color 0.2s,box-shadow 0.2s;
            height:100%;
        "
        onmouseover="this.style.borderColor='rgba(0,212,255,0.4)';
                     this.style.boxShadow='0 4px 24px rgba(0,212,255,0.1)'"
        onmouseout="this.style.borderColor='rgba(59,130,246,0.18)';
                    this.style.boxShadow='none'">
            <div style="position:absolute;top:0;right:0;width:70px;height:70px;
                background:radial-gradient(circle at top right,
                rgba(59,130,246,0.07),transparent 70%);pointer-events:none;"></div>
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;gap:8px;">
                <div style="flex:1;min-width:0;">
                    <div style="color:#475569;font-size:0.63rem;font-weight:700;
                        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:7px;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        {label}</div>
                    <div style="color:#F0F9FF;font-size:1.5rem;font-weight:700;
                        letter-spacing:-0.4px;line-height:1.1;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                        {valor}</div>
                    {delta_html}
                </div>
                {icon_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Spacer para que las columnas tengan altura uniforme
    st.markdown("<div style='margin-bottom:0.5rem'></div>", unsafe_allow_html=True)


# ── Plotly base ────────────────────────────────────────────────────────────────

def _base_layout(fig: go.Figure, titulo: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=13, color="#CBD5E1"), x=0, xanchor="left"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(
            color=TEXTO,
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            size=12,
        ),
        margin=dict(l=16, r=16, t=44, b=16),
        legend=dict(
            bgcolor="rgba(13,21,37,0.85)",
            bordercolor="rgba(59,130,246,0.2)",
            borderwidth=1,
            font=dict(size=11, color="#94A3B8"),
        ),
        hoverlabel=dict(
            bgcolor="#111B2E",
            bordercolor="rgba(59,130,246,0.3)",
            font=dict(color=TEXTO, size=12),
        ),
        colorway=PALETA,
    )
    axis_style = dict(
        gridcolor="rgba(30,45,70,0.6)",
        linecolor="rgba(30,45,70,0.8)",
        tickcolor=MUTED,
        tickfont=dict(color=MUTED, size=11),
        title_font=dict(color=MUTED),
        zeroline=False,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig


# ── Tipos de gráfico ───────────────────────────────────────────────────────────

def barras(df: pl.DataFrame, x: str, y: str, titulo: str = "",
           color: str | None = None, texto: str | None = None) -> go.Figure:
    fig = px.bar(
        df.to_pandas(), x=x, y=y,
        color=color, text=texto,
        color_discrete_sequence=PALETA,
    )
    fig.update_traces(textposition="outside", marker_line_width=0, opacity=0.88)
    return _base_layout(fig, titulo)


def linea(df: pl.DataFrame, x: str, y: str | list[str], titulo: str = "") -> go.Figure:
    fig = px.line(
        df.to_pandas(), x=x, y=y,
        color_discrete_sequence=PALETA, markers=True,
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    return _base_layout(fig, titulo)


def pie(df: pl.DataFrame, nombres: str, valores: str, titulo: str = "") -> go.Figure:
    fig = px.pie(
        df.to_pandas(), names=nombres, values=valores,
        color_discrete_sequence=PALETA, hole=0.45,
    )
    fig.update_traces(
        textposition="inside", textinfo="percent+label", textfont_size=11,
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
        aspect="auto", text_auto=True,
    )
    fig.update_traces(textfont=dict(color=TEXTO, size=11))
    return _base_layout(fig, titulo)
