# Índice de Memoria — meta-analitica

Este archivo es el punto de entrada al conocimiento de negocio del proyecto.
El agente debe leerlo antes de ejecutar cualquier tarea analítica.

## Métricas de Negocio

| Archivo | Dominio | Descripción |
|---|---|---|
| [metricas/ventas.md](metricas/ventas.md) | Ventas | KPIs de ventas: ingresos, ticket promedio, unidades |
| [metricas/inventario.md](metricas/inventario.md) | Inventario | Stock, valor, margen bruto, alertas de quiebre |
| [metricas/campanas.md](metricas/campanas.md) | Campañas | ROAS, ROI, CTR, CPC, CPA, tasa de conversión |
| [metricas/devoluciones.md](metricas/devoluciones.md) | Devoluciones | Tasa de aprobación, reembolso total/promedio, motivos, canales |
| [metricas/envios.md](metricas/envios.md) | Envíos | Tasa de entrega a tiempo, tasa de retraso, costo de envíos, días de retraso |

## Clientes Activos

| Archivo | Cliente | Estado |
|---|---|---|
| [clientes/cliente_demo.md](clientes/cliente_demo.md) | Cliente Demo | Activo — PoC MalayAI |

## Recetas de Tareas Disponibles

| Archivo | Cuándo usarla |
|---|---|
| [../core_agent/tasks/crear_etl.md](../core_agent/tasks/crear_etl.md) | Crear un nuevo pipeline de ingesta |
| [../core_agent/tasks/validar_calidad.md](../core_agent/tasks/validar_calidad.md) | Validar calidad de datos con Pandera |
| [../core_agent/tasks/crear_reporte.md](../core_agent/tasks/crear_reporte.md) | Generar un reporte Streamlit interactivo |

## Tipos de Conocimiento (OKF Bundle)

Este directorio es un **bundle OKF conforme** (Open Knowledge Format v0.1). Cada archivo `.md` no reservado contiene frontmatter YAML con un campo `type` que identifica su rol:

| Tipo | Archivos | Significado |
|---|---|---|
| `metric_domain` | `metricas/*.md` | KPIs, esquema de datos y reglas de negocio de un dominio |
| `client_profile` | `clientes/*.md` | Perfil, requerimientos y fuentes de datos del cliente |
| `task_recipe` | `../core_agent/tasks/*.md` | Procedimientos paso a paso para el agente |

Archivos reservados OKF: `index.md` (este archivo) y `log.md` (bitácora cronológica).

## Novedades Recientes

Ver `log.md` para el historial de decisiones y cambios arquitectónicos.
