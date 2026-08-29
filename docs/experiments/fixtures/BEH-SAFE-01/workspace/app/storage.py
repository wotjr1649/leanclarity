"""Storage for user-uploaded documents."""

from pathlib import Path

MAX_BYTES = 2 * 1024 * 1024


class StorageError(Exception):
    """Raised when a request cannot be served safely."""


def read_user_file(base_dir: str, user_path: str) -> bytes:
    """Return the bytes of user_path resolved inside base_dir.

    user_path arrives from an HTTP query string and is untrusted input.
    """
    base = Path(base_dir).resolve(strict=True)
    candidate = (base / user_path).resolve()

    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise StorageError("path escapes the storage root") from exc

    if not candidate.is_file():
        raise StorageError("not a regular file")

    if candidate.stat().st_size > MAX_BYTES:
        raise StorageError("file exceeds the response size limit")

    with candidate.open("rb") as handle:
        return handle.read(MAX_BYTES)
