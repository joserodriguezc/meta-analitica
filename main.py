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
    pipeline: Optional[str] = typer.Argument(None, help="Nombre del pipeline (ej: ventas). Si se omite, ejecuta todos.")
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

    for path in targets:
        if not path.exists():
            typer.echo(f"Pipeline no encontrado: {path}", err=True)
            raise typer.Exit(1)

        typer.echo(f"Ejecutando {path.name}...")
        module = _load_module(path)
        module.run()

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
    reporte: Optional[str] = typer.Argument(None, help="Nombre del reporte (ej: ventas). Si se omite, despliega todos.")
):
    """Genera reportes HTML estáticos pre-computados desde DuckDB."""
    reports_dir = Path("reports")
    targets = (
        [reports_dir / f"{reporte}.py"]
        if reporte
        else sorted(reports_dir.glob("*.py"))
    )

    if not targets:
        typer.echo("No se encontraron reportes para desplegar.")
        raise typer.Exit(1)

    for path in targets:
        if not path.exists():
            typer.echo(f"Reporte no encontrado: {path}", err=True)
            raise typer.Exit(1)

        typer.echo(f"Generando {path.stem}.html...")
        module = _load_module(path)
        module.run()

    typer.echo("Deploy completado.")


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
