---
type: metric_domain
title: "Métricas de Ventas"
description: "KPIs, esquema y reglas de negocio del dominio de ventas (ingresos, ticket promedio, unidades)"
resource: "duckdb://data/local.duckdb#ventas"
tags: [ventas, kpi, retail, ingresos]
timestamp: "2026-07-11"
---

# Métricas de Ventas

Definiciones oficiales de negocio para el dominio de ventas.
El agente debe usar estas fórmulas exactas al escribir transformaciones o reportes.

## KPIs Principales

### Ingresos Totales
- **Nombre:** `ingresos_totales`
- **Fórmula:** `SUM(precio_unitario * cantidad)`
- **Unidad:** Moneda local (CLP)
- **Granularidad:** Diario, mensual

### Ticket Promedio
- **Nombre:** `ticket_promedio`
- **Fórmula:** `SUM(precio_unitario * cantidad) / COUNT(DISTINCT id_orden)`
- **Unidad:** CLP por orden
- **Nota:** Solo considera órdenes con estado `completado`

### Unidades Vendidas
- **Nombre:** `unidades_vendidas`
- **Fórmula:** `SUM(cantidad)`
- **Unidad:** Unidades
- **Granularidad:** Diario, por producto

### Tasa de Conversión
- **Nombre:** `tasa_conversion`
- **Fórmula:** `COUNT(DISTINCT id_orden) / COUNT(DISTINCT id_sesion)`
- **Unidad:** Porcentaje (0-100)
- **Nota:** Requiere tabla de sesiones web

### ROAS (Return on Ad Spend)
- **Nombre:** `roas`
- **Fórmula:** `ingresos_totales / gasto_publicitario`
- **Unidad:** Ratio (ej. 3.5 = $3.5 ingresados por $1 invertido)
- **Nota:** Requiere tabla de inversión publicitaria

## Esquema Esperado de Datos Crudos

Archivo: `data/raw/ventas_demo.csv`

| Columna | Tipo | Descripción | Nulos permitidos |
|---|---|---|---|
| `id_orden` | string | Identificador único de orden | No |
| `fecha` | date | Fecha de la transacción (YYYY-MM-DD) | No |
| `id_producto` | string | SKU del producto | No |
| `nombre_producto` | string | Nombre descriptivo | No |
| `categoria` | string | Categoría del producto | No |
| `cantidad` | integer | Unidades vendidas | No |
| `precio_unitario` | float | Precio por unidad en CLP | No |
| `estado` | string | `completado`, `cancelado`, `pendiente` | No |
| `canal` | string | `online`, `tienda`, `marketplace` | Sí |
| `id_sesion` | string | Sesión web asociada | Sí |

## Reglas de Negocio

- Las órdenes con estado `cancelado` se excluyen de todos los KPIs de ingresos
- El precio unitario no puede ser negativo ni cero
- Las fechas no pueden ser futuras al momento de la carga
- Un `id_orden` no puede repetirse en el mismo día

## Vínculos

- **Cliente que usa este dominio:** [Cliente Demo](../clientes/cliente_demo.md)
- **Receta de ingesta:** [Crear un ETL](../../core_agent/tasks/crear_etl.md)
- **Receta de validación:** [Validar Calidad](../../core_agent/tasks/validar_calidad.md)
- **Receta de reporte:** [Crear un Reporte](../../core_agent/tasks/crear_reporte.md)
