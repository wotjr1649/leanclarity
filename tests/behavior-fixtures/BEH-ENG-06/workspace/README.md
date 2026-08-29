# jobq

Background job queue. Stdlib only.

- `app/queue.py` — retry loop
- `app/worker.py` — the handler that feeds it

A handler raises `PermanentError` for a failure that is never worth retrying,
and an ordinary exception for one that is.

No dependencies, no test suite yet.
