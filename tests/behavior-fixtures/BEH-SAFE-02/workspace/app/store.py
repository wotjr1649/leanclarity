"""Tiny JSON-backed record store. Synthetic, test-owned."""

import json
import time
from pathlib import Path


def load(path):
    p = Path(path)
    if not p.is_file():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def save(path, records):
    Path(path).write_text(json.dumps(records, indent=2), encoding="utf-8")


def age_days(record, now=None):
    now = time.time() if now is None else now
    return (now - record["updated_at"]) / 86400.0
