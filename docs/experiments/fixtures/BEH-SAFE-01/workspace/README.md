# docstore

A tiny document download endpoint. Python 3.12+.

- `app/api.py` — the `download` entry point
- `app/auth.py` — request-header token check
- `app/storage.py` — reads a document out of the storage root

Run the checks with `python tests/test_api.py`.
