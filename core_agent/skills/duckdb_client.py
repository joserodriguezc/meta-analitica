import duckdb
import polars as pl
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path("data/local.duckdb")


@contextmanager
def connection(read_only: bool = False):
    """Context manager que abre y cierra la conexión a DuckDB."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH), read_only=read_only)
    try:
        yield conn
    finally:
        conn.close()


def query(sql: str) -> pl.DataFrame:
    """Ejecuta una query SQL y retorna un DataFrame Polars."""
    with connection(read_only=True) as conn:
        return conn.execute(sql).pl()


def load_table(df: pl.DataFrame, table_name: str, replace: bool = True) -> int:
    """Carga un DataFrame Polars en DuckDB. Retorna la cantidad de filas cargadas."""
    with connection() as conn:
        if replace:
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
        else:
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
    return len(df)


def table_exists(table_name: str) -> bool:
    """Verifica si una tabla existe en DuckDB."""
    with connection(read_only=True) as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [table_name],
        ).fetchone()
        return result[0] > 0


def list_tables() -> list[str]:
    """Lista todas las tablas disponibles en DuckDB."""
    with connection(read_only=True) as conn:
        rows = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main' ORDER BY 1"
        ).fetchall()
        return [row[0] for row in rows]


def row_count(table_name: str) -> int:
    """Retorna la cantidad de filas de una tabla."""
    with connection(read_only=True) as conn:
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return result[0]
