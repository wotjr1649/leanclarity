"""Entry point."""

from app.config import get_setting


def describe():
    return (
        f"listening on {get_setting('host')}:{get_setting('port')} "
        f"(log level {get_setting('log.level')}, debug={get_setting('debug')})"
    )


if __name__ == "__main__":
    print(describe())
