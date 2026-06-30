"""
Reporte de devoluciones — genera reports/devoluciones.html con datos pre-computados desde DuckDB.
Basado en los KPIs de memoria/metricas/devoluciones.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.report_builder import (
    clp, variacion, _kpi_card, _tabla, generar_html
)

OUTPUT = Path(__file__).parent / "devoluciones.html"

_ESTADO_BADGE = {
    "aprobada":  '<span style="color:#22c55e;font-weight:600">✓ aprobada</span>',
    "rechazada": '<span style="color:#ef4444;font-weight:600">✗ rechazada</span>',
    "pendiente": '<span style="color:#f59e0b">⏳ pendiente</span>',
}


def _seccion_kpis() -> str:
    r = db.query("""
        SELECT
            COUNT(*)                                                            AS total_solicitudes,
            COUNT(*) FILTER (WHERE estado = 'aprobada')                        AS aprobadas,
            ROUND(
                COUNT(*) FILTER (WHERE estado = 'aprobada') * 100.0 / COUNT(*), 1
            )                                                                   AS tasa_aprobacion,
            SUM(reembolso) FILTER (WHERE estado = 'aprobada')                  AS reembolso_total,
            ROUND(AVG(reembolso) FILTER (WHERE estado = 'aprobada'), 0)        AS reembolso_promedio,
            SUM(cantidad_devuelta)                                              AS unidades_devueltas
        FROM devoluciones
    """).to_dicts()[0]

    tasa = f'{r["tasa_aprobacion"]}%' if r["tasa_aprobacion"] is not None else "—"
    delta_aprobadas = f'<span style="color:#22c55e">{r["aprobadas"]} aprobadas</span>' if r["aprobadas"] else ""

    cards = "".join([
        _kpi_card("Total Solicitudes", str(r["total_solicitudes"])),
        _kpi_card("Tasa de Aprobación", tasa, delta_aprobadas),
        _kpi_card("Reembolso Total", clp(r["reembolso_total"] or 0)),
        _kpi_card("Reembolso Promedio", clp(r["reembolso_promedio"] or 0)),
        _kpi_card("Unidades Devueltas", str(r["unidades_devueltas"] or 0)),
    ])
    return f'<h3>Resumen General de Devoluciones</h3><div class="kpi-row">{cards}</div>'


def _seccion_por_motivo() -> str:
    df = db.query("""
        SELECT
            motivo                                              AS Motivo,
            COUNT(*)                                            AS Solicitudes,
            COUNT(*) FILTER (WHERE estado = 'aprobada')        AS Aprobadas,
            ROUND(
                COUNT(*) FILTER (WHERE estado = 'aprobada') * 100.0 / COUNT(*), 1
            )                                                   AS "Aprobación %",
            SUM(reembolso) FILTER (WHERE estado = 'aprobada')  AS "Reembolso Total"
        FROM devoluciones
        GROUP BY motivo
        ORDER BY Solicitudes DESC
    """).with_columns([
        pl.col("Reembolso Total").map_elements(
            lambda v: clp(v) if v is not None else "—", return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Devoluciones por Motivo")


def _seccion_por_categoria() -> str:
    df = db.query("""
        SELECT
            categoria                                           AS Categoría,
            COUNT(*)                                            AS Solicitudes,
            SUM(cantidad_devuelta)                              AS Unidades,
            SUM(valor_devolucion)                               AS "Valor Devuelto",
            SUM(reembolso) FILTER (WHERE estado = 'aprobada')  AS "Reembolso Aprobado"
        FROM devoluciones
        GROUP BY categoria
        ORDER BY Solicitudes DESC
    """).with_columns([
        pl.col("Valor Devuelto").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Reembolso Aprobado").map_elements(
            lambda v: clp(v) if v is not None else "—", return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Devoluciones por Categoría")


def _seccion_por_canal() -> str:
    df = db.query("""
        SELECT
            canal_devolucion                                    AS Canal,
            COUNT(*)                                            AS Solicitudes,
            COUNT(*) FILTER (WHERE estado = 'aprobada')        AS Aprobadas,
            COUNT(*) FILTER (WHERE estado = 'rechazada')       AS Rechazadas,
            COUNT(*) FILTER (WHERE estado = 'pendiente')       AS Pendientes,
            SUM(reembolso) FILTER (WHERE estado = 'aprobada')  AS "Reembolso Total"
        FROM devoluciones
        GROUP BY canal_devolucion
        ORDER BY Solicitudes DESC
    """).with_columns([
        pl.col("Reembolso Total").map_elements(
            lambda v: clp(v) if v is not None else "—", return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Devoluciones por Canal")


def _seccion_por_mes() -> str:
    df = db.query("""
        SELECT
            CAST(mes AS VARCHAR)                                AS Mes,
            COUNT(*)                                            AS Solicitudes,
            COUNT(*) FILTER (WHERE estado = 'aprobada')        AS Aprobadas,
            SUM(cantidad_devuelta)                              AS Unidades,
            SUM(reembolso) FILTER (WHERE estado = 'aprobada')  AS "Reembolso Total"
        FROM devoluciones
        GROUP BY mes
        ORDER BY mes
    """).with_columns([
        pl.col("Reembolso Total").map_elements(
            lambda v: clp(v) if v is not None else "—", return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Evolución Mensual de Devoluciones")


def _seccion_detalle() -> str:
    df = db.query("""
        SELECT
            id_devolucion                       AS ID,
            id_orden                            AS Orden,
            CAST(fecha_devolucion AS VARCHAR)   AS Fecha,
            nombre_producto                     AS Producto,
            categoria                           AS Categoría,
            cantidad_devuelta                   AS Cant,
            valor_devolucion                    AS "Valor Dev.",
            motivo                              AS Motivo,
            estado                              AS Estado,
            canal_devolucion                    AS Canal,
            reembolso                           AS Reembolso
        FROM devoluciones
        ORDER BY fecha_devolucion DESC
        LIMIT 50
    """).with_columns([
        pl.col("Valor Dev.").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Reembolso").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Estado").map_elements(
            lambda e: _ESTADO_BADGE.get(e, e), return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Detalle de Devoluciones (últimas 50)")


def run():
    secciones = [
        _seccion_kpis(),
        _seccion_por_motivo(),
        _seccion_por_categoria(),
        _seccion_por_canal(),
        _seccion_por_mes(),
        _seccion_detalle(),
    ]
    html = generar_html(
        secciones=secciones,
        titulo="Reporte de Devoluciones",
        subtitulo="Cliente Demo S.A. · MalayAI Arnés Analítico · Q3 2026",
    )
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  Reporte generado: {OUTPUT}")


if __name__ == "__main__":
    run()