"""OFF-arm preflight: set both hosts OFF, then prove zero injection.

Proof, not assumption. The probe asks for evidence that can only be produced
when the policy IS in context - a verbatim quote of its first bullet - so a
model cannot agree its way to a false NONE. Protocol section 5.1 recorded that
lesson after a yes/no probe returned a false YES on both hosts.

Claude additionally self-proves per turn: --debug-file records
"provided additionalContext (N chars)" only when the hook injected, so an OFF
run leaves no such line. Codex exposes no equivalent counter, which is why the
probe exists.

Usage: python docs/experiments/onoff/preflight.py [on|off]
"""
import io, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".pilot"
CANDIDATE = SCRATCH / "candidate-1.0.2"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CODEX_MODEL = "gpt-5.6-luna"

STATES = {
    "claude": SCRATCH / "claude-config" / "plugins" / "data" / "leanclarity-inline" / "state.json",
    "codex": SCRATCH / "codex-home" / "plugins" / "data" / "leanclarity-leanclarity" / "state.json",
}

PROBE = (
    "If your context contains a section titled 'LeanClarity Engineering Policy', "
    "reply with that section's first bullet copied verbatim and nothing else. "
    "If it does not, reply with exactly NONE and nothing else. Do not use any tool."
)


def set_state(enabled: bool) -> None:
    for host, path in STATES.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"enabled": enabled}, separators=(",", ":")),
                        encoding="utf-8", newline="\n")
        print(f"  {host}: {path.relative_to(ROOT)} -> {path.read_text(encoding='utf-8')}")


def git_init(tmp: Path) -> None:
    """Codex refuses to run outside a trusted directory, and prepare_workspace
    git-inits every real run workspace. The probe must look the same."""
    (tmp / "README.md").write_text("probe\n", encoding="utf-8", newline="\n")
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.email=p@p", "-c", "user.name=p", "commit", "-qm", "probe"]):
        subprocess.run(["git", *args], cwd=tmp, capture_output=True, text=True)


def probe_claude(tmp: Path):
    env = dict(os.environ)
    env["CLAUDE_CONFIG_DIR"] = str((SCRATCH / "claude-config").resolve())
    debug = tmp / "probe.debug"
    proc = subprocess.run(
        ["claude", "-p", PROBE, "--model", CLAUDE_MODEL,
         "--plugin-dir", str(CANDIDATE.resolve()),
         "--setting-sources", "local", "--dangerously-skip-permissions",
         "--output-format", "json", "--debug-file", str(debug)],
        cwd=tmp, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=300, stdin=subprocess.DEVNULL,
    )
    try:
        response = json.loads(proc.stdout).get("result", "")
    except Exception:
        response = proc.stdout
    text = debug.read_text(encoding="utf-8", errors="replace") if debug.is_file() else ""
    injected = [int(n) for n in re.findall(r"provided additionalContext \((\d+) chars\)", text)]
    return response.strip(), injected


def probe_codex(tmp: Path):
    env = dict(os.environ)
    env["CODEX_HOME"] = str((SCRATCH / "codex-home").resolve())
    last = tmp / "probe.last"
    subprocess.run(
        ["codex", "exec", PROBE, "-m", CODEX_MODEL, "--approve-for-me",
         "--dangerously-bypass-hook-trust", "--output-last-message", str(last)],
        cwd=tmp, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600, stdin=subprocess.DEVNULL,
    )
    response = last.read_text(encoding="utf-8") if last.is_file() else ""
    return response.strip(), None


def main() -> int:
    want = (sys.argv[1] if len(sys.argv) > 1 else "off").lower()
    if want not in ("on", "off"):
        raise SystemExit("usage: preflight.py [on|off]")
    enabled = want == "on"

    print(f"setting saved state to {want.upper()}")
    set_state(enabled)

    ok = True
    with tempfile.TemporaryDirectory(prefix="lc-probe-") as td:
        tmp = Path(td)
        git_init(tmp)
        for host, probe in (("claude", probe_claude), ("codex", probe_codex)):
            response, injected = probe(tmp)
            said_none = response.strip().upper().startswith("NONE")
            quoted = "Understand the request and its relevant execution flow" in response
            if enabled:
                good = quoted and (injected is None or injected == [2486])
            else:
                good = said_none and not quoted and (injected is None or injected == [])
            ok = ok and good
            print(f"\n== {host}  {'PASS' if good else 'FAIL'}")
            print(f"   injected_chars: {injected}")
            print(f"   response: {response[:200]!r}")

    print("\nPREFLIGHT", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
