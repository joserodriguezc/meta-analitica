# Cliente Demo — PoC MalayAI

Perfil del cliente utilizado para la demostración de la PoC del Arnés Analítico.

## Identificación

- **Nombre:** Cliente Demo S.A.
- **Industria:** Retail / E-commerce
- **Estado:** Activo
- **Proyecto:** PoC MalayAI — Arnés Analítico

## Requerimientos del Cliente

### Reporte Principal
El cliente quiere visualizar un **reporte web de ventas mensual** que incluya:
1. Ingresos totales por mes
2. Ticket promedio por canal de venta
3. Top 5 productos más vendidos (por unidades)
4. Evolución diaria de unidades vendidas
5. Distribución de ventas por categoría

### Reglas Específicas del Cliente
- Solo incluir órdenes con estado `completado`
- Comparar siempre contra el mes anterior
- El reporte debe ser accesible vía URL pública (HTML estático)
- Los datos se actualizan una vez al día

## Fuentes de Datos

| Fuente | Formato | Ruta | Frecuencia |
|---|---|---|---|
| Sistema de ventas | CSV | `data/raw/ventas_demo.csv` | Diario |

## Convención de Archivos

El cliente puede enviar archivos con distintos nombres. El ETL los acepta vía `--archivo`:

```bash
# Archivo por defecto
uv run main.py etl ventas

# Archivo específico enviado por el cliente
uv run main.py etl ventas --archivo ventas_enero_2026.csv
uv run main.py etl ventas --archivo ventas_q1_2026.csv
```

**Regla:** El archivo siempre debe depositarse en `data/raw/` antes de ejecutar el ETL.
El esquema esperado (columnas y tipos) está definido en `memoria/metricas/ventas.md`.

## Historial de Entregas

| Fecha | Entregable | Estado |
|---|---|---|
| 2026-06-29 | Configuración inicial del harness | Completado |
| Pendiente | ETL de ventas | En desarrollo |
| Pendiente | Validación de calidad | En desarrollo |
| Pendiente | Reporte HTML de ventas | En desarrollo |

## Contacto

- **Responsable interno:** Equipo MalayAI
- **Canal de entrega:** URL pública del reporte HTML
