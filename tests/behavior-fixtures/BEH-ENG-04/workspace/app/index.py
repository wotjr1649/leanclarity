"""Index building."""

from app.normalize import normalize_key


def build_index(titles):
    """Map each title to its canonical key."""
    return {normalize_key(t): t for t in titles}
