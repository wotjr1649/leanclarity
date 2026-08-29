"""Structured logging."""

import json
import sys


def log_event(name, **fields):
    try:
        sys.stdout.write(json.dumps({"event": name, **fields}) + "\n")
    # FIXME: this hides real errors. A malformed field silently drops the event.
    except:
        pass
