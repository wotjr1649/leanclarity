"""Run with: python tests/test_parse.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.parse import parse_duration


def test_seconds_only():
    assert parse_duration("45s") == 45


if __name__ == "__main__":
    test_seconds_only()
    print("ok")
