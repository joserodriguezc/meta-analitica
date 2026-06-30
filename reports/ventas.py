"""
Reporte de ventas — genera reports/ventas.html con datos pre-computados desde DuckDB.
Basado en los KPIs de memoria/metricas/ventas.md y requerimientos de memoria/clientes/cliente_demo.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.report_builder import (
    clp, variacion, _kpi_card, _tabla, generar_html
)

OUTPUT = Path(__file__).parent / "ventas.html"


def _seccion_kpis() -> str:
    mensual = db.query("""
        SELECT
            mes,
            SUM(ingreso_linea)                                      AS ingresos,
            COUNT(DISTINCT id_orden)                                AS ordenes,
            ROUND(SUM(ingreso_linea) / COUNT(DISTINCT id_orden), 0) AS ticket
        FROM ventas
        WHERE estado = 'completado'
        GROUP BY mes ORDER BY mes
    """)
    filas = mensual.to_dicts()
    ult, ant = filas[-1], filas[-2] if len(filas) >= 2 else None
    mes_label = ult["mes"].strftime("%B %Y").capitalize()

    cards = "".join([
        _kpi_card("Ingresos Totales", clp(ult["ingresos"]),
                  variacion(ult["ingresos"], ant["ingresos"] if ant else 0)),
        _kpi_card("Ticket Promedio", clp(ult["ticket"]),
                  variacion(ult["ticket"], ant["ticket"] if ant else 0)),
        _kpi_card("Órdenes", str(ult["ordenes"]),
                  variacion(ult["ordenes"], ant["ordenes"] if ant else 0)),
    ])
    return f'<h3>KPIs — {mes_label}</h3><div class="kpi-row">{cards}</div>'


def _seccion_mensual() -> str:
    df = db.query("""
        SELECT
            mes,
            SUM(ingreso_linea)                                      AS Ingresos,
            COUNT(DISTINCT id_orden)                                AS Ordenes,
            ROUND(SUM(ingreso_linea) / COUNT(DISTINCT id_orden), 0) AS Ticket
        FROM ventas WHERE estado = 'completado'
        GROUP BY mes ORDER BY mes
    """).with_columns([
        pl.col("mes").dt.strftime("%B %Y").alias("Mes"),
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Ticket").map_elements(clp, return_dtype=pl.Utf8),
    ]).rename({"Ordenes": "Órdenes"}).select(["Mes", "Ingresos", "Órdenes", "Ticket"])
    return _tabla(df, "Evolución Mensual de Ventas")


def _seccion_top_productos() -> str:
    df = db.query("""
        SELECT
            nombre_producto    AS Producto,
            categoria          AS Categoria,
            SUM(cantidad)      AS Unidades,
            SUM(ingreso_linea) AS Ingresos
        FROM ventas WHERE estado = 'completado'
        GROUP BY nombre_producto, categoria
        ORDER BY Unidades DESC LIMIT 5
    """).with_columns(
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8)
    )
    return _tabla(df, "Top 5 Productos por Unidades Vendidas")


def _seccion_canal() -> str:
    df = db.query("""
        SELECT
            COALESCE(canal, 'sin canal')   AS Canal,
            COUNT(DISTINCT id_orden)       AS Ordenes,
            SUM(ingreso_linea)             AS Ingresos,
            ROUND(SUM(ingreso_linea) * 100.0
                / SUM(SUM(ingreso_linea)) OVER (), 1) AS Pct
        FROM ventas WHERE estado = 'completado'
        GROUP BY canal ORDER BY Ingresos DESC
    """).with_columns(
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8)
    ).rename({"Ordenes": "Órdenes", "Pct": "% del Total"})
    return _tabla(df, "Ventas por Canal")


def _seccion_categoria() -> str:
    df = db.query("""
        SELECT
            categoria            AS Categoria,
            SUM(cantidad)        AS Unidades,
            SUM(ingreso_linea)   AS Ingresos,
            COUNT(DISTINCT id_orden) AS Ordenes
        FROM ventas WHERE estado = 'completado'
        GROUP BY categoria ORDER BY Ingresos DESC
    """).with_columns(
        pl.col("Ingresos").map_elements(clp, return_dtype=pl.Utf8)
    ).rename({"Ordenes": "Órdenes"})
    return _tabla(df, "Ventas por Categoría")


def run():
    secciones = [
        _seccion_kpis(),
        _seccion_mensual(),
        _seccion_top_productos(),
        _seccion_canal(),
        _seccion_categoria(),
    ]
    html = generar_html(
        secciones=secciones,
        titulo="Reporte de Ventas",
        subtitulo="Cliente Demo S.A. · MalayAI Arnés Analítico · Abril–Junio 2026",
    )
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  Reporte generado: {OUTPUT}")


if __name__ == "__main__":
    run()
