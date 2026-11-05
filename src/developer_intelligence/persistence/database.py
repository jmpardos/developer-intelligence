import sqlite3
from contextlib import closing
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def initialize_database(database_path: str | Path) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    
    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(schema)