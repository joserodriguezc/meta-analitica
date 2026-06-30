# Métricas de Campañas

Definiciones oficiales de negocio para el dominio de campañas de marketing.
El agente debe usar estas fórmulas exactas al escribir transformaciones o reportes.

## KPIs Principales

### ROAS (Return on Ad Spend)
- **Nombre:** `roas`
- **Fórmula:** `ingresos_atribuidos / gasto_real`
- **Unidad:** Ratio (ej. 3.5 = por cada $1 invertido se generan $3.50)
- **Nota:** Solo cuando `gasto_real > 0`. ROAS > 1 indica rentabilidad.

### ROI (Retorno sobre Inversión)
- **Nombre:** `roi`
- **Fórmula:** `(ingresos_atribuidos - gasto_real) / gasto_real * 100`
- **Unidad:** Porcentaje
- **Nota:** Puede ser negativo. Solo cuando `gasto_real > 0`.

### CTR (Click-Through Rate)
- **Nombre:** `ctr`
- **Fórmula:** `clicks / impresiones * 100`
- **Unidad:** Porcentaje
- **Nota:** Solo cuando `impresiones > 0`. Mide el engagement del anuncio.

### Tasa de Conversión
- **Nombre:** `tasa_conversion`
- **Fórmula:** `conversiones / clicks * 100`
- **Unidad:** Porcentaje
- **Nota:** Solo cuando `clicks > 0`.

### CPC (Costo por Click)
- **Nombre:** `cpc`
- **Fórmula:** `gasto_real / clicks`
- **Unidad:** CLP
- **Nota:** Solo cuando `clicks > 0`.

### CPA (Costo por Adquisición)
- **Nombre:** `cpa`
- **Fórmula:** `gasto_real / conversiones`
- **Unidad:** CLP
- **Nota:** Solo cuando `conversiones > 0`.

### Ejecución Presupuestaria
- **Nombre:** `ejecucion_presupuesto`
- **Fórmula:** `gasto_real / presupuesto * 100`
- **Unidad:** Porcentaje
- **Nota:** >100% indica sobregasto; <80% en finalizadas indica subejecución.

## Columnas Derivadas en ETL

| Columna | Tipo | Descripción |
|---|---|---|
| `estado` | string | `activa`, `finalizada`, `futura` — según fechas vs. fecha de carga |
| `duracion_dias` | integer | Días entre `fecha_inicio` y `fecha_fin` |
| `ejecucion_presupuesto` | float | % del presupuesto gastado |
| `ctr` | float | Click-Through Rate % (nullable) |
| `tasa_conversion` | float | % clicks que convierten (nullable) |
| `cpc` | float | Costo por click en CLP (nullable) |
| `cpa` | float | Costo por adquisición en CLP (nullable) |
| `roas` | float | Retorno sobre gasto publicitario (nullable) |
| `roi` | float | Retorno sobre inversión % (nullable) |

## Esquema Esperado de Datos Crudos

Archivo: `data/raw/campanas_<periodo>.csv`

| Columna | Tipo | Descripción | Nulos permitidos |
|---|---|---|---|
| `id_campana` | string | Identificador único | No |
| `nombre_campana` | string | Nombre descriptivo | No |
| `canal` | string | Canal de distribución | No |
| `fecha_inicio` | date | Fecha de inicio (YYYY-MM-DD) | No |
| `fecha_fin` | date | Fecha de fin (YYYY-MM-DD) | No |
| `presupuesto` | float | Presupuesto asignado en CLP | No |
| `gasto_real` | float | Gasto acumulado en CLP | No |
| `impresiones` | integer | Total de impresiones | No |
| `clicks` | integer | Total de clicks | No |
| `conversiones` | integer | Total de conversiones | No |
| `ingresos_atribuidos` | float | Ingresos atribuidos en CLP | No |

## Canales Válidos

`email`, `redes_sociales`, `display`, `search`, `video`

## Reglas de Negocio

- `presupuesto` siempre mayor a 0
- `gasto_real` puede ser 0 (campañas futuras)
- `fecha_fin` siempre posterior a `fecha_inicio`
- `impresiones`, `clicks`, `conversiones` e `ingresos_atribuidos` pueden ser 0 para campañas futuras
- `id_campana` no puede repetirse en el mismo archivo de carga
- `estado` se calcula automáticamente en el ETL según fechas relativas al día de ejecución