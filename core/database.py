"""
core/database.py
────────────────
SQLite connection management.
Provides a simple context manager and helper used by all db_tools.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from core.config import settings
from core.exceptions import DatabaseError


def get_db_path() -> str:
    path = Path(settings.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


@contextmanager
def get_connection():
    """
    Yields a SQLite connection with:
    - row_factory set to sqlite3.Row (column-name access)
    - WAL mode for concurrent reads
    - Foreign key enforcement
    """
    conn = None
    try:
        conn = sqlite3.connect(get_db_path(), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise DatabaseError(f"SQLite error: {e}") from e
    finally:
        if conn:
            conn.close()


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT and return all rows as list of dicts."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """Execute a SELECT and return the first row as a dict (or None)."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT/UPDATE/DELETE. Returns lastrowid."""
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        return cursor.lastrowid


def execute_many(sql: str, params_list: list[tuple]) -> None:
    """Execute an INSERT for multiple rows."""
    with get_connection() as conn:
        conn.executemany(sql, params_list)