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

## 2026-06-29 — Sprint 6: Dominio de Campañas de Marketing

**Decisión:** Crear el dominio `campanas` completo: ETL, validación Pandera y reporte HTML.

**Contexto:** El cliente envió un archivo con columnas de campañas publicitarias (presupuesto, gasto, impresiones, clicks, conversiones, ingresos). Se modelaron 9 métricas derivadas: `estado`, `duracion_dias`, `ejecucion_presupuesto`, `ctr`, `tasa_conversion`, `cpc`, `cpa`, `roas`, `roi`.

**Canales válidos:** `email`, `redes_sociales`, `display`, `search`, `video`.

**Métricas clave calculadas en ETL:**
- ROAS = `ingresos_atribuidos / gasto_real` (nullable cuando gasto = 0)
- `estado` derivado de fechas vs. `date.today()` al momento de la carga

**Archivos creados:**
- `data/raw/campanas_demo.csv` — 8 campañas de muestra (5 finalizadas, 1 activa, 1 futura, 1 activa parcial)
- `memoria/metricas/campanas.md` — definiciones de negocio
- `pipelines/etl_campanas.py` — ETL con transformaciones completas
- `pipelines/calidad.py` — agregado `schema_campanas` con 20 columnas validadas
- `reports/campanas.py` — 4 secciones: KPIs, por canal, tabla completa, top ROAS

---

## 2026-06-29 — Sprint 7: Dominio de Devoluciones

**Decisión:** Crear el dominio `devoluciones` completo: ETL, validación Pandera y reporte HTML.

**Contexto:** El cliente envió `devoluciones_q3_2026.csv` con 12 columnas: id_devolucion, id_orden, fecha_devolucion, id_producto, nombre_producto, categoria, cantidad_devuelta, precio_unitario, motivo, estado, canal_devolucion, reembolso.

**Columnas derivadas calculadas en ETL:**
- `valor_devolucion = cantidad_devuelta * precio_unitario`
- `mes` — truncado al primer día del mes de `fecha_devolucion`

**Valores controlados:**
- Motivos: `defectuoso`, `incorrecto`, `no_satisface`, `talla_incorrecta`, `dano_envio`, `duplicado`, `otro`
- Estados: `aprobada`, `rechazada`, `pendiente`
- Canales: `online`, `tienda`, `marketplace`

**KPIs principales:**
- Tasa de aprobación = aprobadas / total * 100
- Reembolso total (solo aprobadas)
- Reembolso promedio (solo aprobadas)
- Evolución mensual de solicitudes

**Archivos creados:**
- `memoria/metricas/devoluciones.md` — definiciones de negocio
- `pipelines/etl_devoluciones.py` — ETL con 2 columnas derivadas
- `pipelines/calidad.py` — agregado `schema_devoluciones` con 14 columnas validadas
- `reports/devoluciones.py` — 6 secciones: KPIs, por motivo, por categoría, por canal, mensual, detalle

---

## 2026-06-30 — Sprint 8: Dominio de Envíos

**Decisión:** Crear el dominio `envios` completo: ETL, validación Pandera y reporte Streamlit.

**Contexto:** El cliente envió `envios_q3_2026.csv` con 11 columnas: id_envio, id_orden, fecha_despacho, fecha_entrega_estimada, fecha_entrega_real, courier, tipo_envio, costo_envio, region_destino, estado, peso_kg.

**Columnas derivadas calculadas en ETL:**
- `dias_retraso` — diferencia en días entre fecha_entrega_real y fecha_entrega_estimada (null para envíos en tránsito)
- `mes` — truncado al primer día del mes de `fecha_despacho`

**Valores controlados:**
- Couriers: `chilexpress`, `starken`, `bluexpress`, `correos`
- Tipos: `estandar`, `express`, `mismo_dia`
- Estados: `entregado`, `retrasado`, `en_transito`

**KPIs principales:**
- Tasa de entrega a tiempo = entregados / (entregados + retrasados) * 100
- Tasa de retraso = retrasados / (entregados + retrasados) * 100
- Costo total y promedio de envíos
- Días promedio de retraso (solo envíos retrasados)

**Archivos creados:**
- `data/raw/envios_q3_2026.csv` — 30 envíos Q3 2026 (archivo provisto por el cliente)
- `memoria/metricas/envios.md` — definiciones de negocio
- `pipelines/etl_envios.py` — ETL con 2 columnas derivadas
- `pipelines/calidad.py` — agregado `schema_envios` con 13 columnas validadas
- `reports/envios.py` — 4 secciones: KPIs, distribuciones, por región/tipo, evolución mensual
- `app.py` — registrada la página Envíos 🚚 en la navegación unificada

---

## 2026-06-29 — Sprint 5: Capa de Reportes

**Decisión:** Reemplazar `marimo export html` por generación directa de HTML estático desde Python.

**Contexto:** `marimo export html` genera una app WASM que requiere red para ejecutarse y no puede acceder a archivos locales en el browser. Para un reporte verdaderamente estático y offline-capable, los datos deben estar pre-computados y embebidos en el HTML. Se mantiene `marimo` como dependencia para exploración interactiva (`marimo edit`), pero el comando `deploy` genera HTML directamente.

---
