"""Close the remaining Codex rows on candidate 1.0.2: near match, invalid state,
host control, SubagentStart. Isolated task-owned CODEX_HOME; restores state.json."""

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
ON = "A050EF06EA542B8FD8781F1E945F9ADCD03C7AE5190719E66BA826E2059FCE12"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper() if p.exists() else "ABSENT"


def run(prompt, extra=()):
    cmd = ["codex", "exec", prompt, "--dangerously-bypass-hook-trust", "--skip-git-repo-check",
           "-m", "gpt-5.6-luna", "-s", "read-only", *extra]
    return subprocess.run(cmd, cwd=WS, env=dict(os.environ, CODEX_HOME=str(HOME.resolve())),
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=600, stdin=subprocess.DEVNULL)


def newest_logs(n=1):
    day = HOME / "sessions" / time.strftime("%Y/%m/%d")
    return sorted(day.glob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime)[-n:]


def scan(path):
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        p = o.get("payload") or {}
        if p.get("type") == "message":
            for c in p.get("content") or []:
                t = c.get("text")
                if isinstance(t, str) and t.startswith("# LeanClarity"):
                    out.append(len(t))
        if o.get("type") == "session_meta":
            src = p.get("source")
            if isinstance(src, dict) and "subagent" in src:
                out.append("SUBAGENT-SESSION")
    return out


print(f"state before: {sha(STATE)[:12]}")

# 1 near match must not be intercepted
p = run("/leanclarity")
blocked = "Blocked" in (p.stdout or "") + (p.stderr or "")
print(f"[1 near match /leanclarity] blocked={blocked} "
      f"answered={'yes' if (p.stdout or '').strip() else 'no'}  items={scan(newest_logs()[0])}")

# 2 host control
p = run("reply with exactly: HC", extra=["--disable", "hooks"])
print(f"[2 --disable hooks] hook lines={(p.stdout or '').count('hook:')} items={scan(newest_logs()[0])}")

# 3 invalid state
STATE.write_text('{"enabled":"yes"}', encoding="utf-8", newline="\n")
p = run("reply with exactly: IS")
print(f"[3 invalid state] items={scan(newest_logs()[0])}")
STATE.write_bytes(b'{"enabled":true}\n')
print(f"  state restored: {sha(STATE)[:12]} matches ON = {sha(STATE) == ON}")

# 4 SubagentStart
p = run("Delegate to a subagent: ask it to reply with the single word PONG. "
        "Then report what the subagent said.")
logs = newest_logs(3)
for lg in logs:
    print(f"[4 subagent] {lg.name[-20:]}  items={scan(lg)}")

print(f"\nstate after: {sha(STATE)[:12]}  matches ON = {sha(STATE) == ON}")
