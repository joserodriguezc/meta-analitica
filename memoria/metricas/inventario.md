# Métricas de Inventario

Definiciones oficiales de negocio para el dominio de inventario.
El agente debe usar estas fórmulas exactas al escribir transformaciones o reportes.

## KPIs Principales

### Valor del Inventario
- **Nombre:** `valor_inventario`
- **Fórmula:** `SUM(stock_actual * precio_costo)`
- **Unidad:** CLP
- **Nota:** Solo productos con estado `activo`

### Margen Bruto por Producto
- **Nombre:** `margen_bruto`
- **Fórmula:** `(precio_venta - precio_costo) / precio_venta * 100`
- **Unidad:** Porcentaje
- **Nota:** Representa el % de ganancia sobre el precio de venta

### Productos bajo Stock Mínimo
- **Nombre:** `quiebre_stock`
- **Fórmula:** `stock_actual < stock_minimo AND estado = 'activo'`
- **Unidad:** Cantidad de productos en riesgo
- **Nota:** Requiere acción inmediata de reposición

### Cobertura de Stock
- **Nombre:** `cobertura`
- **Fórmula:** `stock_actual / stock_minimo`
- **Unidad:** Ratio (ej. 2.0 = tiene el doble del mínimo requerido)

## Esquema Esperado de Datos Crudos

Archivo: `data/raw/inventario_<periodo>.csv`

| Columna | Tipo | Descripción | Nulos permitidos |
|---|---|---|---|
| `id_producto` | string | SKU del producto (único) | No |
| `nombre_producto` | string | Nombre descriptivo | No |
| `categoria` | string | Categoría del producto | No |
| `stock_actual` | integer | Unidades disponibles en bodega | No |
| `stock_minimo` | integer | Unidades mínimas requeridas | No |
| `precio_costo` | float | Precio de adquisición en CLP | No |
| `precio_venta` | float | Precio de venta al público en CLP | No |
| `bodega` | string | Bodega donde está almacenado | No |
| `fecha_actualizacion` | date | Fecha del último conteo (YYYY-MM-DD) | No |
| `estado` | string | `activo`, `agotado`, `descontinuado` | No |

## Reglas de Negocio

- `precio_venta` siempre debe ser mayor que `precio_costo`
- `stock_actual` puede ser 0 (producto agotado) pero no negativo
- `stock_minimo` debe ser mayor que 0
- Los productos con estado `descontinuado` se excluyen de los KPIs de cobertura
- Un `id_producto` no puede repetirse en el mismo archivo de carga