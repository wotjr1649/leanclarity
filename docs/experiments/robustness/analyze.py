"""Robustness analysis, exactly as PROTOCOL.md fixed it.

Paired unit is a cell (case x host), n = 8, six ON runs against six OFF runs.
Both tests are exact by enumeration rather than sampling: Fisher for the machine
verdict, and a full enumeration of all C(12,6) = 924 label splits for the
continuous measures. Holm across the family. alpha = 0.05.

Six against six only resolves near-total separation: 6/6 vs 0/6 gives a two-sided
p of 0.0022, 5/6 vs 1/6 gives 0.08. That ceiling is why six runs were bought and
it is stated in the protocol rather than discovered here.
"""
import io, json, glob
from itertools import combinations
from math import comb
from pathlib import Path
import statistics as st

ROOT = Path(__file__).resolve().parents[3]
RUNS = Path(__file__).resolve().parent / "runs"
CASES = ("BEH-ENG-05", "BEH-GUI-07", "BEH-SAFE-02", "BEH-ENG-06")
HOSTS = ("claude", "codex")

PREDICTIONS = {
    ("BEH-ENG-05", "codex"): "no separation - ponytail states Engineering 8 near-verbatim",
    ("BEH-ENG-05", "claude"): "no separation - same, and the case fails on Claude regardless",
    ("BEH-GUI-07", "claude"): "both arms fail",
    ("BEH-GUI-07", "codex"): "both arms fail",
    ("BEH-SAFE-02", "claude"): "no separation - ponytail P18 is in the stand-in",
    ("BEH-SAFE-02", "codex"): "no separation - ponytail P18 is in the stand-in",
    ("BEH-ENG-06", "claude"): "separation possible - E2 is in neither upstream",
    ("BEH-ENG-06", "codex"): "separation possible - E2 is in neither upstream",
}


def churn(diff: str) -> int:
    n = 0
    for line in (diff or "").splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith(("+", "-")):
            n += 1
    return n


def load():
    out = {}
    for path in sorted(glob.glob(str(RUNS / "*" / "*" / "*.json"))):
        d = json.loads(io.open(path, encoding="utf-8").read())
        out.setdefault((d["case"], d["host"], d["arm"]), []).append({
            "run": d["run"],
            "verdict": (d.get("signals") or {}).get("machine_verdict"),
            "resp": len(d.get("response") or ""),
            "churn": churn(d.get("diff")),
            "elapsed": d.get("elapsed_s") or 0.0,
        })
    for v in out.values():
        v.sort(key=lambda x: x["run"])
    return out


def fisher_two_sided(a, b, c, d):
    """2x2 [[a,b],[c,d]]. Sum hypergeometric tables no more likely than observed."""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    def p(x):
        return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)
    obs = p(a)
    lo = max(0, c1 - (n - r1))
    hi = min(r1, c1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs + 1e-12))


def perm_exact(on_vals, off_vals):
    """Exact two-sided permutation p for a difference in means, all splits."""
    pool = list(on_vals) + list(off_vals)
    k = len(on_vals)
    obs = abs(st.mean(on_vals) - st.mean(off_vals))
    idx = range(len(pool))
    total = hits = 0
    for pick in combinations(idx, k):
        s = set(pick)
        a = [pool[i] for i in idx if i in s]
        b = [pool[i] for i in idx if i not in s]
        total += 1
        if abs(st.mean(a) - st.mean(b)) >= obs - 1e-9:
            hits += 1
    return hits / total


def holm(pairs):
    """pairs: list of (label, p). Returns dict label -> adjusted p."""
    ordered = sorted(pairs, key=lambda x: x[1])
    m = len(ordered)
    adj, running = {}, 0.0
    for i, (label, p) in enumerate(ordered):
        running = max(running, min(1.0, (m - i) * p))
        adj[label] = running
    return adj


def main():
    data = load()
    print("== coverage")
    complete = []
    for case in CASES:
        for host in HOSTS:
            on = data.get((case, host, "on"), [])
            off = data.get((case, host, "off"), [])
            flag = "" if len(on) == len(off) == 6 else "   INCOMPLETE"
            print(f"   {case:<12} {host:<7} ON {len(on)}  OFF {len(off)}{flag}")
            if len(on) == len(off) == 6:
                complete.append((case, host))
    if not complete:
        print("\nno complete cells yet")
        return

    print("\n== machine verdicts per cell (run order)")
    raw = []
    for case, host in complete:
        on = data[(case, host, "on")]
        off = data[(case, host, "off")]
        seq = lambda v: "".join(x["verdict"][0] for x in v)
        a = sum(1 for x in on if x["verdict"] == "PASS")
        c = sum(1 for x in off if x["verdict"] == "PASS")
        p = fisher_two_sided(a, 6 - a, c, 6 - c)
        raw.append((f"verdict:{case}:{host}", p))
        print(f"   {case:<12} {host:<7} ON {seq(on)}  OFF {seq(off)}   "
              f"PASS {a}/6 vs {c}/6   fisher p={p:.4f}")

    print("\n== continuous, delta = ON - OFF  (negative: LeanClarity produced less)")
    print("   %-12s %-7s %-8s %9s %9s %9s %8s" % ("case", "host", "metric", "ON", "OFF", "delta", "exact p"))
    for case, host in complete:
        on = data[(case, host, "on")]
        off = data[(case, host, "off")]
        for key in ("resp", "churn"):
            a = [x[key] for x in on]
            b = [x[key] for x in off]
            p = perm_exact(a, b)
            raw.append((f"{key}:{case}:{host}", p))
            print("   %-12s %-7s %-8s %9.1f %9.1f %+9.1f %8.4f"
                  % (case, host, key, st.mean(a), st.mean(b), st.mean(a) - st.mean(b), p))

    adj = holm(raw)
    sig = [(k, p, adj[k]) for k, p in raw if adj[k] < 0.05]
    print(f"\n== Holm over {len(raw)} tests, alpha 0.05")
    if sig:
        for k, p, q in sorted(sig, key=lambda x: x[2]):
            print(f"   SIGNIFICANT  {k:<32} raw {p:.4f}  adj {q:.4f}")
    else:
        print("   nothing survives correction")
        best = min(raw, key=lambda x: x[1])
        print(f"   smallest raw p: {best[0]} = {best[1]:.4f} (adj {adj[best[0]]:.4f})")

    print("\n== pre-registered predictions")
    for case, host in complete:
        on = data[(case, host, "on")]
        off = data[(case, host, "off")]
        a = sum(1 for x in on if x["verdict"] == "PASS")
        c = sum(1 for x in off if x["verdict"] == "PASS")
        p = adj[f"verdict:{case}:{host}"]
        separated = p < 0.05
        pred = PREDICTIONS[(case, host)]
        expected_sep = pred.startswith("separation possible")
        both_fail = a == 0 and c == 0
        if pred == "both arms fail":
            held = both_fail
        else:
            held = separated == expected_sep
        print(f"   {case:<12} {host:<7} {'HELD ' if held else 'BROKE'}  "
              f"ON {a}/6 OFF {c}/6 adj p={p:.4f}  <- {pred}")


if __name__ == "__main__":
    main()
