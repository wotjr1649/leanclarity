# Paired ON/OFF study — design, frozen before the results exist

Not release evidence. Nothing here is part of the candidate distribution byte set,
and no result here changes a GO gate. `LCL-BEH-001` stays `FAIL`, `RELEASE GO`
stays `NOT VERIFIED`, `COMPLETE GO` stays `NOT GRANTED`. This document is
committed before the run records land, so the analysis it fixes cannot have been
chosen after seeing the numbers.

## Question

Does injecting the canonical policy change what the model does, and by how much?
Improvement, parity, or regression.

SPEC 15.3 is why this exists: *"Paired ON/OFF evaluation 없이 README/release note에서
base host 대비 개선율이나 인과적 효과를 주장하지 않는다."* The GO evidence says three
separate times that no paired ON/OFF comparison was run. Nothing in this repository
has ever measured the base host. Every one of the 144 compression-pilot runs and all
102 Phase 7 runs had the policy ON.

## Arms

| Arm | Source | Runs |
|---|---|---|
| ON | `docs/evidence/phase7-runs/` — the recorded Phase 7 gate runs, reused, not re-run | 102 |
| OFF | `docs/experiments/onoff/runs/` — this study | 102 |

Identical in everything except the plugin's saved state: same 17 frozen fixtures at
aggregate `021323236FD175DF8A35D45DB257137096D1ACA5F7C2E46606F9681917449DA6`, same
candidate `99B19A9C…`, same pinned models (`claude-haiku-4-5-20251001`,
`gpt-5.6-luna` at effort `none`), same isolated profiles, same
`tests/behavior-fixtures/harness.py` invoked through its existing `--out` flag. The
harness is inside the fixture freeze and is not modified; `harness.py verify` must
still report `MATCH` after this study.

**OFF is `{"enabled": false}`, not an uninstalled plugin.** The hook still loads, the
plugin is still trusted, the hook map is still registered, the candidate bytes are
still delivered and verified before every run. Only the injection is gone. That
isolates the injection rather than the plugin's presence.

## Zero injection is proved, not assumed

`preflight.py` runs a probe that can only be answered one way if the policy is
absent and the other way if it is present: quote the first bullet of the
`LeanClarity Engineering Policy` section verbatim, or reply `NONE`. Protocol section
5.1 recorded why a yes/no probe is not enough — asked that way, both hosts returned a
false `YES` with the policy demonstrably absent. A verbatim quote cannot be produced
by agreement.

The probe is checked in both directions, because an oracle that cannot go positive is
as useless as one that cannot go negative:

| State | Claude `injected_chars` | Claude reply | Codex reply |
|---|---|---|---|
| ON | `[2486]` | first bullet, verbatim | first bullet, verbatim |
| OFF | `[]` | `NONE` | `NONE` |

Claude additionally self-proves on every recorded turn: `--debug-file` writes
`provided additionalContext (N chars)` only when the hook injected, so every OFF run
carries `injected_chars: []` in its own record. Codex exposes no equivalent counter
and is covered by the probe alone; `preflight-off.log` holds the observation taken
immediately before the batch.

## Paired unit and primary metrics

The paired unit is a **cell**: one case on one host, the mean of its three runs.
`n = 34` overall, `n = 17` per host.

Pairing is not optional here. Phase 7's own records give a between-cell sd of 934
response characters against a within-cell sd of 104 — a 9:1 ratio. An unpaired
comparison would measure which case is being run, not which arm.

| | Metric | Why |
|---|---|---|
| Primary | response characters | the output-length side the compression pilot found unresolvable at n=18 |
| Primary | diff churn lines (added + removed) | the Ponytail thesis is that less code gets written; this is that claim, directly |
| Secondary | lines added, files changed, new files, elapsed seconds | |

## Significance

Sign-flip permutation test on the 34 cell differences, 200,000 draws, two-sided,
seed `20260830`. No normality assumption: every cell's mean far exceeds its median,
and the compression pilot already recorded that this breaks parametric summaries.
Bootstrap 95% CI on the mean difference, 10,000 resamples. `alpha = 0.05`.

Sign convention: **delta = OFF − ON**. A positive delta means the base host did more
of it without the policy.

## Machine verdicts are reported, not scored

Protocol section 5 puts a machine signal above a screener only for what a diff or an
executable oracle settles; everything else is `REVIEW` and needs the two screeners.
**Tier 1 runs no screeners.** So the verdict distribution is reported as a shift
indicator and no pass rate, cell outcome or case result is computed from it. Doing
otherwise would be scoring a gate with half its ladder.

## Pre-declared expectation

Recorded now so the result is interpretable either way. The binary side is expected to
show no usable difference:

- `BEH-GUI-08` has no policy anchor and passed on both hosts — the base host already
  carries behaviour this suite tests.
- The compression pilot found `L3`, which deletes the enumerated nouns
  (`trust-boundary validation`, `accessibility`) outright at 55.8% compression,
  regressed on no case that `L0` passed.
- arXiv 2604.07192 measured no significant constraint-satisfaction difference across
  three encoding forms over 830+ invocations.
- Three of the five Phase 7 failures pass on Codex under byte-identical policy text.
- Protocol 10.6 fixes the arithmetic: at `p ≈ 0.96`, three runs per cell cannot see a
  16-point shift.

Nothing above predicts anything about the continuous metrics, which is the whole
reason they are primary.

## Stopping rule, fixed in advance

| Outcome on a primary metric | Action |
|---|---|
| `p < 0.01` | effect taken as real within this design's limits |
| `0.01 ≤ p ≤ 0.20` | Tier 2: interleaved ON+OFF, +102 runs, to remove window drift |
| `p > 0.20` and the 95% CI lies inside ±10% of the ON mean | record "no effect detectable at this power" and stop |
| `p > 0.20` with a wider CI | underpowered; record that, propose Tier 2, claim nothing |

Screeners run only if the machine verdicts move, and then only on discordant runs.

## What this study cannot say

- **The arms are not interleaved.** ON ran `2026-08-29 16:23-17:27Z`; OFF runs
  `2026-08-30 05:34-06:28Z`, about thirteen hours later.
  Window drift in the serving stack is a confound this design does not remove, and
  protocol 10.4 recorded 8 of 102 machine verdicts flipping between two runs of the
  same suite four bytes apart. A binary-side difference at or below that magnitude is
  not interpretable here. Tier 2 exists for exactly this.
- Nothing generalises past the two pinned models at their pinned settings, per
  protocol section 9. In particular it says nothing about the operator's real
  supported configuration.
- Seventeen synthetic cases chosen to probe SPEC 15.2 are not a sample of real work.
  A difference here is a difference on this suite.
- No result here grants, blocks or modifies any gate.
