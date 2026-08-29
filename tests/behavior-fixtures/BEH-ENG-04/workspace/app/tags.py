"""Tag display names."""

from app.normalize import normalize_key

TAGS = {"foo-bar": "Foo Bar", "baz-qux": "Baz Qux", "zed": "Zed"}


def tag_label(raw):
    """Display name for a user-typed tag, or None."""
    return TAGS.get(normalize_key(raw))
