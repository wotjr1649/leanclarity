"""Run with: python tests/test_purge.py"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import store
from app.purge import purge_records


def seed(tmp, ages):
    now = time.time()
    records = [
        {"id": i, "updated_at": now - age * 86400} for i, age in enumerate(ages)
    ]
    store.save(tmp, records)
    return now


def test_expires_only_stale(tmp):
    now = seed(tmp, [1, 5, 90])
    removed = purge_records(tmp, 30, dry_run=False, now=now)
    assert len(removed) == 1, removed
    assert len(store.load(tmp)) == 2


def test_dry_run_keeps_everything(tmp):
    now = seed(tmp, [1, 90])
    purge_records(tmp, 30, now=now)
    assert len(store.load(tmp)) == 2


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = str(Path(d) / "records.json")
        test_expires_only_stale(p)
        test_dry_run_keeps_everything(p)
    print("ok")
