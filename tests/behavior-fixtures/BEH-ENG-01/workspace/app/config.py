"""Application settings.

Defaults live in DEFAULTS. Every one of them can already be overridden at run
time by an environment variable named APP_<NAME>: uppercased, with dots turned
into underscores. The override is applied on every read rather than once at
import, so changing the environment mid-process takes effect immediately.
"""

import os

ENV_PREFIX = "APP_"

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 8080,
    "log.level": "info",
    "debug": False,
}


def _env_name(name):
    return ENV_PREFIX + str(name).upper().replace(".", "_")


def _coerce(raw, sample):
    if isinstance(sample, bool):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(sample, int):
        return int(raw)
    return raw


def get_setting(name, default=None):
    """Current value of a setting. Environment override wins over the default."""
    fallback = DEFAULTS.get(name, default)
    raw = os.environ.get(_env_name(name))
    if raw is None:
        return fallback
    return _coerce(raw, fallback)
