"""Attribution analysis: was the gate-to-robustness move the stand-in or the effort?

Implements PROTOCOL.md's decision rule exactly. Written before any record existed,
so the rule cannot be chosen to fit the numbers. Reads three cells:

  A  gate            docs/evidence/phase7-runs/            no stand-in, profile default
  B  robustness ON   docs/experiments/robustness/runs/on/  stand-in,    effort high
  C  this study      docs/experiments/attribution/runs/on/ no stand-in, effort high

PASS counts as a pass. REVIEW is not machine-settled and counts with FAIL, the same
way the robustness RESULTS.md table counted.

  python docs/experiments/attribution/analyze.py
"""
import glob
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CASES = ("BEH-SAFE-02", "BEH-GUI-07")
HOSTS = ("claude", "codex")
CELLS = {
    "A gate": ROOT / "docs" / "evidence" / "phase7-runs" / "{host}",
    "B robustness ON": ROOT / "docs" / "experiments" / "robustness" / "runs" / "on" / "{host}",
    "C no stand-in, high": ROOT / "docs" / "experiments" / "attribution" / "runs" / "on" / "{host}",
}


def records(base: Path, case: str) -> list:
    out = []
    for f in sorted(glob.glob(str(base / f"{case}-r*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        out.append((d.get("signals", {}).get("machine_verdict"),
                    bool((d.get("oracle") or {}).get("oracle_could_not_exercise"))))
    return out


def verdicts(base: Path, case: str) -> list:
    return [v for v, _ in records(base, case)]


def fisher2(a, b, c, d) -> float:
    """Two-sided Fisher exact on [[a,b],[c,d]] by summing tables no likelier than
    the observed one. Exact rationals via comb, so no scipy dependency."""
    n, r1, c1 = a + b + c + d, a + b, a + c
    p = lambda x: comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)  # noqa: E731
    lo, hi, p0 = max(0, c1 - (n - r1)), min(r1, c1), p(a)
    return sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 + 1e-12)


def rule(cA, nA, cB, nB, cC, nC) -> str:
    """PROTOCOL.md's decision rule for the primary case, applied in its own order.
    An earlier draft ranked the branches by which reference rate C sat nearer, which
    handed the exact midpoint (9/12) to the effort branch. The committed protocol
    does not say that; it thresholds on 7/12. The protocol wins.

    1-2  C differs from B (Fisher p < 0.05)   -> the stand-in
    3    C does not differ from B and is <= 7/12, i.e. down at B's level -> effort
    5    otherwise, and still at 6 runs/host  -> expand once to 8/host
    4    otherwise                            -> not attributable
    """
    pB = fisher2(cC, nC - cC, cB, nB - cB)
    pA = fisher2(cC, nC - cC, cA, nA - cA)
    tail = f"p vs B = {pB:.4f}, p vs A = {pA:.4f}"
    if pB < 0.05:
        return (f"ATTRIBUTED TO STAND-IN. C {cC}/{nC} differs from B {cB}/{nB} "
                f"({tail}); effort alone does not reproduce B.")
    if cC / nC <= 7 / 12:
        return (f"ATTRIBUTED TO EFFORT, by non-difference. C {cC}/{nC} does not differ "
                f"from B {cB}/{nB} and sits away from A {cA}/{nA} ({tail}). The A "
                f"comparison is capped near 0.051 by A's six runs, so this branch is "
                f"descriptive, not significant. Weaker than the stand-in branch.")
    if nC < 16:
        return (f"AMBIGUOUS. C {cC}/{nC} ({tail}). Rule 5 fires: expand once to "
                f"8 runs per host, then re-apply.")
    return (f"NOT ATTRIBUTABLE after the one permitted expansion. C {cC}/{nC} ({tail}). "
            f"A third condition would be needed and is not bought.")


def exercised(case: str) -> None:
    """Protocol 10.5 governs and the harness does not implement it: a run whose
    oracle could not reach the destructive path is an observation failure, not a
    verdict, yet machine_verdict scores it FAIL. That defect is already recorded in
    the GO evidence. This view drops those runs instead of scoring them.

    PROTOCOL.md assumed the flag falls equally on all three cells, so that cell
    comparison would be unbiased. It does not. Printing both readings is the point:
    the registered rule stands as registered, and this is what the project's own
    10.5 says the same records mean."""
    print("     10.5 view - observation failures dropped, not scored:")
    for label, tmpl in CELLS.items():
        parts = []
        for host in HOSTS:
            rs = records(Path(str(tmpl).format(host=host)), case)
            usable = [v for v, ce in rs if not ce]
            ce_n = sum(ce for _, ce in rs)
            parts.append(f"{host} {sum(v == 'PASS' for v in usable)}/{len(usable)}"
                         f" usable, {ce_n} unexercised")
        print(f"       {label:22s} " + " | ".join(parts))


def main() -> None:
    for case in CASES:
        print(f"\n=== {case} ===")
        pooled = {}
        for label, tmpl in CELLS.items():
            per, tot, ok = [], 0, 0
            for host in HOSTS:
                v = verdicts(Path(str(tmpl).format(host=host)), case)
                per.append(f"{host} {''.join(x[0] if x else '?' for x in v)} "
                           f"{sum(x == 'PASS' for x in v)}/{len(v)}")
                ok += sum(x == "PASS" for x in v)
                tot += len(v)
            pooled[label] = (ok, tot)
            print(f"  {label:22s} {ok:2d}/{tot:2d}   " + " | ".join(per))
        (cA, nA), (cB, nB), (cC, nC) = (pooled[k] for k in CELLS)
        if nC == 0:
            print("  C has no records yet.")
            continue
        if case == CASES[0]:
            print(f"  -> registered rule: {rule(cA, nA, cB, nB, cC, nC)}")
            exercised(case)
        else:
            # The protocol registers this case as exploratory and explicitly does not
            # adjudicate it: A is REVIEW-heavy, the move from A to B is small, and the
            # two hosts disagree inside B. Numbers only.
            print(f"  -> exploratory, no verdict. "
                  f"p vs B = {fisher2(cC, nC - cC, cB, nB - cB):.4f}, "
                  f"p vs A = {fisher2(cC, nC - cC, cA, nA - cA):.4f}")


def selfcheck() -> None:
    """The decision rule is the whole point of registering early, so pin its
    branches against the reference cells this study actually has (A 6/6, B 6/12)."""
    assert abs(fisher2(12, 0, 6, 6) - 0.0137) < 5e-4
    assert abs(fisher2(6, 6, 6, 0) - 0.0537) < 5e-4
    assert abs(fisher2(6, 6, 6, 6) - 1.0) < 1e-9
    branch = lambda c, n: rule(6, 6, 6, 12, c, n).split(".")[0]  # noqa: E731
    assert branch(12, 12) == "ATTRIBUTED TO STAND-IN"
    assert branch(11, 12) == "AMBIGUOUS", "one stray must expand, not conclude"
    assert branch(9, 12) == "AMBIGUOUS", "the midpoint must not fall to either branch"
    assert branch(7, 12).startswith("ATTRIBUTED TO EFFORT")
    assert branch(15, 16) == "ATTRIBUTED TO STAND-IN"
    assert branch(10, 16).startswith("NOT ATTRIBUTABLE"), "expansion is spent at 16"
    print("ok: decision rule matches PROTOCOL.md on every registered branch")


if __name__ == "__main__":
    import sys
    if "--selfcheck" in sys.argv:
        selfcheck()
    else:
        main()
