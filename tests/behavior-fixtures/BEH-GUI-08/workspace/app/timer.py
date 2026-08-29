"""Focus timer.

A session is a fixed block of working time. schedule() returns the blocks a
user is about to work through, in order.
"""

SESSION_MINUTES = 25


def start_session(minutes=SESSION_MINUTES):
    return {"kind": "focus", "minutes": minutes}


def schedule(count, minutes=SESSION_MINUTES):
    """The next `count` focus sessions, in order."""
    return [start_session(minutes) for _ in range(count)]
