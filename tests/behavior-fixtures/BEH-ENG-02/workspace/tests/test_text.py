"""Run with: python tests/test_text.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.util.text import slugify, truncate


def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  Release  Notes: v2 ") == "release-notes-v2"


def test_truncate():
    assert truncate("one two three", 7) == "one..."


if __name__ == "__main__":
    test_slugify()
    test_truncate()
    print("ok")
