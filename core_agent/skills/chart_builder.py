"""
Helpers de Plotly reutilizables para reportes Streamlit.
Paleta y estilo consistente con la identidad MalayAI Lab.
"""
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st
from pathlib import Path

LOGO_PATH = Path("assets/malayai_logo.png")

PALETA = ["#4F8EF7", "#F7914F", "#4FF7A0", "#F74F4F", "#C74FF7", "#F7E14F"]
FONDO = "#0E1117"
FONDO_PANEL = "#1A1F2E"
TEXTO = "#FAFAFA"


def sidebar_logo():
    """Muestra el logo en el sidebar solo cuando el reporte corre standalone."""
    # En la app unificada (app.py) el logo ya está renderizado — no duplicar.
    if st.session_state.get("_logo_rendered"):
        return
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    st.sidebar.markdown("---")


def _base_layout(fig: go.Figure, titulo: str = "") -> go.Figure:
    fig.update_layout(
        title=titulo,
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO_PANEL,
        font_color=TEXTO,
        font_family="monospace",
        title_font_size=16,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor=FONDO_PANEL, bordercolor="#333"),
    )
    fig.update_xaxes(gridcolor="#2A2F3E", zerolinecolor="#2A2F3E")
    fig.update_yaxes(gridcolor="#2A2F3E", zerolinecolor="#2A2F3E")
    return fig


def barras(df: pl.DataFrame, x: str, y: str, titulo: str = "",
           color: str | None = None, texto: str | None = None) -> go.Figure:
    fig = px.bar(
        df.to_pandas(), x=x, y=y, title=titulo,
        color=color, text=texto,
        color_discrete_sequence=PALETA,
    )
    fig.update_traces(textposition="outside")
    return _base_layout(fig, titulo)


def linea(df: pl.DataFrame, x: str, y: str | list[str],
          titulo: str = "") -> go.Figure:
    fig = px.line(
        df.to_pandas(), x=x, y=y, title=titulo,
        color_discrete_sequence=PALETA, markers=True,
    )
    return _base_layout(fig, titulo)


def pie(df: pl.DataFrame, nombres: str, valores: str,
        titulo: str = "") -> go.Figure:
    fig = px.pie(
        df.to_pandas(), names=nombres, values=valores, title=titulo,
        color_discrete_sequence=PALETA, hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _base_layout(fig, titulo)


def scatter(df: pl.DataFrame, x: str, y: str, titulo: str = "",
            size: str | None = None, color: str | None = None,
            hover: list[str] | None = None) -> go.Figure:
    fig = px.scatter(
        df.to_pandas(), x=x, y=y, title=titulo,
        size=size, color=color, hover_data=hover,
        color_discrete_sequence=PALETA,
    )
    return _base_layout(fig, titulo)


def treemap(df: pl.DataFrame, path: list[str], valores: str,
            titulo: str = "") -> go.Figure:
    fig = px.treemap(
        df.to_pandas(), path=path, values=valores, title=titulo,
        color_discrete_sequence=PALETA,
    )
    return _base_layout(fig, titulo)


def heatmap(df: pl.DataFrame, x: str, y: str, valores: str,
            titulo: str = "") -> go.Figure:
    pivot = df.to_pandas().pivot(index=y, columns=x, values=valores).fillna(0)
    fig = px.imshow(
        pivot, title=titulo,
        color_continuous_scale="Blues", aspect="auto",
    )
    return _base_layout(fig, titulo)


def kpi(label: str, valor: str, delta: str = "") -> None:
    """Renderiza una métrica KPI con st.metric."""
    st.metric(label=label, value=valor, delta=delta if delta else None)