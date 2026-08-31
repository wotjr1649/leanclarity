"""Watch for the pathology the robustness study found: when prepare_workspace fails
to clear its scratch directory on Windows (WinError 32, an orphaned host process
holding it as cwd), the directory is left present but empty, git discovers the
enclosing repository instead, and the run's diff becomes the repository's diff.
That run gets scored against the wrong artifact and nothing else notices.

PROTOCOL.md commits this study to checking every record. A path in a diff that the
case's own fixture does not contain, and that the model did not plausibly create, is
the signature.

  python docs/experiments/attribution/check_workspace.py
"""
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "docs" / "experiments" / "attribution" / "runs"
# Files only this repository has. A judged diff naming one of these means the diff
# came from the repository, not from a fixture workspace.
REPO_ONLY = ("policies/", "hooks/", "docs/", "tests/behavior-fixtures/",
             "THIRD_PARTY_NOTICES.md", ".plugin/", "leanclarity.test.cjs")


def leaked(diff: str) -> list:
    paths = set(re.findall(r"^\+\+\+ b/(.+)$", diff, re.M))
    return sorted(p for p in paths if any(m in p for m in REPO_ONLY)), len(paths)


def main() -> None:
    bad, checked = [], 0
    for f in sorted(glob.glob(str(RUNS / "*" / "*" / "*.json"))):
        rec = json.loads(Path(f).read_text(encoding="utf-8"))
        checked += 1
        hits, n = leaked(rec.get("diff", ""))
        if hits:
            bad.append((rec["id"], hits[:5], n))
    for run_id, hits, n in bad:
        print(f"REPOSITORY LEAK  {run_id}: {n} paths, e.g. {hits}")
    print(f"checked {checked} record(s); {len(bad)} with the pathology")
    if bad:
        raise SystemExit(1)


def selfcheck() -> None:
    """A checker that has never seen the thing it looks for is not a checker.
    The signature below is the shape the robustness study actually recorded."""
    clean = "--- a/app/records.py\n+++ b/app/records.py\n@@ -1 +1 @@\n-x\n+y\n"
    assert leaked(clean) == ([], 1), leaked(clean)
    leak = clean + "--- a/policies/engineering.md\n+++ b/policies/engineering.md\n"
    assert leaked(leak)[0] == ["policies/engineering.md"], leaked(leak)
    assert leaked("")[0] == []
    print("ok: clean diffs pass, a repository path in the diff is caught")


if __name__ == "__main__":
    import sys
    selfcheck() if "--selfcheck" in sys.argv else main()
