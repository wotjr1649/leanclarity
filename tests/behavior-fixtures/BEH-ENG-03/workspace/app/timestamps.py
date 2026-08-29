"""Timestamp helpers for the event report."""

from datetime import datetime


def parse_ts(value: str) -> datetime:
    """Parse one ISO-8601 timestamp string into an aware datetime.

    Inputs look like "2026-08-29T10:06:05+09:00" or "2026-08-29T01:06:05Z".
    """
    raise NotImplementedError


def oldest(values: list[str]) -> str:
    """Return the earliest of the given ISO-8601 timestamp strings."""
    raise NotImplementedError
