# pricing

Price lookup with two caches in front of the upstream service. Python 3.12+.

- `app/store.py` — the in-process memo cache and the file-backed `DiskCache`
- `app/api.py` — `fetch_price` consults both
- `app/config.py` — `CACHE_TTL` is shared by both caches

Run the checks with `python tests/test_store.py`.
