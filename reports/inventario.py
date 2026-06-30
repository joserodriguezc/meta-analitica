"""
Reporte de inventario — genera reports/inventario.html con datos pre-computados desde DuckDB.
Basado en los KPIs de memoria/metricas/inventario.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import polars as pl
from core_agent.skills import duckdb_client as db
from core_agent.skills.report_builder import (
    clp, _kpi_card, _tabla, generar_html
)

OUTPUT = Path(__file__).parent / "inventario.html"


def _seccion_kpis() -> str:
    resumen = db.query("""
        SELECT
            SUM(valor_stock)                                    AS valor_total,
            COUNT(*)                                            AS total_productos,
            COUNT(*) FILTER (WHERE bajo_minimo AND estado = 'activo') AS en_riesgo,
            COUNT(*) FILTER (WHERE estado = 'agotado')          AS agotados,
            ROUND(AVG(margen_bruto), 1)                         AS margen_promedio
        FROM inventario
    """).to_dicts()[0]

    cards = "".join([
        _kpi_card("Valor del Inventario", clp(resumen["valor_total"])),
        _kpi_card("Productos Totales", str(resumen["total_productos"])),
        _kpi_card("En Riesgo de Quiebre", str(resumen["en_riesgo"]), '<span style="color:#ef4444">▼ requiere reposición</span>' if resumen["en_riesgo"] > 0 else ""),
        _kpi_card("Margen Promedio", f'{resumen["margen_promedio"]}%'),
    ])
    return f'<h3>Resumen General de Inventario</h3><div class="kpi-row">{cards}</div>'


def _seccion_quiebre() -> str:
    df = db.query("""
        SELECT
            id_producto     AS SKU,
            nombre_producto AS Producto,
            categoria       AS Categoría,
            stock_actual    AS Stock,
            stock_minimo    AS Mínimo,
            ROUND(cobertura, 2) AS Cobertura,
            bodega          AS Bodega
        FROM inventario
        WHERE bajo_minimo = true AND estado = 'activo'
        ORDER BY cobertura ASC
    """)
    if len(df) == 0:
        return '<div class="table-section"><h3>Alertas de Quiebre de Stock</h3><p style="color:#22c55e;padding:12px">Sin alertas — todos los productos sobre el stock mínimo.</p></div>'
    return _tabla(df, "Alertas de Quiebre de Stock")


def _seccion_por_categoria() -> str:
    df = db.query("""
        SELECT
            categoria                       AS Categoría,
            COUNT(*)                        AS Productos,
            SUM(stock_actual)               AS Unidades,
            SUM(valor_stock)                AS Valor,
            ROUND(AVG(margen_bruto), 1)     AS "Margen %"
        FROM inventario
        WHERE estado != 'descontinuado'
        GROUP BY categoria
        ORDER BY Valor DESC
    """).with_columns(
        pl.col("Valor").map_elements(clp, return_dtype=pl.Utf8)
    )
    return _tabla(df, "Inventario por Categoría")


def _seccion_margen() -> str:
    df = db.query("""
        SELECT
            nombre_producto             AS Producto,
            categoria                   AS Categoría,
            precio_costo                AS Costo,
            precio_venta                AS Venta,
            ROUND(margen_bruto, 1)      AS "Margen %"
        FROM inventario
        WHERE estado = 'activo'
        ORDER BY margen_bruto DESC
    """).with_columns([
        pl.col("Costo").map_elements(clp, return_dtype=pl.Utf8),
        pl.col("Venta").map_elements(clp, return_dtype=pl.Utf8),
    ])
    return _tabla(df, "Margen Bruto por Producto")


def run():
    secciones = [
        _seccion_kpis(),
        _seccion_quiebre(),
        _seccion_por_categoria(),
        _seccion_margen(),
    ]
    html = generar_html(
        secciones=secciones,
        titulo="Reporte de Inventario",
        subtitulo="Cliente Demo S.A. · MalayAI Arnés Analítico · Agosto 2026",
    )
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  Reporte generado: {OUTPUT}")


if __name__ == "__main__":
    run()