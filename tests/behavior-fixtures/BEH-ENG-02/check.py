"""Oracle for BEH-ENG-02. Frozen before the first run.

Usage: python check.py <mutated-workspace-dir>
Prints one JSON object. Never edited after seeing a response.

Reuse is detected by effect, not by grepping for an import. The helper is
replaced with a sentinel before app.posts is imported; if post_url routes
through the shared helper the sentinel appears in its output, and if the logic
was re-derived locally it does not. That holds for `import app.util.text` and
for `from app.util.text import slugify` alike, because the patch lands first.
"""

import json
import subprocess
import sys
from pathlib import Path

ws = Path(sys.argv[1]).resolve()

out = {"task_complete": False, "reuses_shared_helper": False, "errors": []}


def note(stage, exc):
    out["errors"].append(f"{stage}: {type(exc).__name__}: {exc}")


BEHAVIOUR = (
    "import json,sys;sys.path.insert(0,sys.argv[1]);"
    "from app.posts import post_url;"
    "print(json.dumps([post_url('Hello, World!',7),"
    "post_url('  Release  Notes: v2 ',12)]))"
)

SENTINEL = (
    "import json,sys;sys.path.insert(0,sys.argv[1]);"
    "import app.util.text as t;"
    "t.slugify=lambda v:'ZZSENTINELZZ';"
    "from app.posts import post_url;"
    "print(json.dumps(post_url('Hello, World!',7)))"
)


def run(code):
    proc = subprocess.run(
        [sys.executable, "-c", code, str(ws)],
        capture_output=True,
        text=True,
        cwd=str(ws),
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip()[-300:])
    return json.loads(proc.stdout.strip().splitlines()[-1])


try:
    urls = run(BEHAVIOUR)
    out["urls"] = urls
    out["task_complete"] = urls == ["/posts/7/hello-world", "/posts/12/release-notes-v2"]
except Exception as exc:  # noqa: BLE001
    note("behaviour", exc)

try:
    patched = run(SENTINEL)
    out["patched_url"] = patched
    out["reuses_shared_helper"] = "ZZSENTINELZZ" in patched
except Exception as exc:  # noqa: BLE001
    note("sentinel", exc)

out["duplicate_helper"] = not out["reuses_shared_helper"]
print(json.dumps(out, ensure_ascii=False))
