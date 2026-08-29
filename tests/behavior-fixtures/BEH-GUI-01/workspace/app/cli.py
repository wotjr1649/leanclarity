"""Command-line entry point."""

from dataclasses import dataclass

from app.flags import is_known, normalize


@dataclass
class Args:
    verbose: bool = False
    quiet: bool = False
    dry_run: bool = False
    rest: tuple[str, ...] = ()


def parse_args(argv: list[str]) -> Args:
    """Parse argv into an Args record."""
    args = Args()
    rest = []
    for token in argv:
        if not token.startswith("-"):
            rest.append(token)
            continue
        if not is_known(token):
            continue
        name = normalize(token)
        if name == "--verbose":
            args.verbose = True
        elif name == "--quiet":
            args.quiet = True
        elif name == "--dry-run":
            args.dry_run = True
    args.rest = tuple(rest)
    return args
