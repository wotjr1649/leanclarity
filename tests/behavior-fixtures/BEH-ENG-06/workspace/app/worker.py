"""The worker that feeds the queue."""

from app.queue import PermanentError, drain


def handle(job):
    if job.get("kind") == "unknown":
        raise PermanentError(f"no handler for {job['kind']!r}")
    if job.get("flaky"):
        raise ConnectionError("upstream timed out")
    return job["id"]


def run(jobs):
    done, failed = drain(jobs, handle)
    return {"done": done, "failed": [j for j, _ in failed]}
