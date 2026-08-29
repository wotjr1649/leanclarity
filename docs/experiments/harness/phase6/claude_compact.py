"""Force a Claude auto-compaction and see whether SessionStart:compact fires.

claude -p has no /compact. --autocompact takes a 100k-1M token window, so the only
route is to fill a session past that window and let the host compact it.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH = Path(__file__).resolve().parents[3] / ".pilot"
CONFIG = SCRATCH / "claude-config"
WS = SCRATCH / "compactws"
MODEL = "claude-haiku-4-5-20251001"
WINDOW = "100000"

WS.mkdir(parents=True, exist_ok=True)
para = ("The inventory reconciliation service walks every warehouse ledger, compares the "
        "recorded quantity against the counted quantity, and emits a discrepancy record "
        "whenever the two disagree by more than the tolerance configured for that site. "
        "Each discrepancy carries the ledger id, the counted-at timestamp, the operator "
        "identifier, and a free-text note explaining the count conditions. ")
for i in range(8):
    (WS / f"ledger_{i}.md").write_text(
        f"# Ledger notes {i}\n\n" + "".join(f"## Section {j}\n\n{para}\n\n" for j in range(90)),
        encoding="utf-8", newline="\n")
total_kb = sum(p.stat().st_size for p in WS.glob("*.md")) // 1024
print(f"fixture: 8 files, {total_kb} KiB total")


def run(prompt, extra=(), want_json=False):
    log = SCRATCH / f"dbg-c-{int(time.time()*1000)}.log"
    cmd = ["claude", "-p", prompt, "--model", MODEL,
           "--setting-sources", "local", "--dangerously-skip-permissions",
           "--plugin-dir", str((SCRATCH / "candidate-1.0.2").resolve()),
           "--autocompact", WINDOW, "--debug-file", str(log)]
    if want_json:
        cmd += ["--output-format", "json"]
    cmd += list(extra)
    proc = subprocess.run(cmd, cwd=WS, env=dict(os.environ, CLAUDE_CONFIG_DIR=str(CONFIG.resolve())),
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=900, stdin=subprocess.DEVNULL)
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    log.unlink(missing_ok=True)
    return proc, text


def show(tag, proc, debug):
    ctx = re.findall(r"provided additionalContext \((\d+) chars\)", debug)
    src = sorted(set(re.findall(r"SessionStart:(\w+)", debug)))
    comp = len(re.findall(r"[Cc]ompact", debug))
    print(f"[{tag}] ctx={ctx} sources={src} compact-mentions={comp} exit={proc.returncode}")
    return src, ctx


proc, debug = run("Read ledger_0.md and ledger_1.md in full, then reply with exactly: C1",
                  want_json=True)
src, ctx = show("turn 1", proc, debug)
sid = None
try:
    sid = json.loads(proc.stdout).get("session_id")
except Exception:
    print("  stdout:", (proc.stdout or "")[:200])
print(f"  session_id={sid}")

for n in range(2, 9):
    if not sid:
        break
    a, b = (2 * n - 2) % 8, (2 * n - 1) % 8
    proc, debug = run(
        f"Read ledger_{a}.md and ledger_{b}.md in full, then reply with exactly: C{n}",
        extra=["--resume", sid])
    src, ctx = show(f"turn {n}", proc, debug)
    if "compact" in src:
        print("\n*** SessionStart:compact observed ***")
        break
else:
    print("\nno compact source seen within the turn budget")
