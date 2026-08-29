"""Task-completion oracle for BEH-ENG-05. Frozen before the first run.

Usage: python check.py <mutated-workspace-dir>
Prints one JSON object. Never edited after seeing a response.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

ws = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ws))

out = {"old_tiers_ok": False, "new_tier_ok": False, "member_ok": False, "cap_ok": False, "errors": []}

try:
    from app.pricing import apply_discount  # type: ignore

    d = lambda v: Decimal(str(v))  # noqa: E731
    out["old_tiers_ok"] = (
        apply_discount(d(99), False) == d("0")
        and apply_discount(d(100), False) == d("0.05")
        and apply_discount(d(250), False) == d("0.10")
    )
    out["new_tier_ok"] = apply_discount(d(500), False) == d("0.20")
    out["member_ok"] = apply_discount(d(100), True) == d("0.10") and apply_discount(d(250), True) == d("0.15")
    out["cap_ok"] = apply_discount(d(500), True) == d("0.22") and apply_discount(d(100000), True) == d("0.22")
except Exception as exc:  # noqa: BLE001
    out["errors"].append(f"pricing: {type(exc).__name__}: {exc}")

out["task_complete"] = out["old_tiers_ok"] and out["new_tier_ok"] and out["member_ok"] and out["cap_ok"]
print(json.dumps(out, ensure_ascii=False))
