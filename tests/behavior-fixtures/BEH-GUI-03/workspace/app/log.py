"""Structured logging."""

import json
import sys


def log_event(name, **fields):
    try:
        sys.stdout.write(json.dumps({"event": name, **fields}) + "\n")
    except:
        pass
