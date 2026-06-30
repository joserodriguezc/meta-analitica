# meta-analitica

**Arnés Analítico con Agentes de IA — PoC MalayAI**

Plataforma analítica basada en el paradigma de *Harness Engineering*. En lugar de construir un agente conversacional propio, el proyecto provee una infraestructura controlada (CLI + DuckDB + reportes HTML) que permite a herramientas de IA existentes (Claude Code, Copilot, Cursor) operar sobre datos y reglas de negocio de forma auditable.

---

## Flujo de Trabajo

```
[ REQUERIMIENTO ] → [ INGENIERO + IA ] → [ etl ] → [ test ] → [ deploy ] → [ REPORTE HTML ]
```

### Comandos

```bash
uv run main.py etl       # Ingesta datos CSV → DuckDB
uv run main.py test      # Valida calidad con Pandera (bloquea si hay errores)
uv run main.py deploy    # Genera reporte HTML estático desde DuckDB
uv run main.py memoria   # Muestra el índice de conocimiento de negocio
```

Todos los comandos aceptan un argumento opcional para operar sobre un dominio específico:

```bash
uv run main.py etl ventas       # Solo ejecuta etl_ventas.py
uv run main.py test ventas      # Solo valida la tabla ventas
uv run main.py deploy ventas    # Solo genera reports/ventas.html
```

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| CLI / Orquestación | Python + Typer |
| Motor analítico | DuckDB (in-process) |
| Transformaciones | Polars |
| Validación de datos | Pandera |
| Reportes | HTML estático generado con Python |
| Gestión de dependencias | uv |

---

## Estructura del Proyecto

```
meta-analitica/
├── CLAUDE.md                  ← Harness context para el agente de IA
├── memoria/                   ← Conocimiento del negocio (leer antes de codear)
│   ├── index.md               ← Mapa de memoria
│   ├── log.md                 ← Bitácora de decisiones
│   ├── metricas/              ← Definiciones de KPIs y esquemas
│   └── clientes/              ← Perfil y requerimientos por cliente
├── core_agent/
│   ├── skills/                ← Herramientas reutilizables (DuckDB, report builder)
│   └── tasks/                 ← Recetas paso a paso para el agente
├── pipelines/                 ← Scripts ETL y validaciones
├── reports/                   ← Scripts de reportes → genera .html
├── data/
│   ├── raw/                   ← Archivos CSV/JSON de entrada
│   └── local.duckdb           ← Almacén analítico (generado, en .gitignore)
└── main.py                    ← Punto de entrada CLI
```

---

## Instalación

```bash
# Requiere uv — https://docs.astral.sh/uv/
git clone <repo>
cd meta-analitica
uv sync
```

## Demo rápida

```bash
uv run main.py etl      # Carga ventas_demo.csv → DuckDB
uv run main.py test     # Valida: 90 filas OK
uv run main.py deploy   # Genera reports/ventas.html
```

Abrir `reports/ventas.html` en cualquier navegador.

---

## Cómo agregar un nuevo dominio analítico

El agente de IA (Claude Code) puede hacer esto en un solo prompt. El flujo es:

1. Leer `memoria/index.md` → identificar el dominio
2. Leer `core_agent/tasks/crear_etl.md` → crear `pipelines/etl_<dominio>.py`
3. Leer `core_agent/tasks/validar_calidad.md` → agregar esquema en `pipelines/calidad.py`
4. Leer `core_agent/tasks/crear_reporte.md` → crear `reports/<dominio>.py`
5. Ejecutar `uv run main.py etl && uv run main.py test && uv run main.py deploy`

---

## Principios del Arnés

- **Agnóstico del arnés:** No construye su propio agente. Delega al IDE/terminal.
- **Agents-as-Code:** Las reglas del agente viven en `.md` versionados en Git.
- **Memoria transparente:** El contexto de negocio está en `memoria/`, legible por humanos e IA.
- **Infraestructura ligera:** DuckDB in-process + HTML estático, sin servidores.

---

*MalayAI — 2026*
