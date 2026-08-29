"""Background job queue with retries."""

import time

MAX_RETRIES = 3


class PermanentError(Exception):
    """Raised by a handler for a failure that is never worth retrying."""


def process(job, handler):
    """Run handler(job), retrying on failure.

    Returns the handler's result, or raises once the retries are exhausted.
    """
    attempt = 0
    while attempt <= MAX_RETRIES:
        try:
            return handler(job)
        except Exception:
            attempt += 1
            time.sleep(1)
    raise RuntimeError(f"job {job!r} failed after {attempt} attempts")


def drain(jobs, handler):
    """Process every job, collecting results and failures."""
    done, failed = [], []
    for job in jobs:
        try:
            done.append(process(job, handler))
        except RuntimeError as exc:
            failed.append((job, str(exc)))
    return done, failed
