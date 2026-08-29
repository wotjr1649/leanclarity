"""Command line entry point for the purge job."""

import argparse
import sys

from app.purge import PurgeRefused, purge_records


def main(argv=None):
    parser = argparse.ArgumentParser(prog="purge")
    parser.add_argument("path")
    parser.add_argument("--older-than-days", type=int, required=True)
    parser.add_argument("--apply", action="store_true", help="actually delete")
    parser.add_argument("--allow-full", action="store_true")
    args = parser.parse_args(argv)

    try:
        removed = purge_records(
            args.path,
            args.older_than_days,
            dry_run=not args.apply,
            allow_full=args.allow_full,
        )
    except PurgeRefused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2

    verb = "deleted" if args.apply else "would delete"
    print(f"{verb} {len(removed)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
