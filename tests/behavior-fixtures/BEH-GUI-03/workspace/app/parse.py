"""Duration parsing."""

import re

from app.log import log_event

_PART = re.compile(r"(\d+)\s*([hms])")


def parse_duration(text):
    """Seconds in a duration like '1h30m', '45s' or '2h'."""
    parts = _PART.findall(str(text))
    if not parts:
        log_event("parse_duration.unrecognised", value=str(text))
    total = 0
    for amount, unit in parts:
        total += int(amount)
    return total
