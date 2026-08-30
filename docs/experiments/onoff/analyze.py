"""Paired ON/OFF analysis. No model calls.

ON  = docs/evidence/phase7-runs/          (the recorded Phase 7 gate runs)
OFF = docs/experiments/onoff/runs/        (this study's control arm)

Both arms run the same frozen fixtures, the same pinned models, the same
isolated profiles and the same harness. The only difference is the plugin's
saved state, proved zero-injection in preflight-off.log.

The paired unit is a cell: one case on one host, the mean of its three runs.
Phase 7's own records put between-cell sd at 934 response characters against a
within-cell sd of 104, so an unpaired comparison would be swamped by which case
is being run. Pairing removes that entirely.

Significance is a sign-flip permutation test on the 34 cell differences: exact
in construction, no normality assumption, which matters because every cell's
mean far exceeds its median.
"""
import io, json, math, random, statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ON = ROOT / "docs" / "evidence" / "phase7-runs"
OFF = ROOT / "docs" / "experiments" / "onoff" / "runs"
HOSTS = ("claude", "codex")
RUNS = (1, 2, 3)
DRAWS = 200_000
random.seed(20260830)


def diff_counts(d):
    add = rem = 0
    for line in (d or "").splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            add += 1
        elif line.startswith("-"):
            rem += 1
    return add, rem


def measures(rec):
    add, rem = diff_counts(rec.get("diff"))
    sig = rec.get("signals") or {}
    return {
        "resp": len(rec.get("response") or ""),
        "churn": add + rem,
        "added": add,
        "removed": rem,
        "files": sig.get("changed_files", len({
            l.split(" b/")[-1] for l in (rec.get("diff") or "").splitlines()
            if l.startswith("diff --git")
        })),
        "new_files": sig.get("new_files", 0),
        "elapsed": rec.get("elapsed_s") or 0.0,
        "verdict": sig.get("machine_verdict"),
        "empty": 1 if add + rem == 0 else 0,
    }


def load(base):
    out = {}
    for host in HOSTS:
        for path in sorted((base / host).glob("*.json")):
            rec = json.loads(io.open(path, encoding="utf-8").read())
            out[(host, rec["case"], rec["run"])] = measures(rec)
    return out


def perm_p(diffs, draws=DRAWS):
    """Two-sided sign-flip permutation p for a mean difference of zero."""
    n = len(diffs)
    if n == 0:
        return float("nan")
    obs = abs(st.mean(diffs))
    hits = 0
    for _ in range(draws):
        s = sum(d if random.getrandbits(1) else -d for d in diffs)
        if abs(s / n) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (draws + 1)


def boot_ci(diffs, draws=10_000, alpha=0.05):
    n = len(diffs)
    means = sorted(st.mean(random.choices(diffs, k=n)) for _ in range(draws))
    lo = means[int(alpha / 2 * draws)]
    hi = means[int((1 - alpha / 2) * draws) - 1]
    return lo, hi


def cells(data):
    grouped = {}
    for (host, case, _run), m in data.items():
        grouped.setdefault((host, case), []).append(m)
    return grouped


def main():
    on, off = load(ON), load(OFF)
    common = sorted(set(on) & set(off))
    print(f"ON runs {len(on)}   OFF runs {len(off)}   paired runs {len(common)}")
    missing = sorted(set(on) - set(off))
    if missing:
        print(f"MISSING OFF runs ({len(missing)}): {missing[:8]}{' ...' if len(missing) > 8 else ''}")

    on_c, off_c = cells({k: on[k] for k in common}), cells({k: off[k] for k in common})
    keys = sorted(set(on_c) & set(off_c))
    print(f"paired cells {len(keys)}\n")

    print("delta = OFF - ON.  positive => the base host did MORE of it without the policy.\n")
    metrics = [("resp", "response chars"), ("churn", "diff churn lines"),
               ("added", "lines added"), ("files", "files changed"),
               ("new_files", "new files"), ("elapsed", "elapsed s")]

    for scope in ("both", "claude", "codex"):
        sel = [k for k in keys if scope == "both" or k[0] == scope]
        print(f"== {scope}   n={len(sel)} cells")
        print("   %-17s %10s %10s %10s %8s %20s %8s"
              % ("metric", "ON mean", "OFF mean", "delta", "delta %", "95% CI of delta", "perm p"))
        for key, label in metrics:
            a = [st.mean([m[key] for m in on_c[k]]) for k in sel]
            b = [st.mean([m[key] for m in off_c[k]]) for k in sel]
            d = [y - x for x, y in zip(a, b)]
            ma, mb = st.mean(a), st.mean(b)
            lo, hi = boot_ci(d)
            pct = (mb - ma) / ma * 100 if ma else float("nan")
            print("   %-17s %10.1f %10.1f %+10.1f %+7.1f%% %9.1f .. %+8.1f %8.4f"
                  % (label, ma, mb, st.mean(d), pct, lo, hi, perm_p(d)))
        print()

    print("== machine verdicts (first pass only: FAIL is settled, REVIEW is not a verdict)")
    for host in HOSTS:
        sel = [k for k in common if k[0] == host]
        for arm, data in (("ON ", on), ("OFF", off)):
            counts = {}
            for k in sel:
                counts[data[k]["verdict"]] = counts.get(data[k]["verdict"], 0) + 1
            print("   %-7s %s  %s" % (host, arm, dict(sorted(counts.items(), key=lambda x: str(x[0])))))
    flips = [(k, on[k]["verdict"], off[k]["verdict"]) for k in common
             if on[k]["verdict"] != off[k]["verdict"]]
    print(f"\n   runs whose machine verdict differs: {len(flips)} / {len(common)}")
    for k, a, b in flips:
        print("     %-7s %-12s r%d   ON %-7s -> OFF %-7s" % (k[0], k[1], k[2], a, b))

    print("\n== empty-diff runs (model touched no file)")
    for host in HOSTS:
        sel = [k for k in common if k[0] == host]
        print("   %-7s ON %2d / %2d   OFF %2d / %2d"
              % (host, sum(on[k]["empty"] for k in sel), len(sel),
                 sum(off[k]["empty"] for k in sel), len(sel)))

    print("\n== per-cell response chars and churn (ON -> OFF)")
    print("   %-7s %-12s %18s %16s" % ("host", "case", "resp ON -> OFF", "churn ON -> OFF"))
    for k in keys:
        a_r = st.mean([m["resp"] for m in on_c[k]])
        b_r = st.mean([m["resp"] for m in off_c[k]])
        a_c = st.mean([m["churn"] for m in on_c[k]])
        b_c = st.mean([m["churn"] for m in off_c[k]])
        print("   %-7s %-12s %8.0f -> %-8.0f %7.1f -> %-7.1f" % (k[0], k[1], a_r, b_r, a_c, b_c))


if __name__ == "__main__":
    main()
