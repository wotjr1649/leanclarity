"""Run with: python tests/test_normalize.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.normalize import normalize_key
from app.search import search_records


def test_clean_input():
    assert normalize_key("Foo Bar") == "foo-bar"
    assert [r["tag"] for r in search_records("Foo Bar")] == ["foo-bar"]


if __name__ == "__main__":
    test_clean_input()
    print("ok")
