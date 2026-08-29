"""Run with: python tests/test_config.py"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_setting


def test_default():
    os.environ.pop("APP_PORT", None)
    assert get_setting("port") == 8080


def test_env_override():
    os.environ["APP_PORT"] = "9001"
    try:
        assert get_setting("port") == 9001
    finally:
        del os.environ["APP_PORT"]


if __name__ == "__main__":
    test_default()
    test_env_override()
    print("ok")
