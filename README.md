# meta-analitica

**Arnés Analítico con Agentes de IA — PoC MalayAI Lab**

Plataforma analítica basada en el paradigma de *Harness Engineering*. En lugar de construir un agente conversacional propio, el proyecto provee una infraestructura controlada (CLI + DuckDB + dashboards Streamlit) que permite a herramientas de IA existentes (Claude Code, Copilot, Cursor) operar sobre datos y reglas de negocio de forma auditable. El humano actúa como supervisor y aprobador.

---

## Flujo de Trabajo

```
[ CSV del cliente ] → [ etl ] → [ test ] → [ deploy ] → [ Dashboard Streamlit ]
         ↑                                                         ↑
   data/raw/               IA opera el arnés              Browser interactivo
```

### Comandos

```bash
uv run main.py etl                          # Ingesta todos los dominios → DuckDB
uv run main.py etl ventas                   # Solo el pipeline de ventas
uv run main.py etl ventas --archivo ventas_enero.csv   # Archivo específico
uv run main.py etl ventas --acumular        # Modo incremental (no reemplaza)

uv run main.py test                         # Valida todos los dominios con Pandera
uv run main.py test ventas                  # Solo valida la tabla ventas

uv run main.py deploy                       # Levanta la app unificada (4 dominios)
uv run main.py deploy ventas                # Solo el reporte de ventas
uv run main.py deploy --puerto 8502         # Puerto personalizado

uv run main.py memoria                      # Muestra el índice de conocimiento de negocio
```

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| CLI / Orquestación | Python + Typer |
| Motor analítico | DuckDB (in-process) |
| Transformaciones | Polars |
| Validación de datos | Pandera |
| Reportes interactivos | Streamlit + Plotly |
| Gestión de dependencias | uv |

---

## Dominios Analíticos

| Dominio | Tabla DuckDB | Reporte | KPIs principales |
|---|---|---|---|
| Ventas | `ventas` | `reports/ventas.py` | Ingresos, ticket promedio, órdenes |
| Inventario | `inventario` | `reports/inventario.py` | Valor stock, margen, quiebre |
| Campañas | `campanas` | `reports/campanas.py` | ROAS, ROI, CTR, CPC, CPA |
| Devoluciones | `devoluciones` | `reports/devoluciones.py` | Tasa aprobación, reembolso |
| Envíos | `envios` | `reports/envios.py` | Tasa entrega a tiempo, retrasos, costo courier |

---

## Estructura del Proyecto

```
meta-analitica/
├── CLAUDE.md                  ← Harness context para el agente de IA
├── app.py                     ← App Streamlit unificada (4 dominios)
├── assets/
│   └── malayai_logo.png       ← Logo para el sidebar de reportes
├── memoria/                   ← Conocimiento del negocio (leer antes de codear)
│   ├── index.md               ← Mapa de memoria
│   ├── log.md                 ← Bitácora de decisiones
│   ├── metricas/              ← Definiciones de KPIs por dominio
│   └── clientes/              ← Perfil y requerimientos por cliente
├── core_agent/
│   ├── skills/                ← Herramientas reutilizables
│   │   ├── duckdb_client.py   ← Wrapper DuckDB (query, load, append)
│   │   └── chart_builder.py   ← Helpers Plotly + CSS premium MalayAI
│   └── tasks/                 ← Recetas paso a paso para el agente
├── pipelines/
│   ├── etl_ventas.py
│   ├── etl_inventario.py
│   ├── etl_campanas.py
│   ├── etl_devoluciones.py
│   ├── etl_envios.py
│   └── calidad.py             ← Schemas Pandera para todos los dominios
├── reports/
│   ├── ventas.py
│   ├── inventario.py
│   ├── campanas.py
│   ├── devoluciones.py
│   └── envios.py
├── data/
│   ├── raw/                   ← Archivos CSV de entrada (solo lectura)
│   └── local.duckdb           ← Almacén analítico (generado, en .gitignore)
└── main.py                    ← Punto de entrada CLI
```

---

## Instalación

```bash
# Requiere uv — https://docs.astral.sh/uv/
git clone https://github.com/joserodriguezc/meta-analitica
cd meta-analitica
uv sync
```

## Demo rápida

```bash
# 1. Cargar datos de los 4 dominios
uv run main.py etl ventas      --archivo ventas_demo.csv
uv run main.py etl inventario  --archivo inventario_agosto.csv
uv run main.py etl campanas    --archivo campanas_q3_2026.csv
uv run main.py etl devoluciones --archivo devoluciones_q3_2026.csv

# 2. Validar calidad (bloquea si hay errores)
uv run main.py test

# 3. Levantar la app interactiva
uv run main.py deploy
# → Abre http://localhost:8501 con los 4 dashboards
```

---

## Cómo agregar un nuevo dominio analítico

Usar este prompt con Claude Code (u otro agente):

```
El cliente mandó <archivo.csv> con columnas <col1, col2, ...>.

Crea el dominio de <nombre> siguiendo las reglas del harness:
1. Lee CLAUDE.md y memoria/index.md antes de escribir cualquier código
2. Crea memoria/metricas/<dominio>.md con esquema, KPIs y reglas de negocio
3. Crea pipelines/etl_<dominio>.py siguiendo core_agent/tasks/crear_etl.md
4. Agrega schema_<dominio> en pipelines/calidad.py
5. Crea reports/<dominio>.py como app Streamlit con chart_builder
6. Actualiza memoria/index.md
7. Verifica: uv run main.py etl <dominio> --archivo <archivo.csv> &&
             uv run main.py test <dominio> &&
             uv run main.py deploy <dominio>
```

El agente no termina hasta que el flujo pase limpio.

---

## Principios del Arnés

- **Agnóstico del LLM:** No construye su propio agente. Delega al IDE/terminal.
- **Agents-as-Code:** Las reglas del agente viven en `.md` versionados en Git.
- **Memoria transparente:** El contexto de negocio está en `memoria/`, legible por humanos e IA.
- **Calidad como bloqueo:** `test` falla con exit code 1 si hay errores — no hay deploy sin datos limpios.
- **Infraestructura ligera:** DuckDB in-process + Streamlit local, sin servidores ni cloud.

---

*MalayAI Lab — 2026*
