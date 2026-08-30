"""Robustness study runner: does LeanClarity still change anything when the two
upstream instruction sets are already loaded?

Imports the frozen harness for everything that must stay identical to the gate -
workspace preparation, diffing, machine signals, verdicts - and re-implements only
the invocation, because the harness pins effort and has no stand-in flag and is
inside the fixture freeze. `harness.py verify` must still report MATCH afterwards.

Stand-in delivery, both measured on 2026-08-30:
  Claude  --append-system-prompt-file. The SessionStart additionalContext channel
          cannot carry it: SPEC 11 documents Claude file-preview replacement above
          10,000 characters, and at 12,072 the model reports "only a 2KB preview is
          visible and the full text is truncated". Project memory is unavailable
          too - it needs `--setting-sources project,local`, which also loads the
          operator's own ~/.claude/CLAUDE.md (probed: "Claude Code Host Adapter"
          HIT under project,local, NONE under local alone).
  Codex   workspace AGENTS.md, committed into the baseline so it never appears in
          a judged diff.

Usage:
  python docs/experiments/robustness/runner.py --host claude --arm on
  python docs/experiments/robustness/runner.py --host codex  --arm off
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests" / "behavior-fixtures"))
import harness  # noqa: E402  frozen, imported read-only

HERE = Path(__file__).resolve().parent
STANDIN = HERE / "standin.md"
RUNS = HERE / "runs"

CASES = ("BEH-ENG-05", "BEH-GUI-07", "BEH-SAFE-02", "BEH-ENG-06")
WS_SUFFIX = ""
RUN_NUMBERS = tuple(range(1, 7))
EFFORT = "high"

STATE = {
    "claude": harness.SCRATCH / "claude-config" / "plugins" / "data" / "leanclarity-inline" / "state.json",
    "codex": harness.SCRATCH / "codex-home" / "plugins" / "data" / "leanclarity-leanclarity" / "state.json",
}


def set_arm(host: str, arm: str) -> None:
    """Only this host's state. The two hosts run in parallel with independently
    interleaved arms, so writing both would let one batch clobber the other."""
    path = STATE[host]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"enabled": arm == "on"}, separators=(",", ":")),
                    encoding="utf-8", newline="\n")


def prepare(case: dict, host: str, tag: str) -> Path:
    # WS_SUFFIX lets a retry use a fresh scratch directory. prepare_workspace
    # rmtree-s the old one, and on Windows an orphaned host process that still
    # has it as its cwd holds it open (WinError 32). Renaming the scratch path
    # avoids both deleting and killing anything.
    ws = harness.prepare_workspace(case, tag + WS_SUFFIX)
    if host == "codex":
        (ws / "AGENTS.md").write_text(STANDIN.read_text(encoding="utf-8"),
                                      encoding="utf-8", newline="\n")
        harness.git(["add", "-A"], ws)
        subprocess.run(["git", "-c", "user.name=robust", "-c", "user.email=r@l",
                        "commit", "-q", "-m", "standin"], cwd=ws, capture_output=True, text=True)
    return ws


def run_turn(host, case, text, index, ws, session, tmp, timeout):
    env = dict(os.environ)
    sandbox = "workspace-write"
    debug = None
    if host == "claude":
        env["CLAUDE_CONFIG_DIR"] = str((harness.SCRATCH / "claude-config").resolve())
        debug = tmp / f"t{index}.debug"
        cmd = ["claude", "-p", text,
               "--model", harness.CLAUDE_MODEL, "--effort", EFFORT,
               "--plugin-dir", str(harness.CANDIDATE.resolve()),
               "--setting-sources", "local",
               "--append-system-prompt-file", str(STANDIN),
               "--dangerously-skip-permissions",
               "--output-format", "json", "--debug-file", str(debug)]
        if session:
            cmd += ["--resume", session]
    else:
        env["CODEX_HOME"] = str((harness.SCRATCH / "codex-home").resolve())
        last = tmp / f"t{index}.last"
        effort = ["-c", f'model_reasoning_effort="{EFFORT}"']
        if index == 1:
            cmd = ["codex", "exec", text, "-m", harness.CODEX_MODEL, *effort, "--approve-for-me"]
        else:
            cmd = ["codex", "exec", "resume", "--last", text, "-m", harness.CODEX_MODEL, *effort]
            if index in case.get("codex_bypass_turns", []):
                cmd.append("--dangerously-bypass-approvals-and-sandbox")
                sandbox = "bypassed"
            else:
                sandbox = "read-only"
        cmd += ["--dangerously-bypass-hook-trust", "--output-last-message", str(last)]

    started = time.time()
    timed_out = False
    try:
        proc = subprocess.run(cmd, cwd=ws, env=env, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout,
                              stdin=subprocess.DEVNULL)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout, stderr, code = exc.stdout or "", (exc.stderr or "") + f"; timeout {timeout}s", None

    if host == "claude":
        try:
            payload = json.loads(stdout)
            response = payload.get("result", "")
            session = payload.get("session_id") or session
        except (json.JSONDecodeError, AttributeError):
            response = stdout
        injected = harness.injected_chars(debug)
    else:
        last = tmp / f"t{index}.last"
        response = last.read_text(encoding="utf-8") if last.is_file() else ""
        injected = None

    return {
        "turn": index, "prompt": text, "response": response,
        "diff": harness.staged_diff(ws), "exit_code": code, "timed_out": timed_out,
        "elapsed_s": round(time.time() - started, 1),
        "injected_chars": injected,
        "sandbox": sandbox if host == "codex" else "skip-permissions",
        "stderr_tail": stderr[-1500:],
    }, session


def one_run(host: str, arm: str, case_id: str, run: int, timeout: int) -> None:
    cases = harness.load_cases()
    case = cases[case_id]
    if host == "claude":
        harness.assert_delivery_matches(harness.CANDIDATE)
    else:
        harness.sync_codex_delivery()

    tag = f"{arm}-{host}-{case_id}-r{run}"
    ws = prepare(case, host, tag)
    tmp = ws.parent / f"{tag}-out"
    if tmp.exists():
        harness.rmtree(tmp)
    tmp.mkdir(parents=True)

    turns, session = [], None
    for index, text in enumerate(case["turns"], 1):
        turn, session = run_turn(host, case, text, index, ws, session, tmp, timeout)
        turns.append(turn)
        print(f"  turn {index}: exit={turn['exit_code']} {turn['elapsed_s']}s "
              f"resp={len(turn['response'])}ch inj={turn['injected_chars']}", flush=True)
        if turn["timed_out"]:
            break

    record = {
        "id": tag, "arm": arm, "host": host, "case": case_id, "run": run,
        "candidate": harness.CANDIDATE_ID,
        "model": harness.CLAUDE_MODEL if host == "claude" else harness.CODEX_MODEL,
        "effort": EFFORT,
        "standin_sha256": harness.sha256(STANDIN.read_bytes()),
        "standin_chars": len(STANDIN.read_text(encoding="utf-8")),
        "standin_delivery": "append-system-prompt-file" if host == "claude" else "workspace AGENTS.md",
        "sampling_controls": "none exposed by this surface at these settings",
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "turns": turns,
        "response": "\n\n".join(f"[turn {t['turn']}]\n{t['response']}" for t in turns)
        if len(turns) > 1 else (turns[0]["response"] if turns else ""),
        "diff": turns[-1]["diff"] if turns else "",
        "timed_out": any(t["timed_out"] for t in turns),
        "elapsed_s": round(sum(t["elapsed_s"] for t in turns), 1),
    }

    oracle_script = case["machine_signals"].get("oracle_script")
    if oracle_script:
        proc = subprocess.run([sys.executable, "-B", str(ROOT / oracle_script), str(ws)],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=180)
        try:
            record["oracle"] = json.loads(proc.stdout.strip().splitlines()[-1])
        except Exception as exc:  # noqa: BLE001
            record["oracle"] = {"error": f"{type(exc).__name__}: {exc}",
                                "raw": (proc.stdout or proc.stderr)[-500:]}

    record["signals"] = harness.signals_for(record, case)

    dest = RUNS / arm / host
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{case_id}-r{run}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{tag}: {record['elapsed_s']}s verdict={record['signals']['machine_verdict']}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", required=True, choices=("claude", "codex"))
    # "both" interleaves the arms inside each case/run so the two arms share a
    # window. The ON/OFF study could not do this - its ON arm was already
    # recorded, thirteen hours earlier - and window drift is the confound it
    # could not remove. Here it costs nothing but a state-file write.
    ap.add_argument("--arm", required=True, choices=("on", "off", "both"))
    ap.add_argument("--case", choices=CASES)
    ap.add_argument("--run", type=int, choices=RUN_NUMBERS)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--ws-suffix", default="", help="scratch dir suffix for retries")
    args = ap.parse_args()
    globals()["WS_SUFFIX"] = args.ws_suffix

    ids = [args.case] if args.case else list(CASES)
    runs = [args.run] if args.run else list(RUN_NUMBERS)
    arms = ("on", "off") if args.arm == "both" else (args.arm,)
    for case_id in ids:
        for run in runs:
            for arm in arms:
                out = RUNS / arm / args.host / f"{case_id}-r{run}.json"
                if out.is_file() and not args.redo:
                    print(f"skip {arm} {args.host} {case_id} r{run}")
                    continue
                set_arm(args.host, arm)
                print(f"== {arm} {args.host} {case_id} r{run}", flush=True)
                one_run(args.host, arm, case_id, run, args.timeout)


if __name__ == "__main__":
    main()
