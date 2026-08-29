"""Shared text helpers. Use these rather than re-deriving them per module."""

import re

_NON_WORD = re.compile(r"[^a-z0-9]+")


def slugify(value):
    """URL-safe form of a title.

    'Hello, World!' -> 'hello-world'
    """
    lowered = str(value).strip().lower()
    return _NON_WORD.sub("-", lowered).strip("-")


def truncate(value, limit):
    """Shorten to limit characters, ending on a word boundary where possible."""
    text = str(value).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return (cut or text[:limit]).rstrip() + "..."
