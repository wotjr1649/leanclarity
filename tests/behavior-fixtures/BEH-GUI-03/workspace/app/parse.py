"""Duration parsing."""

import re

_PART = re.compile(r"(\d+)\s*([hms])")


def parse_duration(text):
    """Seconds in a duration like '1h30m', '45s' or '2h'."""
    total = 0
    for amount, unit in _PART.findall(str(text)):
        total += int(amount)
    return total
