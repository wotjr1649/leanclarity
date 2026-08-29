"""Download endpoint wiring."""

from app.auth import AuthError, verify_token
from app.storage import StorageError, read_user_file

STORAGE_ROOT = "./var/documents"


def download(request_headers: dict, query: dict, expected_token: str) -> tuple[int, bytes]:
    """Serve one document. Returns an (http_status, body) pair."""
    if not verify_token(request_headers.get("x-token", ""), expected_token):
        raise AuthError("bad token")

    try:
        body = read_user_file(STORAGE_ROOT, query.get("path", ""))
    except StorageError:
        return 400, b""
    except FileNotFoundError:
        return 404, b""
    return 200, body
