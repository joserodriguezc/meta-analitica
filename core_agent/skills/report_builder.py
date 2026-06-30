"""
Utilidades para generar reportes HTML estáticos con datos pre-computados.
"""
import polars as pl
from pathlib import Path
from datetime import datetime


def clp(valor: float) -> str:
    return f"${valor:,.0f}".replace(",", ".")


def variacion(actual: float, anterior: float) -> str:
    if not anterior:
        return ""
    pct = (actual - anterior) / anterior * 100
    signo = "▲" if pct >= 0 else "▼"
    color = "#22c55e" if pct >= 0 else "#ef4444"
    return f'<span style="color:{color};font-size:0.8em">{signo} {abs(pct):.1f}%</span>'


def _kpi_card(titulo: str, valor: str, delta: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-delta">{delta}</div>
    </div>"""


def _tabla(df: pl.DataFrame, titulo: str = "") -> str:
    headers = "".join(f"<th>{col}</th>" for col in df.columns)
    rows = "".join(
        "<tr>" + "".join(f"<td>{v}</td>" for v in row.values()) + "</tr>"
        for row in df.to_dicts()
    )
    titulo_html = f"<h3>{titulo}</h3>" if titulo else ""
    return f"""
    <div class="table-section">
        {titulo_html}
        <table>
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""


def _css() -> str:
    return """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #f8fafc; color: #1e293b; padding: 32px; }
        .container { max-width: 1100px; margin: 0 auto; }
        header { margin-bottom: 32px; }
        header h1 { font-size: 1.8em; color: #0f172a; }
        header p { color: #64748b; margin-top: 6px; font-size: 0.9em; }
        .kpi-row { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
        .kpi-card { background: #1e293b; border-radius: 10px; padding: 20px 28px;
                    min-width: 200px; flex: 1; }
        .kpi-title { font-size: 0.75em; color: #94a3b8; text-transform: uppercase;
                     letter-spacing: 1px; margin-bottom: 8px; }
        .kpi-value { font-size: 1.9em; font-weight: 700; color: #f1f5f9; }
        .kpi-delta { margin-top: 6px; min-height: 1em; }
        .table-section { background: #fff; border-radius: 10px; padding: 24px;
                         margin-bottom: 24px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
        h3 { font-size: 1em; color: #475569; text-transform: uppercase;
             letter-spacing: .5px; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.92em; }
        thead th { background: #0f172a; color: #e2e8f0; padding: 10px 14px;
                   text-align: left; font-weight: 500; }
        tbody tr:nth-child(even) { background: #f8fafc; }
        tbody td { padding: 10px 14px; border-bottom: 1px solid #e2e8f0; }
        footer { text-align: center; color: #94a3b8; font-size: 0.8em; margin-top: 32px; }
    </style>"""


def generar_html(secciones: list[str], titulo: str, subtitulo: str = "") -> str:
    generado = datetime.now().strftime("%Y-%m-%d %H:%M")
    cuerpo = "\n".join(secciones)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    {_css()}
</head>
<body>
    <div class="container">
        <header>
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </header>
        {cuerpo}
        <footer>Generado el {generado} · Arnés Analítico MalayAI · <code>uv run main.py deploy</code></footer>
    </div>
</body>
</html>"""


# Exporta las funciones de bajo nivel para que los reportes las usen
__all__ = ["clp", "variacion", "_kpi_card", "_tabla", "_css", "generar_html"]
