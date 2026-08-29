"""Re-run a case's oracle against stored runs, without re-invoking any model.

Usage: python tests/behavior-fixtures/reoracle.py <CASE-ID> [--dir DIR]

An oracle is a pure function of the workspace the run left behind, and the
stored `diff` determines that workspace completely. So when an oracle is
corrected, the model runs do not have to happen again: rebuild each run's final
workspace by applying its recorded diff to a fresh copy of the frozen fixture,
and evaluate the corrected oracle there.

The protocol's freeze rule requires that a scoring-logic change re-runs the
affected cells. This is that re-run, done at the only layer that changed.

Records are rewritten in place with the new oracle output and the previous one
kept under `oracle_superseded`, so the correction is visible rather than
silently overwriting what the gate first observed.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("case")
parser.add_argument("--dir", default=str(ROOT / "docs" / "evidence" / "phase7-runs"))
args = parser.parse_args()

case = H.load_cases()[args.case]
script = case["machine_signals"].get("oracle_script")
if not script:
    raise SystemExit(f"{args.case} has no oracle script")

paths = sorted(Path(args.dir).rglob(f"{args.case}-r*.json"))
if not paths:
    raise SystemExit(f"no records for {args.case} under {args.dir}")

for path in paths:
    record = json.loads(path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "workspace"
        shutil.copytree(ROOT / case["workspace"], ws)
        H.git(["init", "-q"], ws)
        H.git(["add", "-A"], ws)
        subprocess.run(
            ["git", "-c", "user.name=reoracle", "-c", "user.email=reoracle@localhost",
             "commit", "-q", "-m", "fixture"],
            cwd=ws, capture_output=True, text=True,
        )
        diff = record.get("diff", "")
        if diff.strip():
            patch = Path(tmp) / "run.patch"
            patch.write_text(diff, encoding="utf-8", newline="\n")
            applied = subprocess.run(
                ["git", "apply", "--whitespace=nowarn", str(patch)],
                cwd=ws, capture_output=True, text=True,
            )
            if applied.returncode != 0:
                print(f"{path.parent.name}/{path.stem}: PATCH FAILED "
                      f"{applied.stderr.strip()[-160:]}")
                continue
        proc = subprocess.run(
            [sys.executable, "-B", str(ROOT / script), str(ws)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
        )
        try:
            fresh = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception as exc:  # noqa: BLE001
            fresh = {"error": f"{type(exc).__name__}: {exc}",
                     "raw": (proc.stdout or proc.stderr)[-400:]}

    before = record.get("oracle")
    if before is not None and "oracle_superseded" not in record:
        record["oracle_superseded"] = before
    record["oracle"] = fresh
    record["signals"] = H.signals_for(record, case)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=1),
                    encoding="utf-8", newline="\n")

    def brief(o):
        return " ".join(f"{k}={v}" for k, v in (o or {}).items() if k != "errors")

    print(f"{path.parent.name}/{path.stem}")
    print(f"   was: {brief(before)}")
    print(f"   now: {brief(fresh)}  -> {record['signals']['machine_verdict']}")
