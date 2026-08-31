"""Guard the one thing the --standin flag must not break: with the default
`full`, the runner still builds the exact invocation that produced the frozen
96-run robustness record. Runs no model - it intercepts subprocess.run and
reads back the command.

  python docs/experiments/attribution/test_standin_flag.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "docs" / "experiments" / "robustness"))
import runner  # noqa: E402


class Captured(Exception):
    def __init__(self, cmd):
        self.cmd = cmd


def claude_cmd():
    real = subprocess.run
    subprocess.run = lambda cmd, **kw: (_ for _ in ()).throw(Captured(cmd))
    try:
        runner.run_turn("claude", {}, "hi", 1, Path("."), None, Path("."), 60)
    except Captured as exc:
        return exc.cmd
    finally:
        subprocess.run = real
    raise AssertionError("subprocess.run was never reached")


def main():
    saved = runner.STANDIN
    try:
        runner.STANDIN = saved if saved is not None else runner.HERE / "standin.md"
        full = claude_cmd()
        assert "--append-system-prompt-file" in full, full
        assert full[full.index("--append-system-prompt-file") + 1].endswith("standin.md"), full
        assert "--effort" in full and full[full.index("--effort") + 1] == runner.EFFORT

        runner.STANDIN = None
        none = claude_cmd()
        assert "--append-system-prompt-file" not in none, none
        # Everything else is identical: dropping the stand-in is the only difference
        # between the robustness cell and the attribution cell.
        assert none == [a for a in full if a not in
                        ("--append-system-prompt-file",
                         full[full.index("--append-system-prompt-file") + 1])], (full, none)
    finally:
        runner.STANDIN = saved
    print("ok: default delivers the stand-in, --standin none drops only that")


if __name__ == "__main__":
    main()
