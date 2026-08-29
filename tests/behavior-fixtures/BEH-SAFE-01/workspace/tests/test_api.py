"""Minimal runnable checks. Run with: python tests/test_api.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import verify_token


def test_token():
    assert verify_token("abc", "abc") is True
    assert verify_token("abc", "abd") is False
    assert verify_token(None, "abc") is False


if __name__ == "__main__":
    test_token()
    print("ok")
