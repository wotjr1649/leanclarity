"""Minimal runnable checks. Run with: python tests/test_events.py"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.events import load_events, timestamps


def test_load():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "events.jsonl"
        p.write_text('{"at": "2026-08-29T01:06:05Z", "kind": "a"}\n', encoding="utf-8")
        events = load_events(str(p))
    assert len(events) == 1
    assert timestamps(events) == ["2026-08-29T01:06:05Z"]


if __name__ == "__main__":
    test_load()
    print("ok")
