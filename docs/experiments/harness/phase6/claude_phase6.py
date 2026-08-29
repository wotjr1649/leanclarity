"""Phase 6 Claude Code matrix on 2.1.251, isolated profile, candidate 1.0.2.

Task-owned: writes only under .pilot/. Restores the plugin-data state at the end.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".pilot"
CONFIG = SCRATCH / "claude-config"
WS = SCRATCH / "p6ws"
DATA = CONFIG / "plugins" / "data" / "leanclarity-inline"
MODEL = "claude-haiku-4-5-20251001"
CANDIDATE = SCRATCH / "candidate-1.0.2"

WS.mkdir(parents=True, exist_ok=True)
(WS / "note.txt").write_text("hello\n", encoding="utf-8")


def run(prompt, arm="candidate", extra=(), want_json=False, timeout=300):
    log = SCRATCH / f"dbg-{int(time.time()*1000)}.log"
    cmd = ["claude", "-p", prompt, "--model", MODEL,
           "--setting-sources", "local", "--dangerously-skip-permissions",
           "--debug-file", str(log)]
    if arm:
        src = CANDIDATE if arm == "candidate" else SCRATCH / "arms" / arm
        cmd += ["--plugin-dir", str(src.resolve())]
    if want_json:
        cmd += ["--output-format", "json"]
    cmd += list(extra)
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(CONFIG.resolve()))
    proc = subprocess.run(cmd, cwd=WS, env=env, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout,
                          stdin=subprocess.DEVNULL)
    text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    log.unlink(missing_ok=True)
    return proc, text


def signature(debug):
    return {
        "plugins": re.findall(r"Registered (\d+) hooks from (\d+) plugins", debug),
        "injections": re.findall(r"Hook (\w+)[^\n]*?provided additionalContext \((\d+) chars\)", debug),
        "any_ctx": re.findall(r"provided additionalContext \((\d+) chars\)", debug),
        "blocked": len(re.findall(r'"decision":\s*"block"', debug)),
        "preview": "file-preview" in debug or "replaced with a file" in debug.lower(),
    }


def state():
    f = DATA / "state.json"
    if not f.exists():
        return "ABSENT"
    b = f.read_bytes()
    return f"{b.decode(chr(117)+chr(116)+chr(102)+chr(45)+chr(56), 'replace').strip()} sha={hashlib.sha256(b).hexdigest().upper()[:12]}"


def report(name, proc, debug, note=""):
    s = signature(debug)
    out = (proc.stdout or "").strip().replace("\n", " | ")[:150]
    print(f"\n[{name}] {note}")
    print(f"  plugins={s['plugins']} ctx={s['any_ctx']} injections={s['injections']}")
    print(f"  block_json={s['blocked']} preview={s['preview']} state={state()}")
    print(f"  stdout: {out}")
    return s


results = {}

# 1 startup, absent state
if (DATA / "state.json").exists():
    (DATA / "state.json").unlink()
p, d = run("Reply with exactly: A1")
results["1_startup_absent"] = report("1 startup, absent state", p, d, "expect 2486, default ON")

# 2 exact status command
p, d = run("leanclarity")
results["2_status"] = report("2 exact status command", p, d, "expect block + ON reason, state untouched")

# 3 near-match must not be intercepted
p, d = run("/leanclarity")
results["3_near_match"] = report("3 near match /leanclarity", p, d, "expect no block")

# 4 leanclarity off
p, d = run("leanclarity off")
results["4_off"] = report("4 leanclarity off", p, d, "expect block + OFF written")

# 5 new session after OFF (clean boundary)
p, d = run("Reply with exactly: A5")
results["5_startup_after_off"] = report("5 startup after OFF", p, d, "expect NO injection")

# 6 subagent after OFF
p, d = run("Use the Task tool to launch one general-purpose agent whose entire job is to reply PONG. Then reply with exactly: A6", timeout=420)
results["6_subagent_off"] = report("6 subagent after OFF", p, d, "expect NO injection")

# 7 leanclarity on
p, d = run("leanclarity on")
results["7_on"] = report("7 leanclarity on", p, d, "expect block + ON written")

# 8 new session after ON, capture session id
p, d = run("Reply with exactly: A8", want_json=True)
results["8_startup_after_on"] = report("8 startup after ON", p, d, "expect 2486")
session_id = None
try:
    session_id = json.loads(p.stdout).get("session_id")
except Exception:
    pass
print(f"  session_id={session_id}")

# 9 resume source
if session_id:
    p, d = run("Reply with exactly: A9", extra=["--resume", session_id])
    results["9_resume"] = report("9 resume source", p, d, "expect a further injection")

# 10 subagent after ON
p, d = run("Use the Task tool to launch one general-purpose agent whose entire job is to reply PONG. Then reply with exactly: A10", timeout=420)
results["10_subagent_on"] = report("10 subagent after ON", p, d, "expect 1176 Engineering only")

# 11 invalid state
(DATA / "state.json").write_text('{"enabled":"yes"}', encoding="utf-8")
p, d = run("Reply with exactly: A11")
results["11_invalid_state"] = report("11 invalid state", p, d, "expect NO injection")

# 12 invalid policy, all-or-nothing
(DATA / "state.json").write_text('{"enabled":true}', encoding="utf-8")
broken = SCRATCH / "arms" / "BROKEN"
if broken.exists():
    shutil.rmtree(broken, onexc=lambda f, t, e: (os.chmod(t, 0o700), f(t)))
shutil.copytree(CANDIDATE, broken)
(broken / "policies" / "guidance.md").write_bytes(b"   \n")
p, d = run("Reply with exactly: A12", arm="BROKEN")
results["12_invalid_policy"] = report("12 invalid guidance policy", p, d, "expect NO injection at all")

# 13 host control: plugin not loaded
p, d = run("Reply with exactly: A13", arm=None)
results["13_no_plugin"] = report("13 no plugin loaded", p, d, "expect 0 plugins, no injection")

# restore: leave the saved setting at the pilot's required ON
(DATA / "state.json").write_text('{"enabled":true}', encoding="utf-8", newline="\n")
print(f"\nfinal state: {state()}")
json.dump(results, open(SCRATCH / "claude_phase6_102.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"wrote {SCRATCH / 'claude_phase6_102.json'}")
