---
type: client_profile
title: "Cliente Demo — PoC MalayAI"
description: "Perfil y requerimientos del cliente de demostración (retail e-commerce, 5 dominios analíticos)"
resource: "data/raw/ventas_demo.csv"
tags: [cliente, retail, poc, demo, ecommerce]
timestamp: "2026-07-11"
---

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
| Sistema de logística | CSV | `data/raw/envios_<periodo>.csv` | Por período (Q1/Q2/Q3/Q4) |

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
| 2026-06-29 | ETL de ventas + validación Pandera | Completado |
| 2026-06-29 | Dominio campañas (ETL + validación + reporte) | Completado |
| 2026-06-29 | Dominio devoluciones (ETL + validación + reporte) | Completado |
| 2026-06-30 | Dominio envíos (ETL + validación + reporte) | Completado |

## Contacto

- **Responsable interno:** Equipo MalayAI
- **Canal de entrega:** Dashboard Streamlit vía `uv run main.py deploy`

## Dominios Analíticos Activos

- [Ventas](../metricas/ventas.md) — ingresos, ticket promedio, unidades vendidas
- [Inventario](../metricas/inventario.md) — valor stock, margen bruto, quiebre de stock
- [Campañas](../metricas/campanas.md) — ROAS, ROI, CTR, CPA
- [Devoluciones](../metricas/devoluciones.md) — tasa de aprobación, reembolso
- [Envíos](../metricas/envios.md) — entrega a tiempo, couriers, costos logísticos
