# catalog

Record search over a small tag catalog. Stdlib only.

- `app/normalize.py` — canonical key form, shared by everything below
- `app/search.py` — record search
- `app/tags.py` — tag display names
- `app/index.py` — index building
- `tests/test_normalize.py` — `python tests/test_normalize.py`

Anything that turns a human-typed string into a stored key goes through
`app.normalize.normalize_key`.

No dependencies.
