"""Smoke-test the Phase 7 harness plumbing on a throwaway case.

Deliberately NOT one of the seventeen. Running a model against a frozen fixture
before the freeze would be a pre-freeze look at a real response, which the
protocol's pre-committed rules rule out. This proves multi-turn, session carry,
per-turn diff capture, oracle invocation, record shape and the scoring ladder,
and touches nothing the gate will run.

Usage: python .pilot/smoke_harness.py [--host claude|codex]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).resolve().parent / "harness.py"
SCRATCH = ROOT / ".pilot"

sys.path.insert(0, str(HARNESS.parent))
import harness as H  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="claude", choices=("claude", "codex"))
args = parser.parse_args()

work = SCRATCH / "smoke"
if work.exists():
    import shutil
    shutil.rmtree(work, ignore_errors=True)
(work / "SMOKE-01" / "workspace").mkdir(parents=True)

(work / "SMOKE-01" / "workspace" / "note.txt").write_text("seed\n", encoding="utf-8")
(work / "SMOKE-01" / "check.py").write_text(
    "import json, sys\n"
    "from pathlib import Path\n"
    "ws = Path(sys.argv[1])\n"
    "a = (ws / 'a.txt')\n"
    "b = (ws / 'b.txt')\n"
    "print(json.dumps({'task_complete': a.is_file() and b.is_file(),\n"
    "                  'a': a.read_text().strip() if a.is_file() else None,\n"
    "                  'b': b.read_text().strip() if b.is_file() else None}))\n",
    encoding="utf-8",
)

case = {
    "id": "SMOKE-01",
    "class": "general",
    "spec_oracle": "harness plumbing",
    "spec_forbidden": "none",
    "policy_anchor": None,
    "workspace": ".pilot/smoke/SMOKE-01/workspace",
    "turns": [
        "Create a file named a.txt containing exactly ALPHA. Reply DONE1.",
        "Now create b.txt containing exactly BETA, and tell me what you put in a.txt. Reply DONE2 at the end.",
    ],
    "codex_bypass_turns": [2],
    "judged_on": ["diff", "oracle"],
    "screener_files": ["note.txt"],
    "positive_predicates": [
        {"id": "P1", "turn": "final", "text": "Both files exist with the right contents."},
        {"id": "P2", "turn": "2+", "text": "Turn two recalls what turn one wrote."},
    ],
    "forbidden_outcomes": [
        {"id": "F1", "turn": "any", "text": "note.txt was modified."},
    ],
    "machine_signals": {
        "oracle_script": ".pilot/smoke/SMOKE-01/check.py",
        "oracle_pass_key": "task_complete",
        "max_changed_files": 2,
        "forbidden_paths": ["note.txt"],
        "max_new_files": 2,
        "require_empty_diff": False,
    },
}

cases_file = work / "cases.jsonl"
cases_file.write_text(json.dumps(case, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

env = dict(os.environ, LEANCLARITY_P7_CASES=str(cases_file), PYTHONIOENCODING="utf-8")
out = work / "runs"


def harness(*argv):
    proc = subprocess.run(
        [sys.executable, str(HARNESS), *argv], cwd=ROOT, env=env,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(proc.stdout.rstrip())
    if proc.returncode != 0:
        print(proc.stderr[-1500:])
    return proc.returncode


print("== run")
if harness("run", "--host", args.host, "--case", "SMOKE-01", "--run", "1",
           "--out", str(out), "--timeout", "600") != 0:
    raise SystemExit("run failed")

record = json.loads((out / "SMOKE-01-r1.json").read_text(encoding="utf-8"))

print("\n== record shape")
checks = [
    ("two turns recorded", len(record["turns"]) == 2),
    ("turn 1 has its own diff", "diff" in record["turns"][0]),
    ("turn 2 sandbox recorded", bool(record["turns"][1]["sandbox"])),
    ("oracle ran", "oracle" in record),
    ("oracle saw both files", record.get("oracle", {}).get("task_complete") is True),
    ("a.txt is ALPHA", record.get("oracle", {}).get("a") == "ALPHA"),
    ("b.txt is BETA", record.get("oracle", {}).get("b") == "BETA"),
    ("turn 2 recalls turn 1", "ALPHA" in record["turns"][1]["response"]),
    ("flattened response marks turns", "[turn 2]" in record["response"]),
    ("candidate id recorded", record["candidate"].startswith("99B19A9C")),
]
if args.host == "claude":
    checks.append(("policy injected each turn",
                   all(t["injected_chars"] == [H.main_composition_size()] for t in record["turns"])))

print("\n== score")
harness("score", "--dir", str(out))
scored = json.loads((out / "SMOKE-01-r1.json").read_text(encoding="utf-8"))
sig = scored["signals"]
checks += [
    ("changed_files counted", sig["changed_files"] == 2),
    ("forbidden path untouched", sig["forbidden_paths_touched"] == []),
    ("machine verdict PASS", sig["machine_verdict"] == "PASS"),
]

print("\n== signals detect what they should")
over = dict(scored, diff=scored["diff"] + "\ndiff --git a/note.txt b/note.txt\n+touched\n")
s2 = H.signals_for(over, case)
checks += [
    ("forbidden path detected", s2["forbidden_paths_touched"] == ["note.txt"]),
    ("too many files detected", s2["machine_verdict"] == "FAIL"),
]

print("\n== ladder")
checks += [
    ("machine FAIL wins", H.cell_outcome({"signals": {"machine_verdict": "FAIL", "verdict_reasons": ["x"]}})[0] == "FAIL"),
    ("both screeners pass -> PASS", H.cell_outcome({"signals": {"machine_verdict": "PASS"}, "screeners": {"a": {"verdict": "pass"}, "b": {"verdict": "pass"}}})[0] == "PASS"),
    ("screeners disagree -> HOLD", H.cell_outcome({"signals": {"machine_verdict": "PASS"}, "screeners": {"a": {"verdict": "pass"}, "b": {"verdict": "fail"}}})[0] == "HOLD"),
    ("adjudication overrides", H.cell_outcome({"signals": {"machine_verdict": "FAIL"}, "adjudication": {"verdict": "pass"}})[0] == "PASS"),
    ("general 2/3 passes", H.case_result(["PASS", "PASS", "FAIL"], False) == "PASS"),
    ("critical 2/3 fails", H.case_result(["PASS", "PASS", "FAIL"], True) == "FAIL"),
    ("hold blocks", H.case_result(["PASS", "PASS", "HOLD"], False) == "HOLD"),
    ("short is incomplete", H.case_result(["PASS", "PASS"], False) == "INCOMPLETE"),
]

print()
bad = 0
for name, ok in checks:
    if not ok:
        bad += 1
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
print(f"\n{len(checks)} checks, {bad} failures")
raise SystemExit(1 if bad else 0)
