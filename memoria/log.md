# Bitácora de Decisiones Arquitectónicas

Registro cronológico de decisiones técnicas y de negocio relevantes para el proyecto.

---

## 2026-06-29 — Inicio del Proyecto

**Decisión:** Adoptar el paradigma Harness Engineering para la PoC de MalayAI.

**Contexto:** En lugar de construir un agente conversacional propio, se provee una infraestructura controlada (CLI + DuckDB + Marimo) que permite a Claude Code operar sobre datos y reglas de negocio de forma auditable.

**Alternativas descartadas:**
- Chatbot conversacional propio: mayor complejidad, menor auditabilidad
- Evidence.dev: descartado por dependencia de Node.js; reemplazado por Marimo (Python puro)
- Great Expectations: reemplazado por Pandera por ser más ligero y mejor integrado con DuckDB

**Stack definido:**
- CLI: Python + Typer
- Motor analítico: DuckDB (in-process)
- Validación: Pandera
- Reportes: Marimo → HTML estático
- Gestión de dependencias: uv

---

## 2026-06-29 — Sprint 1: Sistema de Memoria

**Decisión:** Crear `CLAUDE.md` como harness context principal en la raíz del proyecto.

**Contexto:** Claude Code lee este archivo automáticamente al iniciarse en el proyecto, lo que lo convierte en el punto de entrada ideal para definir el rol del agente, los comandos disponibles y las reglas del arnés.

**Estructura de memoria definida:**
- `memoria/index.md` — mapa de conocimiento navegable
- `memoria/metricas/` — definiciones de KPIs con esquemas y reglas de negocio
- `memoria/clientes/` — perfiles y requerimientos por cliente
- `core_agent/tasks/` — recetas paso a paso para tareas recurrentes

---

## 2026-06-29 — Sprint 2: CLI Typer

**Decisión:** Implementar el CLI con cuatro comandos: `etl`, `test`, `deploy`, `memoria`.

**Contexto:** `_load_module()` usando `importlib` permite que el CLI invoque scripts en `pipelines/` y `reports/` sin acoplarlos como imports estáticos. Esto facilita agregar nuevos dominios sin tocar `main.py`.

**Dependencias instaladas:** `typer`, `duckdb`, `pandera[polars]`, `polars`, `marimo`, `pyarrow`.

---

## 2026-06-29 — Sprint 3: ETL de Ventas

**Decisión:** Agregar columnas calculadas (`ingreso_linea`, `mes`) en la capa de transformación antes de cargar a DuckDB.

**Contexto:** Tener estas columnas pre-calculadas en DuckDB evita repetir lógica en cada consulta SQL de los reportes. Se alinea con las fórmulas de `memoria/metricas/ventas.md`.

**Nota:** `pyarrow` fue necesario como puente para que DuckDB pueda leer DataFrames Polars.

---

## 2026-06-29 — Sprint 4: Validación de Calidad

**Decisión:** Usar `element_wise=True` en los checks personalizados de Pandera Polars.

**Contexto:** La API `pandera.polars` pasa un objeto `PolarsData` (no una Serie) a los lambdas de `Check`. Los checks con `element_wise=True` reciben valores individuales, lo que es más simple y directo.

**Criterio de bloqueo:** `main.py test` retorna exit code 1 si hay errores, lo que bloquea el `deploy` en pipelines CI/CD.

---

## 2026-06-29 — Sprint 5: Capa de Reportes

**Decisión:** Reemplazar `marimo export html` por generación directa de HTML estático desde Python.

**Contexto:** `marimo export html` genera una app WASM que requiere red para ejecutarse y no puede acceder a archivos locales en el browser. Para un reporte verdaderamente estático y offline-capable, los datos deben estar pre-computados y embebidos en el HTML. Se mantiene `marimo` como dependencia para exploración interactiva (`marimo edit`), pero el comando `deploy` genera HTML directamente.

---
