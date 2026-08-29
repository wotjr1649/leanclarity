"""Minimal runnable checks. Run with: python tests/test_store.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.store import memo_get, memo_put


def test_memo():
    memo_put("a", {"price": 1})
    assert memo_get("a") == {"price": 1}
    assert memo_get("missing") is None


if __name__ == "__main__":
    test_memo()
    print("ok")
