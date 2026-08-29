"""Compression-pilot harness. One file, four subcommands.

  arms      materialize the four arm plugin directories and print their hashes
  manifest  write docs/experiments/fixtures/MANIFEST.md
  run       execute one (host, arm, case, run) and store the record
  score     recompute machine signals over every stored record

Nothing here is release evidence. See docs/experiments/README.md.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs" / "experiments" / "fixtures"
LEVELS = ROOT / "docs" / "experiments" / "levels"
RUNS = ROOT / "docs" / "experiments" / "runs"
SCRATCH = ROOT / ".pilot"

ARMS = ("L0", "L1", "L2", "L3")
HOSTS = ("claude", "codex")

# Frozen distribution byte set of candidate 1.0.1 (GO evidence, Artifact section).
CANDIDATE_FILES = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    "LICENSE",
    "README.md",
    "THIRD_PARTY_NOTICES.md",
    "hooks/hooks.json",
    "hooks/leanclarity.cjs",
    "policies/engineering.md",
    "policies/guidance.md",
)

CLAUDE_MODEL = "claude-haiku-4-5-20251001"
CODEX_MODEL = "gpt-5.6-luna"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def rmtree(path: Path) -> None:
    """Delete a scratch tree. Git marks its object files read-only on Windows."""
    def onexc(func, target, _exc):
        os.chmod(target, 0o700)
        func(target)

    shutil.rmtree(path, onexc=onexc)


def policy_dir(arm: str) -> Path:
    return ROOT / "policies" if arm == "L0" else LEVELS / arm


def load_cases() -> dict:
    lines = (FIXTURES / "cases.jsonl").read_text(encoding="utf-8").splitlines()
    return {json.loads(line)["id"]: json.loads(line) for line in lines if line.strip()}


# --------------------------------------------------------------------------- arms


def cmd_arms(_args) -> None:
    """Copy the candidate into .pilot/arms/<ARM>/ with that arm's policies."""
    out_root = SCRATCH / "arms"
    for arm in ARMS:
        dest = out_root / arm
        if dest.exists():
            rmtree(dest)
        for rel in CANDIDATE_FILES:
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            src = ROOT / rel
            if rel.startswith("policies/"):
                src = policy_dir(arm) / Path(rel).name
            target.write_bytes(src.read_bytes())

        eng = (dest / "policies" / "engineering.md").read_text(encoding="utf-8").strip()
        gui = (dest / "policies" / "guidance.md").read_text(encoding="utf-8").strip()
        main = eng + "\n\n" + gui + "\n"
        manifest = "".join(
            f"{rel}\t{(dest / rel).stat().st_size}\t{sha256((dest / rel).read_bytes())}\n"
            for rel in sorted(CANDIDATE_FILES)
        )
        print(
            f"{arm}  main={len(main.encode('utf-8')):>5} bytes  "
            f"mainSHA={sha256(main.encode('utf-8'))[:16]}  "
            f"armSHA={sha256(manifest.encode('utf-8'))[:16]}  {dest}"
        )


# ----------------------------------------------------------------------- manifest


def cmd_manifest(_args) -> None:
    """Freeze fixture bytes into docs/experiments/fixtures/MANIFEST.md."""
    rows = []
    for path in sorted(FIXTURES.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.md":
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(FIXTURES).as_posix()
        data = path.read_bytes()
        rows.append((rel, len(data), sha256(data)))

    aggregate = sha256(
        "".join(f"{rel}\t{size}\t{digest}\n" for rel, size, digest in rows).encode("utf-8")
    )
    body = [
        "# Pilot fixture manifest",
        "",
        "Frozen before the first pilot run. Any change to a byte below invalidates every",
        "run recorded against the old hash (docs/experiments/README.md pre-committed rules).",
        "",
        f"Aggregate SHA-256: `{aggregate}`",
        "",
        "Identity algorithm: sort the paths below relative to `docs/experiments/fixtures/`;",
        "for each emit UTF-8 `<path>\\t<byte-count>\\t<uppercase-file-SHA-256>\\n`; hash those",
        "manifest bytes with SHA-256. Same algorithm as the candidate identity.",
        "",
        "| Path | Bytes | SHA-256 |",
        "|---|---:|---|",
    ]
    body += [f"| `{rel}` | {size} | `{digest}` |" for rel, size, digest in rows]
    body.append("")
    (FIXTURES / "MANIFEST.md").write_text("\n".join(body), encoding="utf-8", newline="\n")
    print(f"wrote {FIXTURES / 'MANIFEST.md'} ({len(rows)} files)")
    print(f"aggregate {aggregate}")


# ---------------------------------------------------------------------------- run


def git(args, cwd) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    ).stdout


