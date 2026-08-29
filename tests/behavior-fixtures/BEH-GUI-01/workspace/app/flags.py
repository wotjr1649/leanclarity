"""Flag token helpers shared by the CLI and the config loader."""

KNOWN = ("--verbose", "--quiet", "--dry-run")


def normalize(token: str) -> str:
    """Return a comparable form of one command-line token."""
    return token.strip().lstrip("-").lower()


def is_known(token: str) -> bool:
    """Return True when token names a flag this program understands."""
    return normalize(token) in KNOWN
