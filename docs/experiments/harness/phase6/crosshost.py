"""Cross-host state isolation, direction 2: Codex OFF while Claude stays ON.

Flips the real Codex saved setting and restores it in the same run, verifying the
byte hash before and after. Writes nothing outside the two plugin-data files.
"""

import hashlib
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH = Path(__file__).resolve().parents[3] / ".pilot"
CLAUDE_STATE = SCRATCH / "claude-config/plugins/data/leanclarity-inline/state.json"
CODEX_STATE = Path(os.path.expanduser("~/.codex/plugins/data/leanclarity-leanclarity/state.json"))
ON = "A050EF06EA542B8FD8781F1E945F9ADCD03C7AE5190719E66BA826E2059FCE12"
OFF = "7187D1E8E2A4D61B1DC5DFEDB22D703A462DF21470E0C145365B20FB3ED467C3"


def h(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest().upper() if p.exists() else "ABSENT"


def label(d: str) -> str:
    return {ON: "ON", OFF: "OFF"}.get(d, d[:16])


def codex(prompt: str) -> str:
    p = subprocess.run(
        ["codex", "exec", "--skip-git-repo-check", "-m", "gpt-5.6-luna", "-s", "read-only", prompt],
        cwd=SCRATCH / "p6ws", capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=420, stdin=subprocess.DEVNULL,
    )
    return (p.stdout or "")[-400:]


def codex_injected() -> int:
    """Characters of LeanClarity context in the newest Codex rollout."""
    day = Path(os.path.expanduser("~/.codex/sessions")) / time.strftime("%Y/%m/%d")
    newest = max(day.glob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime)
    total = 0
    for line in newest.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"# LeanClarity' in line:
            total += 1
    return total


def claude_injected() -> list:
    log = SCRATCH / f"dbg-x-{int(time.time()*1000)}.log"
    subprocess.run(
        ["claude", "-p", "Reply with exactly: X", "--model", "claude-haiku-4-5-20251001",
         "--setting-sources", "local", "--plugin-dir", str((SCRATCH / "candidate-1.0.2").resolve()),
         "--debug-file", str(log)],
        cwd=SCRATCH / "p6ws", env=dict(os.environ, CLAUDE_CONFIG_DIR=str((SCRATCH / "claude-config").resolve())),
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=300, stdin=subprocess.DEVNULL,
    )
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    log.unlink(missing_ok=True)
    return re.findall(r"provided additionalContext \((\d+) chars\)", text)


print(f"before   claude={label(h(CLAUDE_STATE))}  codex={label(h(CODEX_STATE))}")

print("\ncodex: leanclarity off")
print("  ", codex("leanclarity off").strip().replace("\n", " | ")[:120])
print(f"  after write   claude={label(h(CLAUDE_STATE))}  codex={label(h(CODEX_STATE))}")

print(f"  codex items in newest rollout after OFF: {codex_injected()}")
print(f"  claude injection while codex is OFF: {claude_injected()}")

print("\ncodex: leanclarity on  (restore)")
print("  ", codex("leanclarity on").strip().replace("\n", " | ")[:120])
final_codex, final_claude = h(CODEX_STATE), h(CLAUDE_STATE)
print(f"  restored      claude={label(final_claude)}  codex={label(final_codex)}")
print(f"\ncodex restored to the pre-test value: {final_codex == ON}")
print(f"claude untouched throughout:          {final_claude == ON}")
