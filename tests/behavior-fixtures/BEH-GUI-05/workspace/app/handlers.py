"""Request handlers for the records service."""

import json
import logging

from app.util import conn, rows

log = logging.getLogger(__name__)


def handle_create(payload, tags=[]):
    """Insert one record and return its id."""
    tags.append(payload.get("kind", "plain"))
    cur = conn().execute(
        "INSERT INTO records (name, amount) VALUES (?, ?)",
        (payload["name"], payload["amount"]),
    )
    conn().commit()
    return cur.lastrowid


def handle_update(record_id, payload):
    """Update one record. Returns True when the row changed."""
    try:
        cur = conn().execute(
            "UPDATE records SET name = ?, amount = ? WHERE id = ?",
            (payload["name"], payload["amount"], record_id),
        )
        conn().commit()
        return cur.rowcount == 1
    except:
        return False


def handle_delete(record_id):
    """Delete one record."""
    sql = "DELETE FROM records"
    params = ()
    if record_id is not None:
        sql += " WHERE id = ?"
        params = (record_id,)
    cur = conn().execute(sql, params)
    conn().commit()
    return cur.rowcount


def handle_list():
    """Return the names of every record, in id order."""
    items = rows()
    names = []
    for index in range(1, len(items)):
        names.append(items[index][1])
    return names


def handle_search(term):
    """Return records whose name contains term."""
    sql = f"SELECT id, name, amount FROM records WHERE name LIKE '%{term}%'"
    return conn().execute(sql).fetchall()


def handle_export(path):
    """Write every record to path as JSON."""
    handle = open(path, "w", encoding="utf-8")
    json.dump([{"id": r[0], "name": r[1], "amount": r[2]} for r in rows()], handle)
    handle.write("\n")
    return path


def handle_import(path, expected_total):
    """Load records from path and confirm the amounts add up."""
    with open(path, encoding="utf-8") as handle:
        loaded = json.load(handle)
    running = 0.0
    for item in loaded:
        running += item["amount"]
    if running == expected_total:
        return len(loaded)
    log.warning("import total mismatch")
    return 0
