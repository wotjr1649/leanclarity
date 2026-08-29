# svc

Small service skeleton. Stdlib only.

- `app/config.py` — settings, with environment overrides
- `app/main.py` — entry point
- `tests/test_config.py` — `python tests/test_config.py`

## Configuration

Defaults are in `app.config.DEFAULTS`. Any setting can be overridden at run
time with `APP_<NAME>`, uppercased and with dots replaced by underscores:

```
APP_PORT=9001 python -m app.main
APP_LOG_LEVEL=debug python -m app.main
```

No dependencies.
