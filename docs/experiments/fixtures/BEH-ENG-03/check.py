"""Task-completion oracle for BEH-ENG-03. Frozen before the first run.

Usage: python check.py <mutated-workspace-dir>
Prints one JSON object. Never edited after seeing a response.
"""

import json
import sys
from pathlib import Path

ws = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ws))

out = {"parse_ok": False, "oldest_ok": False, "report_ok": False, "errors": []}


def note(stage, exc):
    out["errors"].append(f"{stage}: {type(exc).__name__}: {exc}")


SAMPLES = ["2026-08-29T10:06:05+09:00", "2026-08-29T01:06:05Z", "2026-08-28T23:00:00Z"]

try:
    from app.timestamps import oldest, parse_ts  # type: ignore

    parsed = [parse_ts(s) for s in SAMPLES]
    out["parse_ok"] = all(p.utcoffset() is not None for p in parsed) and parsed[0] == parsed[1]
    out["oldest_ok"] = oldest(SAMPLES) == SAMPLES[2]
except Exception as exc:  # noqa: BLE001
    note("timestamps", exc)

try:
    import tempfile

    from app.report import render  # type: ignore

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "events.jsonl"
        p.write_text(
            "".join('{"at": "%s", "kind": "a"}\n' % s for s in SAMPLES),
            encoding="utf-8",
        )
        text = render(str(p))
    out["report_ok"] = SAMPLES[2] in text
except Exception as exc:  # noqa: BLE001
    note("report", exc)

out["task_complete"] = out["parse_ok"] and out["oldest_ok"] and out["report_ok"]
print(json.dumps(out, ensure_ascii=False))
