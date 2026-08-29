"""Two caches sit in front of the pricing service."""

import json
import time
from pathlib import Path

from app.config import CACHE_TTL, DISK_CACHE_DIR

_MEMO: dict[str, tuple[float, dict]] = {}


def memo_get(key: str):
    """Return the in-process cached value for key, or None."""
    hit = _MEMO.get(key)
    if hit is None:
        return None
    stored_at, value = hit
    if time.time() - stored_at > CACHE_TTL:
        return None
    return value


def memo_put(key: str, value: dict) -> None:
    """Store value in the in-process cache."""
    _MEMO[key] = (time.time(), value)


class DiskCache:
    """A file-backed cache shared by every worker process."""

    def __init__(self, directory: str = DISK_CACHE_DIR):
        self.directory = Path(directory)

    def _path(self, key: str) -> Path:
        return self.directory / f"{key}.json"

    def get(self, key: str):
        """Return the cached value for key, or None."""
        path = self._path(key)
        if not path.is_file():
            return None
        if time.time() - path.stat().st_mtime > CACHE_TTL:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, value: dict) -> None:
        """Store value on disk."""
        self.directory.mkdir(parents=True, exist_ok=True)
        self._path(key).write_text(json.dumps(value), encoding="utf-8")
