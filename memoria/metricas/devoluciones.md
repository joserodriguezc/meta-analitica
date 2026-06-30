# Métricas de Devoluciones

Definiciones oficiales de negocio para el dominio de devoluciones.
El agente debe usar estas fórmulas exactas al escribir transformaciones o reportes.

## KPIs Principales

### Tasa de Aprobación
- **Nombre:** `tasa_aprobacion`
- **Fórmula:** `COUNT(*) FILTER (WHERE estado = 'aprobada') / COUNT(*) * 100`
- **Unidad:** Porcentaje
- **Nota:** Refleja qué porcentaje de solicitudes de devolución se aprueban.

### Monto Reembolsado Total
- **Nombre:** `reembolso_total`
- **Fórmula:** `SUM(reembolso) FILTER (WHERE estado = 'aprobada')`
- **Unidad:** CLP
- **Nota:** Solo considera devoluciones aprobadas.

### Reembolso Promedio
- **Nombre:** `reembolso_promedio`
- **Fórmula:** `AVG(reembolso) FILTER (WHERE estado = 'aprobada')`
- **Unidad:** CLP

### Valor Devuelto Total
- **Nombre:** `valor_devolucion_total`
- **Fórmula:** `SUM(valor_devolucion)` (sobre devoluciones aprobadas)
- **Unidad:** CLP
- **Nota:** `valor_devolucion = cantidad_devuelta * precio_unitario`

### Unidades Devueltas
- **Nombre:** `unidades_devueltas`
- **Fórmula:** `SUM(cantidad_devuelta)`
- **Unidad:** Unidades

## Columnas Derivadas en ETL

| Columna | Tipo | Descripción |
|---|---|---|
| `valor_devolucion` | float | `cantidad_devuelta * precio_unitario` |
| `mes` | date | Primer día del mes de `fecha_devolucion` |

## Esquema Esperado de Datos Crudos

Archivo: `data/raw/devoluciones_<periodo>.csv`

| Columna | Tipo | Descripción | Nulos permitidos |
|---|---|---|---|
| `id_devolucion` | string | Identificador único de la devolución | No |
| `id_orden` | string | Orden original asociada | No |
| `fecha_devolucion` | date | Fecha de la solicitud (YYYY-MM-DD) | No |
| `id_producto` | string | Identificador del producto | No |
| `nombre_producto` | string | Nombre del producto | No |
| `categoria` | string | Categoría del producto | No |
| `cantidad_devuelta` | integer | Unidades devueltas | No |
| `precio_unitario` | float | Precio unitario en CLP | No |
| `motivo` | string | Motivo declarado de la devolución | No |
| `estado` | string | Estado de la solicitud | No |
| `canal_devolucion` | string | Canal por donde se hizo la devolución | No |
| `reembolso` | float | Monto reembolsado en CLP | No |

## Motivos Válidos

`cambio_opinion`, `dano_envio`, `defecto`, `no_esperado`, `talla_incorrecta`

## Estados Válidos

`aprobada`, `rechazada`, `pendiente`

## Canales de Devolución Válidos

`courier`, `online`, `tienda`

## Reglas de Negocio

- `id_devolucion` no puede repetirse en el mismo archivo de carga
- `cantidad_devuelta` siempre mayor a 0
- `precio_unitario` siempre mayor a 0
- `reembolso` puede ser 0 (devoluciones rechazadas o pendientes)
- `reembolso` no puede ser negativo
- `fecha_devolucion` debe ser posterior al año 2020
- `reembolso` no debe superar `valor_devolucion` (cantidad_devuelta * precio_unitario)