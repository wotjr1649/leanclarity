"""Does each host actually read the stand-in from the workspace?

Evidence that can only be produced when the text is present: the final sentence of
each of the two sections, quoted verbatim. A yes/no probe is not enough - protocol
section 5.1 recorded both hosts returning a false YES with the policy demonstrably
absent. Asking for the FINAL sentence also proves the tail arrived, which a head
marker would not.

Usage: python docs/experiments/robustness/probe_standin.py
"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".pilot"
STANDIN = Path(__file__).resolve().parent / "standin.md"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CODEX_MODEL = "gpt-5.6-luna"

PONY_TAIL = "The shortest path to done is the right path."
ADHD_TAIL = "If yes, send."

PROBE = (
    "Line 1: if your context contains a section headed 'Ponytail', reply with that "
    "section's final sentence copied verbatim; otherwise write NONE. "
    "Line 2: if your context contains a section headed 'i-have-adhd', reply with that "
    "section's final sentence copied verbatim; otherwise write NONE. "
    "Output exactly two lines and nothing else. Do not use any tool."
)


def workspace(tmp: Path, filename: str) -> Path:
    ws = tmp / filename.replace(".", "_")
    ws.mkdir(parents=True, exist_ok=True)
    (ws / "app.py").write_text("def main():\n    return 1\n", encoding="utf-8", newline="\n")
    (ws / filename).write_text(STANDIN.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "base"]):
        subprocess.run(["git", *args], cwd=ws, capture_output=True, text=True)
    return ws


def run_claude(ws: Path, effort: str):
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str((SCRATCH / "claude-config").resolve())
    proc = subprocess.run(
        ["claude", "-p", PROBE, "--model", CLAUDE_MODEL, "--effort", effort,
         "--setting-sources", "local", "--dangerously-skip-permissions",
         "--output-format", "json"],
        cwd=ws, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600, stdin=subprocess.DEVNULL)
    try:
        return json.loads(proc.stdout).get("result", "")
    except Exception:
        return proc.stdout


def run_codex(ws: Path, effort: str):
    env = dict(os.environ)
    env["CODEX_HOME"] = str((SCRATCH / "codex-home").resolve())
    last = ws.parent / "codex.last"
    subprocess.run(
        ["codex", "exec", PROBE, "-m", CODEX_MODEL,
         "-c", f'model_reasoning_effort="{effort}"', "--approve-for-me",
         "--dangerously-bypass-hook-trust", "--output-last-message", str(last)],
        cwd=ws, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=900, stdin=subprocess.DEVNULL)
    return last.read_text(encoding="utf-8") if last.is_file() else ""


def main() -> int:
    ok = True
    with tempfile.TemporaryDirectory(prefix="lc-standin-") as td:
        tmp = Path(td)
        for host, filename, runner in (("claude", "CLAUDE.md", run_claude),
                                       ("codex", "AGENTS.md", run_codex)):
            ws = workspace(tmp, filename)
            reply = (runner(ws, "high") or "").strip()
            pony = PONY_TAIL in reply
            adhd = ADHD_TAIL in reply
            good = pony and adhd
            ok = ok and good
            print(f"\n== {host} via {filename}  {'PASS' if good else 'FAIL'}"
                  f"  ponytail={pony} i-have-adhd={adhd}")
            print(f"   {reply[:300]!r}")
    print("\nSTAND-IN LOADING", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
