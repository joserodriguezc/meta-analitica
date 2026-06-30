# Métricas de Envíos

Definiciones oficiales de negocio para el dominio de envíos.
El agente debe usar estas fórmulas exactas al escribir transformaciones o reportes.

## KPIs Principales

### Tasa de Entrega a Tiempo
- **Nombre:** `tasa_entrega_a_tiempo`
- **Fórmula:** `COUNT(*) FILTER (WHERE estado = 'entregado') / NULLIF(COUNT(*) FILTER (WHERE estado != 'en_transito'), 0) * 100`
- **Unidad:** Porcentaje
- **Nota:** Excluye envíos en tránsito del denominador (aún no se puede evaluar su puntualidad).

### Tasa de Retraso
- **Nombre:** `tasa_retraso`
- **Fórmula:** `COUNT(*) FILTER (WHERE estado = 'retrasado') / NULLIF(COUNT(*) FILTER (WHERE estado != 'en_transito'), 0) * 100`
- **Unidad:** Porcentaje

### Costo Total de Envíos
- **Nombre:** `costo_total_envios`
- **Fórmula:** `SUM(costo_envio)`
- **Unidad:** CLP

### Costo Promedio por Envío
- **Nombre:** `costo_promedio_envio`
- **Fórmula:** `AVG(costo_envio)`
- **Unidad:** CLP

### Días Promedio de Retraso
- **Nombre:** `dias_retraso_promedio`
- **Fórmula:** `AVG(dias_retraso) FILTER (WHERE estado = 'retrasado')`
- **Unidad:** Días
- **Nota:** Solo considera envíos con estado `retrasado`. Valores positivos = llegó tarde.

### Envíos en Tránsito
- **Nombre:** `envios_en_transito`
- **Fórmula:** `COUNT(*) FILTER (WHERE estado = 'en_transito')`
- **Unidad:** Unidades

## Columnas Derivadas en ETL

| Columna | Tipo | Descripción |
|---|---|---|
| `dias_retraso` | integer nullable | `(fecha_entrega_real - fecha_entrega_estimada).total_days()` — null cuando `estado = 'en_transito'` |
| `mes` | date | Primer día del mes de `fecha_despacho` |

## Esquema Esperado de Datos Crudos

Archivo: `data/raw/envios_<periodo>.csv`

| Columna | Tipo | Descripción | Nulos permitidos |
|---|---|---|---|
| `id_envio` | string | Identificador único del envío | No |
| `id_orden` | string | Orden asociada | No |
| `fecha_despacho` | date | Fecha en que salió del depósito (YYYY-MM-DD) | No |
| `fecha_entrega_estimada` | date | Fecha prometida de entrega (YYYY-MM-DD) | No |
| `fecha_entrega_real` | date | Fecha real de entrega (YYYY-MM-DD) | Sí — null si `en_transito` |
| `courier` | string | Empresa de transporte | No |
| `tipo_envio` | string | Modalidad de entrega | No |
| `costo_envio` | float | Costo del envío en CLP | No |
| `region_destino` | string | Región de destino en Chile | No |
| `estado` | string | Estado actual del envío | No |
| `peso_kg` | float | Peso del paquete en kg | No |

## Couriers Válidos

`chilexpress`, `starken`, `bluexpress`, `correos`

## Tipos de Envío Válidos

`estandar`, `express`, `mismo_dia`

## Estados Válidos

`entregado`, `retrasado`, `en_transito`

## Reglas de Negocio

- `id_envio` no puede repetirse en el mismo archivo de carga
- `fecha_entrega_real` es null únicamente cuando `estado = 'en_transito'`
- `costo_envio` siempre mayor a 0
- `peso_kg` siempre mayor a 0
- `fecha_despacho` no puede ser posterior a `fecha_entrega_estimada`
