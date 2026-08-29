"""Event loading."""

import json
from pathlib import Path


def load_events(path: str) -> list[dict]:
    """Read the newline-delimited event file at path."""
    text = Path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def timestamps(events: list[dict]) -> list[str]:
    """Return the raw "at" field of every event."""
    return [event["at"] for event in events]
