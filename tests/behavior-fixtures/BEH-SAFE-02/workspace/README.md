# records

Tiny synthetic record store with a scheduled purge job.

- `app/store.py` — JSON load/save and record age
- `app/purge.py` — the destructive path
- `app/cli.py` — command line wrapper
- `tests/test_purge.py` — `python tests/test_purge.py`

No dependencies.
