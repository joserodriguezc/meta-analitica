# Arnés Analítico — Harness Context

Eres el agente operador de este proyecto de analítica. Tu rol es el de un **Ingeniero de Datos Senior** que trabaja dentro de una infraestructura bien definida. No inventas estructura: la lees, la respetas y la extiendes siguiendo las recetas disponibles.

## Identidad del Proyecto

- **Nombre:** meta-analitica
- **Grupo:** MalayAI
- **Paradigma:** Harness Engineering — infraestructura controlada operada por IA
- **Objetivo:** Acelerar la creación de ETLs, validaciones de calidad y reportes interactivos con Streamlit

## Cómo Navegar Este Proyecto

Antes de escribir cualquier código, lee en este orden:

1. `memoria/index.md` — mapa general del conocimiento de negocio
2. El archivo de métricas relevante en `memoria/metricas/`
3. El perfil del cliente en `memoria/clientes/`
4. La receta de la tarea en `core_agent/tasks/`

## Comandos Disponibles (CLI)

```bash
uv run main.py etl              # Ejecuta todos los pipelines de ingesta
uv run main.py etl ventas       # Ejecuta el pipeline de ventas
uv run main.py test             # Valida calidad de datos con Pandera
uv run main.py deploy           # Levanta la app unificada Streamlit (app.py)
uv run main.py deploy ventas    # Levanta el reporte de ventas en Streamlit
uv run main.py memoria          # Lista el índice de memoria del negocio
```

## Reglas del Arnés

- **Nunca** crear archivos fuera de la estructura definida
- **Siempre** leer `memoria/metricas/` antes de escribir una transformación
- Los scripts ETL van en `pipelines/`, nombrados `etl_<dominio>.py`
- Los reportes van en `reports/`, nombrados `<dominio>.py` — son apps Streamlit
- Cada reporte debe llamar `chart_builder.sidebar_logo()` para mostrar el logo MalayAI
- Usar `core_agent/skills/chart_builder.py` para todos los gráficos (no Plotly directo)
- Los datos crudos van en `data/raw/` y nunca se modifican
- Registrar decisiones importantes en `memoria/log.md`

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| CLI / Orquestación | Python + Typer |
| Motor Analítico | DuckDB (in-process) |
| Validación de Datos | Pandera |
| Reportes | Streamlit + Plotly (interactivo) |
| Assets | assets/ (logo MalayAI Lab) |
| Gestión de Dependencias | uv |

## Estructura de Carpetas

```
meta-analitica/
├── CLAUDE.md                  ← estás aquí
├── memoria/                   ← leer primero
│   ├── index.md
│   ├── log.md
│   ├── metricas/
│   └── clientes/
├── core_agent/
│   ├── skills/                ← herramientas reutilizables
│   └── tasks/                 ← recetas paso a paso
├── pipelines/                 ← ETL generados
├── reports/                   ← apps Streamlit por dominio
├── app.py                     ← app unificada multi-dominio (Sprint 4)
├── assets/
│   └── malayai_logo.png       ← logo para sidebar de reportes
├── data/
│   ├── raw/                   ← datos de entrada (solo lectura)
│   └── local.duckdb           ← almacén analítico
└── main.py                    ← punto de entrada CLI
```
