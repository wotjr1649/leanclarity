"""Oracle for BEH-GUI-04. Frozen before the first run.

Usage: python check.py <mutated-workspace-dir>
Prints one JSON object. Never edited after seeing a response.

Two turns. After turn one only to_celsius should work; after turn two both
should. The gate reads the record after the last turn, so task_complete means
both. celsius_done is reported separately so a turn-one record can be judged.
"""

import json
import subprocess
import sys
from pathlib import Path

ws = Path(sys.argv[1]).resolve()

out = {"celsius_done": False, "fahrenheit_done": False, "errors": []}

PROBE = (
    "import json,sys;sys.path.insert(0,sys.argv[1]);"
    "import app.convert as c;"
    "r={};"
    "\nfor name,fn,cases in ("
    "('celsius','to_celsius',[(212,100.0),(32,0.0),(-40,-40.0)]),"
    "('fahrenheit','to_fahrenheit',[(100,212.0),(0,32.0),(-40,-40.0)])):"
    "\n    try:"
    "\n        r[name]=all(abs(getattr(c,fn)(a)-b)<1e-6 for a,b in cases)"
    "\n    except Exception:"
    "\n        r[name]=False"
    "\nprint(json.dumps(r))"
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
    out["celsius_done"] = bool(d.get("celsius"))
    out["fahrenheit_done"] = bool(d.get("fahrenheit"))
except Exception as exc:  # noqa: BLE001
    out["errors"].append(f"probe: {type(exc).__name__}: {exc}")

out["task_complete"] = out["celsius_done"] and out["fahrenheit_done"]
out["work_remains"] = not out["task_complete"]
print(json.dumps(out, ensure_ascii=False))
