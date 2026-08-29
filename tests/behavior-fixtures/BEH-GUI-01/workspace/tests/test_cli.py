"""Minimal runnable checks. Run with: python tests/test_cli.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.cli import parse_args


def test_rest():
    assert parse_args(["build", "x"]).rest == ("build", "x")


if __name__ == "__main__":
    test_rest()
    print("ok")
