"""Minimal runnable checks. Run with: python tests/test_handlers.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.handlers import handle_create
from app.util import rows


def test_create():
    new_id = handle_create({"name": "alpha", "amount": 10.0})
    assert new_id == 1
    assert rows() == [(1, "alpha", 10.0)]


if __name__ == "__main__":
    test_create()
    print("ok")
