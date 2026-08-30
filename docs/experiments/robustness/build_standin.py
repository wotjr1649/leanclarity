"""Build the stand-in instruction file from the two pinned upstream SKILL.md bodies.

Byte-exact and reproducible: frontmatter is stripped the same way each upstream's
own SessionStart hook strips it, nothing else is edited, and the result is hashed.
The study needs a constant, not a plugin whose injected bytes depend on a persisted
mode (ponytail) or an opt-in flag file (i-have-adhd).

Usage: python docs/experiments/robustness/build_standin.py
Writes docs/experiments/robustness/standin.md and prints its SHA-256.
"""
import hashlib
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "standin.md"

SOURCES = [
    ("ponytail", Path("D:/AI_DEV/_refs/ponytail/skills/ponytail/SKILL.md"),
     "2ed6c52c9d7e5e56942508591085fd45dea277d3"),
    ("i-have-adhd", Path("D:/AI_DEV/_refs/i-have-adhd/skills/i-have-adhd/SKILL.md"),
     "cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c"),
]

# Same expression i-have-adhd's always-on.mjs uses, which is the stricter of the two.
FRONTMATTER = re.compile(r"^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)")


def body_of(path: Path) -> str:
    raw = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    return FRONTMATTER.sub("", raw).strip("\n")


def main() -> None:
    parts = []
    for name, path, rev in SOURCES:
        body = body_of(path)
        parts.append(body)
        print(f"{name:<12} {rev[:8]}  body {len(body)} chars  "
              f"first={body.splitlines()[0][:40]!r}  last={body.splitlines()[-1][:40]!r}")
    text = "\n\n".join(parts) + "\n"
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    print(f"\nstand-in {len(text)} chars  SHA-256 {digest}")
    print(f"written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
