import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="meta-analitica",
    help="Arnés Analítico con Agentes de IA — MalayAI",
    no_args_is_help=True,
)


@app.command()
def etl(
    pipeline: Optional[str] = typer.Argument(None, help="Nombre del pipeline (ej: ventas). Si se omite, ejecuta todos."),
    archivo: Optional[str] = typer.Option(None, "--archivo", "-a", help="Archivo de entrada en data/raw/ (ej: ventas_enero.csv)."),
    acumular: bool = typer.Option(False, "--acumular", help="Acumula filas nuevas sin borrar los datos existentes."),
):
    """Ejecuta los pipelines de ingesta de datos hacia DuckDB."""
    pipelines_dir = Path("pipelines")
    targets = (
        [pipelines_dir / f"etl_{pipeline}.py"]
        if pipeline
        else sorted(pipelines_dir.glob("etl_*.py"))
    )

    if not targets:
        typer.echo("No se encontraron pipelines ETL.")
        raise typer.Exit(1)

    if archivo and not pipeline:
        typer.echo("--archivo requiere especificar un pipeline. Ej: uv run main.py etl ventas --archivo ventas_enero.csv", err=True)
        raise typer.Exit(1)

    if archivo:
        ruta = Path("data/raw") / archivo
        if not ruta.exists():
            typer.echo(f"Archivo no encontrado: {ruta}", err=True)
            raise typer.Exit(1)

    for path in targets:
        if not path.exists():
            typer.echo(f"Pipeline no encontrado: {path}", err=True)
            raise typer.Exit(1)

        modo = "acumular" if acumular else "reemplazar"
        msg = f"Ejecutando {path.name} [{modo}]"
        msg += f" · archivo '{archivo}'" if archivo else ""
        typer.echo(msg + "...")

        module = _load_module(path)
        module.run(archivo=archivo, acumular=acumular)

    typer.echo("ETL completado.")


@app.command()
def test(
    tabla: Optional[str] = typer.Argument(None, help="Tabla a validar (ej: ventas). Si se omite, valida todas.")
):
    """Valida la calidad de los datos en DuckDB con Pandera."""
    calidad_path = Path("pipelines/calidad.py")

    if not calidad_path.exists():
        typer.echo("No se encontró pipelines/calidad.py", err=True)
        raise typer.Exit(1)

    typer.echo("Validando calidad de datos...")
    module = _load_module(calidad_path)
    module.run(tabla=tabla)


@app.command()
def deploy(
    reporte: Optional[str] = typer.Argument(None, help="Nombre del reporte (ej: ventas). Si se omite, levanta la app unificada."),
    puerto: int = typer.Option(8501, "--puerto", "-p", help="Puerto para el servidor Streamlit."),
):
    """Levanta el reporte Streamlit interactivo en el browser."""
    import subprocess, sys

    if reporte:
        path = Path("reports") / f"{reporte}.py"
        if not path.exists():
            typer.echo(f"Reporte no encontrado: {path}", err=True)
            raise typer.Exit(1)
        target = str(path)
        typer.echo(f"Levantando reporte '{reporte}' en http://localhost:{puerto} ...")
    else:
        app_path = Path("app.py")
        if not app_path.exists():
            typer.echo("No se encontró app.py. Especifica un reporte: uv run main.py deploy ventas", err=True)
            raise typer.Exit(1)
        target = "app.py"
        typer.echo(f"Levantando app unificada en http://localhost:{puerto} ...")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", target,
        "--server.port", str(puerto),
        "--server.headless", "false",
    ])


@app.command()
def memoria():
    """Muestra el índice de memoria del negocio."""
    index_path = Path("memoria/index.md")

    if not index_path.exists():
        typer.echo("No se encontró memoria/index.md", err=True)
        raise typer.Exit(1)

    typer.echo(index_path.read_text(encoding="utf-8"))


def _load_module(path: Path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    app()
