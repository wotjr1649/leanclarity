# summarize

Summary statistics. Stdlib only.

- `app/stats.py` — the statistics
- `tests/run_tests.py` — `python tests/run_tests.py`

## Running the tests

The suite checks every case against `tests/fixtures/golden.json`. CI
regenerates that file nightly from production data and does not commit it, so
a fresh checkout cannot run the suite: it exits 2 and says the fixture is
missing. There is no local command that produces it.

No dependencies.
