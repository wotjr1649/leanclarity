"""Generate a minimal Claude plugin that injects standin.md at SessionStart.

Why a plugin rather than --append-system-prompt-file: the stand-in must reach the
model through the SAME channel LeanClarity uses (SessionStart additionalContext).
A system-prompt append would rank the stand-in above LeanClarity by construction,
which is exactly the thing the study is trying to measure rather than assume.

Why not a project CLAUDE.md: measured 2026-08-30 on Claude Code 2.1.251 - loading
project memory needs `--setting-sources project,local`, and that also pulls in the
operator's own ~/.claude/CLAUDE.md even under an isolated CLAUDE_CONFIG_DIR. Probed
with an exact phrase found only in that file: HIT under `project,local`, NONE
under `local` alone. The gate's `local` configuration is therefore clean, and it is
kept.

Output goes to .pilot/standin-plugin/ (gitignored, machine-local). Regenerate with
this script; standin.md and its hash are the committed source of truth.

Usage: python docs/experiments/robustness/build_standin_plugin.py
"""
import hashlib
import io
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STANDIN = Path(__file__).resolve().parent / "standin.md"
OUT = ROOT / ".pilot" / "standin-plugin"

HOOK = """'use strict';
// Emits the stand-in instruction text as SessionStart additionalContext, the same
// channel LeanClarity uses. No state, no flag file, no mode: the bytes on disk are
// the bytes injected, so the study's constant is actually constant.
const fs = require('node:fs');
const path = require('node:path');

const root = process.env.CLAUDE_PLUGIN_ROOT || process.env.PLUGIN_ROOT;
if (!root) process.exit(0);
let text;
try {
  text = fs.readFileSync(path.join(root, 'standin.md'), 'utf8');
} catch {
  process.exit(0);
}
process.stdout.write(JSON.stringify({
  hookSpecificOutput: { hookEventName: 'SessionStart', additionalContext: text },
}));
"""

HOOKS_JSON = {
    "hooks": {
        "SessionStart": [
            {
                "matcher": "startup|resume|clear|compact",
                "hooks": [
                    {
                        "type": "command",
                        "command": 'node "${CLAUDE_PLUGIN_ROOT}/hooks/standin.cjs"',
                        "timeout": 10,
                    }
                ],
            }
        ]
    }
}

PLUGIN_JSON = {
    "name": "standin",
    "version": "0.0.1",
    "description": "Study fixture: injects the pinned upstream instruction text.",
}


def main() -> None:
    text = io.open(STANDIN, encoding="utf-8").read()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / ".claude-plugin").mkdir(parents=True)
    (OUT / "hooks").mkdir(parents=True)

    io.open(OUT / "standin.md", "w", encoding="utf-8", newline="\n").write(text)
    io.open(OUT / "hooks" / "standin.cjs", "w", encoding="utf-8", newline="\n").write(HOOK)
    for path, obj in ((OUT / "hooks" / "hooks.json", HOOKS_JSON),
                      (OUT / ".claude-plugin" / "plugin.json", PLUGIN_JSON)):
        io.open(path, "w", encoding="utf-8", newline="\n").write(
            json.dumps(obj, indent=2) + "\n")

    print(f"standin-plugin built at {OUT}")
    print(f"  standin.md {len(text)} chars  SHA-256 {digest}")


if __name__ == "__main__":
    main()
