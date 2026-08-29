"""Last two Codex rows on 1.0.2: Subagent under OFF, and an invalid Guidance policy.

Both mutate only the task-owned isolated home and restore it byte-for-byte.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH = Path(__file__).resolve().parents[3] / ".pilot"
HOME = SCRATCH / "codex-home"
WS = SCRATCH / "p6ws-codex"
STATE = HOME / "plugins/data/leanclarity-leanclarity/state.json"
GUIDANCE = HOME / "plugins/cache/leanclarity/leanclarity/1.0.2/policies/guidance.md"
ON = "A050EF06EA542B8FD8781F1E945F9ADCD03C7AE5190719E66BA826E2059FCE12"
GUIDANCE_SHA = "D50C059F0498CEE86C8F36A57441ECF5C16827A21A17E1712DE15E57621ED7D8"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper() if p.exists() else "ABSENT"


def run(prompt):
    cmd = ["codex", "exec", prompt, "--dangerously-bypass-hook-trust", "--skip-git-repo-check",
           "-m", "gpt-5.6-luna", "-s", "read-only"]
    return subprocess.run(cmd, cwd=WS, env=dict(os.environ, CODEX_HOME=str(HOME.resolve())),
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=600, stdin=subprocess.DEVNULL)


def scan(n=1):
    day = HOME / "sessions" / time.strftime("%Y/%m/%d")
    logs = sorted(day.glob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime)[-n:]
    result = []
    for lg in logs:
        items = []
        sub = False
        for line in lg.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                o = json.loads(line)
            except Exception:
                continue
            p = o.get("payload") or {}
            if o.get("type") == "session_meta" and isinstance(p.get("source"), dict) \
                    and "subagent" in p["source"]:
                sub = True
            if p.get("type") == "message":
                for c in p.get("content") or []:
                    t = c.get("text")
                    if isinstance(t, str) and t.startswith("# LeanClarity"):
                        items.append(len(t))
        result.append(("subagent" if sub else "main", items))
    return result


assert sha(GUIDANCE) == GUIDANCE_SHA, "guidance.md is not the candidate byte set"
print(f"guidance ok, state {sha(STATE)[:12]}")

# --- Subagent under OFF
run("leanclarity off")
print(f"state now OFF: {sha(STATE)[:12]}")
run("Delegate to a subagent: ask it to reply with the single word PONG. Then report it.")
print(f"[Subagent under OFF] last 3 sessions: {scan(3)}")
run("leanclarity on")
print(f"state restored: {sha(STATE)[:12]} matches ON = {sha(STATE) == ON}")

# --- Invalid Guidance policy, Main all-or-nothing
original = GUIDANCE.read_bytes()
GUIDANCE.write_bytes(b"   \n")
try:
    run("reply with exactly: IP")
    print(f"[invalid Guidance policy] {scan(1)}")
finally:
    GUIDANCE.write_bytes(original)
    print(f"guidance restored: {sha(GUIDANCE)[:12]} matches candidate = {sha(GUIDANCE) == GUIDANCE_SHA}")

run("reply with exactly: OK")
print(f"[after restore] {scan(1)}")
print(f"final state: {sha(STATE)[:12]} matches ON = {sha(STATE) == ON}")
