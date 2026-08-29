"""Event report."""

from app.events import load_events


def render(path: str) -> str:
    events = load_events(path)
    lines = [f"{len(events)} events"]
    # TODO: print the oldest event time here, formatted as the raw timestamp string.
    return "\n".join(lines)
