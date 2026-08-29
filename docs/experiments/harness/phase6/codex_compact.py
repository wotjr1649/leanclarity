"""Force a Codex auto-compaction on candidate 1.0.2 and look for a re-injection."""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH = Path(__file__).resolve().parents[3] / ".pilot"
HOME = SCRATCH / "codex-home"
WS = SCRATCH / "compactws-codex"
MODEL = "gpt-5.6-luna"
WINDOW = os.environ.get("LC_WINDOW", "24000")

WS.mkdir(parents=True, exist_ok=True)
para = ("The inventory reconciliation service walks every warehouse ledger, compares the "
        "recorded quantity against the counted quantity, and emits a discrepancy record "
        "whenever the two disagree by more than the tolerance configured for that site. ")
for i in range(6):
    (WS / f"ledger_{i}.md").write_text(
        f"# Ledger notes {i}\n\n" + "".join(f"## Section {j}\n\n{para}\n\n" for j in range(60)),
        encoding="utf-8", newline="\n")
print(f"fixture: 6 files, {sum(p.stat().st_size for p in WS.glob('*.md'))//1024} KiB")


def run(args, resume=False):
    # codex exec resume rejects -s; only the first call may set the sandbox.
    cmd = ["codex", "exec", *args, "--dangerously-bypass-hook-trust", "--skip-git-repo-check",
           "-m", MODEL, "-c", f"model_context_window={WINDOW}"]
    if not resume:
        cmd += ["-s", "read-only"]
    proc = subprocess.run(cmd, cwd=WS, env=dict(os.environ, CODEX_HOME=str(HOME.resolve())),
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=900, stdin=subprocess.DEVNULL)
    return proc


def newest_log():
    day = HOME / "sessions" / time.strftime("%Y/%m/%d")
    return max(day.glob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime)


def scan(path):
    injections, compacted = [], 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"# LeanClarity' in line:
            injections.append(1)
        if '"compacted"' in line or '"type":"compacted"' in line:
            compacted += 1
    return len(injections), compacted


first = run(["Read ledger_0.md and ledger_1.md in full, then reply with exactly: K1"])
log = newest_log()
sid = log.name.split("-", 6)[-1].replace(".jsonl", "")
inj, comp = scan(log)
print(f"[turn 1] injections={inj} compacted_events={comp} exit={first.returncode} sid={sid}")

for n in range(2, 7):
    p = run(["resume", sid, f"Read ledger_{n % 6}.md and ledger_{(n+1) % 6}.md in full, then reply with exactly: K{n}"], resume=True)
    inj, comp = scan(log)
    print(f"[turn {n}] injections={inj} compacted_events={comp} exit={p.returncode}")
    if comp and inj > 1:
        print("\n*** re-injection after a compacted event observed ***")
        break
    if p.returncode != 0:
        print("  stderr:", (p.stderr or "")[-300:])
        break
else:
    print("\nno compaction reached within the turn budget")
print("log:", log)