def prepare_workspace(case: dict, tag: str) -> Path:
    ws = SCRATCH / "ws" / tag
    if ws.exists():
        rmtree(ws)
    ws.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / case["workspace"], ws)
    git(["init", "-q"], ws)
    # Interpreter bytecode is not part of anyone's answer. Exclude it outside the
    # working tree so the fixture bytes stay exactly what MANIFEST.md froze.
    (ws / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (ws / ".git" / "info" / "exclude").write_text(
        "__pycache__/\n*.pyc\n", encoding="utf-8", newline="\n"
    )
    git(["add", "-A"], ws)
    subprocess.run(
        ["git", "-c", "user.name=pilot", "-c", "user.email=pilot@localhost",
         "commit", "-q", "-m", "fixture"],
        cwd=ws, capture_output=True, text=True,
    )
    return ws


def build_command(host: str, arm: str, case: dict, response_file: Path, home: str | None,
                  debug_file: Path | None = None):
    """Return the host command and its environment.

    ``home`` overrides the isolated profile. The isolated profile is the primary
    evidence; a real profile carries that host's own global instructions and other
    plugins, which the pilot records as a confound rather than a clean arm.
    """
    env = dict(os.environ)
    if host == "claude":
        env["CLAUDE_CONFIG_DIR"] = home or str((SCRATCH / "claude-config").resolve())
        cmd = [
            "claude", "-p", case["prompt"],
            "--model", CLAUDE_MODEL,
            "--plugin-dir", str((SCRATCH / "arms" / arm).resolve()),
            # Measured on 2.1.251: an isolated CLAUDE_CONFIG_DIR still loads the
            # user CLAUDE.md, and "--setting-sources project,local" still does.
            # Only "local" drops it, which the arm needs: the real user memory
            # names a response language and its own engineering rules.
            "--setting-sources", "local",
            "--dangerously-skip-permissions",
        ]
        if debug_file is not None:
            cmd += ["--debug-file", str(debug_file)]
    else:
        env["CODEX_HOME"] = home or str((SCRATCH / "codex-home").resolve())
        cmd = [
            "codex", "exec", case["prompt"],
            "-m", CODEX_MODEL,
            "-s", "workspace-write",
            "-c", "approval_policy=never",
            "--output-last-message", str(response_file),
        ]
    return cmd, env


def activate_codex_arm(arm: str, plugin_root: str) -> str:
    """Copy the arm's two policy files into an installed Codex plugin.

    Everything else in that installed copy stays as installed, so the hook map,
    the runtime and both manifests are byte-identical across arms. Returns the
    resulting Main-composition SHA-256 for the run record.
    """
    dest = Path(plugin_root)
    for name in ("engineering.md", "guidance.md"):
        (dest / "policies" / name).write_bytes((policy_dir(arm) / name).read_bytes())
    eng = (dest / "policies" / "engineering.md").read_text(encoding="utf-8").strip()
    gui = (dest / "policies" / "guidance.md").read_text(encoding="utf-8").strip()
    main = eng + "\n\n" + gui + "\n"
    return sha256(main.encode("utf-8"))


def cmd_run(args) -> None:
    cases = load_cases()
    case = cases[args.case]
    tag = f"{args.host}-{args.arm}-{args.case}-r{args.run}"
    main_sha = None
    if args.host == "codex" and args.codex_plugin_root:
        main_sha = activate_codex_arm(args.arm, args.codex_plugin_root)
    ws = prepare_workspace(case, tag)
    response_file = ws.parent / f"{tag}.last"
    debug_file = ws.parent / f"{tag}.debug" if args.host == "claude" else None
    cmd, env = build_command(args.host, args.arm, case, response_file, args.home, debug_file)

    started = time.time()
    timed_out = False
    try:
        proc = subprocess.run(
            cmd, cwd=ws, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=args.timeout,
        )
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        # A lost run is worse than a recorded timeout: the batch must not stall
        # and the cell must not silently disappear from the matrix.
        timed_out = True
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"; timeout after {args.timeout}s"
        code = None
    elapsed = round(time.time() - started, 1)

    if args.host == "codex":
        response = response_file.read_text(encoding="utf-8") if response_file.exists() else ""
    else:
        response = stdout

    injected = None
    if debug_file is not None and debug_file.exists():
        text = debug_file.read_text(encoding="utf-8", errors="replace")
        found = re.findall(r"provided additionalContext \((\d+) chars\)", text)
        injected = [int(n) for n in found]
        debug_file.unlink()

    git(["add", "-A"], ws)
    diff = git(["diff", "--cached"], ws)

    record = {
        "id": tag,
        "host": args.host,
        "arm": args.arm,
        "case": args.case,
        "run": args.run,
        "model": CLAUDE_MODEL if args.host == "claude" else CODEX_MODEL,
        "arm_main_sha256": main_sha,
        "injected_chars": injected,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "elapsed_s": elapsed,
        "exit_code": code,
        "timed_out": timed_out,
        "response": response,
        "diff": diff,
        "stderr_tail": stderr[-2000:],
    }
    if "oracle_script" in case["machine_signals"]:
        oracle = subprocess.run(
            [sys.executable, "-B", str(ROOT / case["machine_signals"]["oracle_script"]), str(ws)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
        )
        try:
            record["oracle"] = json.loads(oracle.stdout.strip().splitlines()[-1])
        except Exception as exc:  # noqa: BLE001
            record["oracle"] = {"error": f"{type(exc).__name__}: {exc}", "raw": oracle.stdout[-500:]}

    dest = Path(args.out) if args.out else RUNS / args.host / args.arm
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{args.case}-r{args.run}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n"
    )
    print(f"{tag}: exit={code} {elapsed}s response={len(response)}ch diff={len(diff)}ch")


# -------------------------------------------------------------------------- score


def diff_lines(diff: str, prefix: str) -> list[str]:
    return [
        line[1:] for line in diff.splitlines()
        if line.startswith(prefix) and not line.startswith(prefix * 3)
    ]


def signals_for(record: dict, case: dict) -> dict:
    ms = case["machine_signals"]
    diff = record.get("diff", "")
    response = record.get("response", "") or ""
    low = response.lower()
    added, removed = diff_lines(diff, "+"), diff_lines(diff, "-")

    sig = {
        "diff_empty": diff.strip() == "",
        "new_files": diff.count("new file mode "),
        "new_deps": 0,
        "removed_guard_lines": 0,
    }

    for dep in ms.get("dependency_files", []):
        in_dep = False
        for line in diff.splitlines():
            if line.startswith("diff --git "):
                in_dep = line.endswith(dep)
            elif in_dep and line.startswith("+") and not line.startswith("+++"):
                sig["new_deps"] += 1

    guards = ms.get("guard_substrings", [])
    if guards:
        sig["removed_guard_lines"] = sum(
            1 for line in removed if any(g in line for g in guards)
        )
        sig["guards_gone"] = sorted(
            g for g in guards
            if any(g in line for line in removed) and not any(g in line for line in added)
        )

    if "forbidden_import_substrings" in ms:
        sig["forbidden_imports"] = sorted(
            {m for m in ms["forbidden_import_substrings"]
             if any(m in line for line in added)}
        )

    if "added_lines_required_in_paths" in ms:
        touched, current = set(), None
        for line in diff.splitlines():
            if line.startswith("diff --git "):
                current = line.split(" b/")[-1]
            elif current and line.startswith("+") and not line.startswith("+++"):
                touched.add(current)
        sig["added_line_paths"] = sorted(touched)
        sig["test_lines_added"] = any(
            any(p in path for p in ms["added_lines_required_in_paths"]) for path in touched
        )
        sig["test_mentions"] = sorted(
            {w for w in ms.get("added_test_line_substrings", [])
             if any(w in line for line in added)}
        )

    if "first_line_preamble_prefixes" in ms:
        first = next((ln.strip() for ln in response.splitlines() if ln.strip()), "")
        fl = first.lower().lstrip("#*- ").strip()
        sig["first_line"] = first[:300]
        sig["first_line_is_preamble"] = any(
            fl.startswith(p) for p in ms["first_line_preamble_prefixes"]
        )
        sig["first_line_has_content"] = any(
            c in fl for c in ms["first_line_content_substrings"]
        )

    if "seeded_findings" in ms:
        hits = {
            key: any(kw.lower() in low for kw in kws)
            for key, kws in ms["seeded_findings"].items()
        }
        sig["findings"] = hits
        sig["findings_hit"] = sum(hits.values())
        sig["cap_phrases_hit"] = sorted(
            {p for p in ms.get("cap_phrases", []) if p.lower() in low}
        )

    if "assumption_substrings" in ms:
        sig["assumption_markers"] = sorted(
            {m for m in ms["assumption_substrings"] if m.lower() in low}
        )
        sig["asked_or_assumed"] = bool(sig["assumption_markers"])

    if "impl_markers" in ms:
        sig["impls_touched"] = sorted(
            name for name, markers in ms["impl_markers"].items()
            if any(m in line for m in markers for line in added + removed)
        )

    if "oracle" in record:
        sig["oracle"] = record["oracle"]

    sig["machine_verdict"] = machine_verdict(sig, case)
    return sig


def machine_verdict(sig: dict, case: dict) -> str:
    """First-pass verdict. FAIL is decisive; PASS still goes to the screener."""
    ms = case["machine_signals"]
    oracle = sig.get("oracle") or {}

    if ms.get("require_empty_diff") and not sig["diff_empty"]:
        return "FAIL"
    if sig["new_deps"] > ms.get("max_new_deps", 10**6):
        return "FAIL"
    if sig["new_files"] > ms.get("max_new_files", 10**6):
        return "FAIL"
    if sig.get("forbidden_imports"):
        return "FAIL"
    if ms.get("oracle_fail_key") and oracle.get(ms["oracle_fail_key"]) is not False:
        return "FAIL"
    if ms.get("oracle_pass_key") and oracle.get(ms["oracle_pass_key"]) is not True:
        return "FAIL"
    if "test_lines_added" in sig and not sig["test_lines_added"]:
        return "FAIL"
    if "first_line_is_preamble" in sig and (
        sig["first_line_is_preamble"] or not sig["first_line_has_content"]
    ):
        return "FAIL"
    if "findings_hit" in sig and sig["findings_hit"] < ms.get("min_findings", 0):
        return "FAIL"
    if sig.get("cap_phrases_hit"):
        return "FAIL"
    if "asked_or_assumed" in sig and not sig["asked_or_assumed"]:
        return "FAIL"
    return "PASS"


def cmd_score(args) -> None:
    cases = load_cases()
    base = Path(args.dir) if args.dir else RUNS
    out = []
    for path in sorted(base.rglob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        case = cases[record["case"]]
        sig = signals_for(record, case)
        out.append({"id": record["id"], **{k: v for k, v in sig.items()}})
        print(f"{record['id']:<34} {sig['machine_verdict']}")
    dest = (base / "results.jsonl") if args.dir else (ROOT / "docs" / "experiments" / "results.jsonl")
    dest.write_text(
        "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in out),
        encoding="utf-8", newline="\n",
    )
    print(f"\nwrote {dest} ({len(out)} records)")


# --------------------------------------------------------------------------- main


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("arms").set_defaults(func=cmd_arms)
    sub.add_parser("manifest").set_defaults(func=cmd_manifest)

    run = sub.add_parser("run")
    run.add_argument("--host", required=True, choices=HOSTS)
    run.add_argument("--arm", required=True, choices=ARMS)
    run.add_argument("--case", required=True)
    run.add_argument("--run", required=True, type=int, choices=(1, 2, 3))
    run.add_argument("--timeout", type=int, default=1200)
    run.add_argument("--home", help="override the isolated host profile directory")
    run.add_argument("--out", help="override the record output directory")
    run.add_argument("--codex-plugin-root", help="installed Codex plugin root to swap policies into")
    run.set_defaults(func=cmd_run)

    score = sub.add_parser("score")
    score.add_argument("--dir", help="override the record directory")
    score.set_defaults(func=cmd_score)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
