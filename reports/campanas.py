"""
Reporte de campañas — genera reports/campanas.html con datos pre-computados desde DuckDB.
Basado en los KPIs de memoria/metricas/campanas.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.report_builder import (
    clp, variacion, _kpi_card, _tabla, generar_html
)

OUTPUT = Path(__file__).parent / "campanas.html"

_ESTADO_BADGE = {
    "activa":     '<span style="color:#22c55e;font-weight:600">● activa</span>',
    "finalizada": '<span style="color:#94a3b8">◆ finalizada</span>',
    "futura":     '<span style="color:#60a5fa">◇ futura</span>',
}


def _seccion_kpis() -> str:
    r = db.query("""
        SELECT
            SUM(presupuesto)                                            AS presupuesto_total,
            SUM(gasto_real)                                             AS gasto_total,
            SUM(ingresos_atribuidos)                                    AS ingresos_total,
            ROUND(SUM(ingresos_atribuidos) / NULLIF(SUM(gasto_real),0), 2) AS roas_global,
            COUNT(*)                                                    AS total_campanas,
            COUNT(*) FILTER (WHERE estado = 'activa')                   AS activas
        FROM campanas
    """).to_dicts()[0]

    roas_str = f'{r["roas_global"]}x' if r["roas_global"] else "—"
    delta_activas = f'<span style="color:#22c55e">{r["activas"]} activa(s) ahora</span>' if r["activas"] else ""

    cards = "".join([
        _kpi_card("Presupuesto Total", clp(r["presupuesto_total"])),
        _kpi_card("Gasto Real", clp(r["gasto_total"])),
        _kpi_card("Ingresos Atribuidos", clp(r["ingresos_total"])),
        _kpi_card("ROAS Global", roas_str),
        _kpi_card("Campañas", str(r["total_campanas"]), delta_activas),
    ])
    return f'<h3>Resumen General de Campañas</h3><div class="kpi-row">{cards}</div>'


def _seccion_por_canal() -> str:
    df = db.query("""
        SELECT
            canal                                                                   AS Canal,
            COUNT(*)                                                                AS Campañas,
            SUM(impresiones)                                                        AS Impresiones,
            SUM(clicks)                                                             AS Clicks,
            ROUND(SUM(clicks) * 100.0 / NULLIF(SUM(impresiones), 0), 2)            AS "CTR %",
            SUM(conversiones)                                                       AS Conversiones,
            SUM(gasto_real)                                                         AS Gasto,
            SUM(ingresos_atribuidos)                                                AS Ingresos,
            ROUND(SUM(ingresos_atribuidos) / NULLIF(SUM(gasto_real), 0), 2)        AS ROAS
        FROM campanas
        GROUP BY canal
        ORDER BY Ingresos DESC
    """).with_columns([
        pl.col("Gasto").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8),
    ])
    return _tabla(df, "Performance por Canal")


def _seccion_campanas() -> str:
    df = db.query("""
        SELECT
            id_campana                              AS ID,
            nombre_campana                          AS Campaña,
            canal                                   AS Canal,
            estado                                  AS Estado,
            CAST(fecha_inicio AS VARCHAR)           AS Inicio,
            CAST(fecha_fin AS VARCHAR)              AS Fin,
            duracion_dias                           AS Días,
            gasto_real                              AS Gasto,
            ingresos_atribuidos                     AS Ingresos,
            ROUND(ejecucion_presupuesto, 1)         AS "Ejec %",
            ROUND(roas, 2)                          AS ROAS,
            ROUND(ctr, 2)                           AS "CTR %"
        FROM campanas
        ORDER BY fecha_inicio DESC
    """).with_columns([
        pl.col("Estado").map_elements(
            lambda e: _ESTADO_BADGE.get(e, e), return_dtype=pl.Utf8
        ),
        pl.col("Gasto").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8),
    ])
    return _tabla(df, "Todas las Campañas")


def _seccion_top_roas() -> str:
    df = db.query("""
        SELECT
            nombre_campana              AS Campaña,
            canal                       AS Canal,
            gasto_real                  AS Gasto,
            ingresos_atribuidos         AS Ingresos,
            ROUND(roas, 2)              AS ROAS,
            ROUND(roi, 1)               AS "ROI %",
            ROUND(cpa, 0)               AS CPA,
            ROUND(tasa_conversion, 2)   AS "Conv %"
        FROM campanas
        WHERE gasto_real > 0
        ORDER BY roas DESC NULLS LAST
        LIMIT 5
    """).with_columns([
        pl.col("Gasto").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("CPA").map_elements(
            lambda v: clp(v) if v is not None else "—", return_dtype=pl.Utf8
        ),
    ])
    return _tabla(df, "Top 5 Campañas por ROAS")


def run():
    secciones = [
        _seccion_kpis(),
        _seccion_por_canal(),
        _seccion_campanas(),
        _seccion_top_roas(),
    ]
    html = generar_html(
        secciones=secciones,
        titulo="Reporte de Campañas de Marketing",
        subtitulo="Cliente Demo S.A. · MalayAI Arnés Analítico · Junio 2026",
    )
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  Reporte generado: {OUTPUT}")


if __name__ == "__main__":
    run()