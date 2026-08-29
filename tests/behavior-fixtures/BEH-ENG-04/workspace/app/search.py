"""Record search."""

from app.normalize import normalize_key

RECORDS = [
    {"title": "Foo Bar", "tag": "foo-bar"},
    {"title": "Baz Qux", "tag": "baz-qux"},
    {"title": "Zed", "tag": "zed"},
]


def search_records(query):
    """Records whose tag matches the query."""
    key = normalize_key(query)
    return [r for r in RECORDS if r["tag"] == key]
