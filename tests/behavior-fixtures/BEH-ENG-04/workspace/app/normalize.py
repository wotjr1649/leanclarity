"""Canonical form for user-supplied keys.

Every module that turns a human-typed string into a stored key goes through
normalize_key, so the search index, the tag table and the index builder all
agree on what a key looks like.
"""


def normalize_key(value):
    """Canonical key: lowercase, spaces become dashes."""
    return str(value).lower().replace(" ", "-")
