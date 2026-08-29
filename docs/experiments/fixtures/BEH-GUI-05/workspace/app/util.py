"""In-memory stand-in for the record store."""

import sqlite3

_CONN = None


def conn() -> sqlite3.Connection:
    """Return the process-wide SQLite connection."""
    global _CONN
    if _CONN is None:
        _CONN = sqlite3.connect(":memory:")
        _CONN.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, name TEXT, amount REAL)")
    return _CONN


def rows() -> list[tuple]:
    """Return every record as a tuple row."""
    return conn().execute("SELECT id, name, amount FROM records ORDER BY id").fetchall()
