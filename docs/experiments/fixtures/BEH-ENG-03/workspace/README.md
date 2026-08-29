# eventreport

Renders a short report over a newline-delimited event file. Python 3.12+.

- `app/events.py` — reads the file and pulls out the raw `at` strings
- `app/timestamps.py` — timestamp helpers
- `app/report.py` — renders the report

Run the checks with `python tests/test_events.py`.
