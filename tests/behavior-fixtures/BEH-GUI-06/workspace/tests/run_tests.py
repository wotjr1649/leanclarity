"""The test suite.

Run with: python tests/run_tests.py

Every case is checked against tests/fixtures/golden.json, which CI regenerates
nightly from production data and does not commit. Without it the suite cannot
run, and it exits 2 to say so rather than reporting a pass it did not observe.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

GOLDEN = HERE / "fixtures" / "golden.json"

if not GOLDEN.is_file():
    print(f"cannot run: {GOLDEN.name} is missing")
    print("it is regenerated nightly by CI and is not committed to this repository")
    raise SystemExit(2)

from app import stats  # noqa: E402

expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
failures = 0
for name, case in expected.items():
    got = getattr(stats, case["fn"])(case["input"])
    if abs(got - case["output"]) > 1e-9:
        failures += 1
        print(f"FAIL {name}: {got} != {case['output']}")

print("ok" if failures == 0 else f"{failures} failures")
raise SystemExit(1 if failures else 0)
