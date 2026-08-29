"""Shared-secret check for the download endpoint."""

import hmac


class AuthError(Exception):
    """Raised when a caller is not authorized."""


def verify_token(provided: str, expected: str) -> bool:
    """Return True when provided matches expected.

    provided comes from a request header and is untrusted input.
    """
    if not isinstance(provided, str) or not isinstance(expected, str):
        return False
    return hmac.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))
