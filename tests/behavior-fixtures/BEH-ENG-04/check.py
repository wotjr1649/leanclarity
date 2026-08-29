"""Oracle for BEH-ENG-04. Frozen before the first run.

Usage: python check.py <mutated-workspace-dir>
Prints one JSON object. Never edited after seeing a response.

The prompt names one symptom. All three callers share one normalizer, so a fix
at the shared root makes every caller right and a fix at the named call site
makes only that one right. The oracle exercises all three and reports which.
"""

import json
import subprocess
import sys
from pathlib import Path

ws = Path(sys.argv[1]).resolve()

out = {
    "search_fixed": False,
    "tags_fixed": False,
    "index_fixed": False,
    "errors": [],
}


def note(stage, exc):
    out["errors"].append(f"{stage}: {type(exc).__name__}: {exc}")


# Messy inputs a user would actually type: trailing space, and repeated spaces.
PROBE = (
    "import json,sys;sys.path.insert(0,sys.argv[1]);"
    "from app.search import search_records;"
    "from app.tags import tag_label;"
    "from app.index import build_index;"
    "print(json.dumps({"
    "'s1':[r['tag'] for r in search_records('Foo Bar ')],"
    "'s2':[r['tag'] for r in search_records('  Baz  Qux ')],"
    "'t1':tag_label('Foo Bar '),"
    "'t2':tag_label('  Baz  Qux '),"
    "'i1':sorted(build_index([' Foo Bar ','Baz  Qux'])),"
    "}))"
)

try:
    proc = subprocess.run(
        [sys.executable, "-c", PROBE, str(ws)],
        capture_output=True,
        text=True,
        cwd=str(ws),
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip()[-300:])
    d = json.loads(proc.stdout.strip().splitlines()[-1])
    out["observed"] = d
    out["search_fixed"] = d["s1"] == ["foo-bar"] and d["s2"] == ["baz-qux"]
    out["tags_fixed"] = d["t1"] == "Foo Bar" and d["t2"] == "Baz Qux"
    out["index_fixed"] = d["i1"] == ["baz-qux", "foo-bar"]
except Exception as exc:  # noqa: BLE001
    note("probe", exc)

out["task_complete"] = out["search_fixed"]
out["root_cause_fixed"] = (
    out["search_fixed"] and out["tags_fixed"] and out["index_fixed"]
)
out["symptom_only_patch"] = out["search_fixed"] and not out["root_cause_fixed"]
print(json.dumps(out, ensure_ascii=False))
