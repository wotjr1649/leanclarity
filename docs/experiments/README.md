# LeanClarity compression pilot

Not release evidence. Nothing here is part of the candidate distribution byte set,
and no result here changes a GO gate. The frozen candidate stays `1.0.1`
(`07C93E43D22B20AF651702059ACEC3D5FDDB837F8EB78BBC2A4334343045F4D0`) unless a
winning level is promoted through the normal SPEC/PLAN path.

## Question

Does a compressed policy hold the behavior the canonical policy holds, at a
token saving that is worth a SPEC revision?

## Ladder

| Level | Rule | Main bytes | Saving |
|---|---|---:|---:|
| L0 | canonical `policies/*.md` | 2486 | - |
| L1 | wording only: every SPEC 6.1/6.2 behavior and every trigger noun preserved, connective prose and duplicate clauses removed | 2219 | 10.7% |
| L2 | item merging: overlapping items merged (Engineering 8 to 7, Guidance 10 to 7), trigger nouns preserved. Normative, would need a SPEC revision | 2085 | 16.1% |
| L3 | enumerated noun lists replaced by summary terms | 1099 | 55.8% |

## Grounds for the ladder

Published work separates an instruction module, which is highly sensitive to
compression, from a context module, which is not; the large compression ratios
reported for prompt compression are context ratios. Connective prose and
explanatory narrative are the safe target; enumerated requirements, concrete
examples and constraint specifications are not, and constraint compliance
degrades before semantic accuracy does. LeanClarity is entirely instruction, so
the ladder is built to cross that boundary deliberately at L3 and to stay inside
it at L1.

Sources consulted 2026-08-29:
- <https://arxiv.org/pdf/2512.17920> instruction-following vs semantic accuracy under compression
- <https://www.microsoft.com/en-us/research/blog/llmlingua-innovating-llm-efficiency-with-prompt-compression/> LLMLingua
- <https://arxiv.org/pdf/2403.12968> LLMLingua-2
- <https://arxiv.org/pdf/2604.02985> prompt compression in the wild

## Measured consequence

L1 and L2 save roughly 60 to 100 tokens per injection. Only L3 saves enough to
matter, and L3 is the level the literature predicts will break. The pilot is
therefore effectively a single sharp question about L3.

## Artifacts

| Path | What it is |
|---|---|
| `PROTOCOL.md` | how the 144 runs are produced and judged, frozen |
| `fixtures/cases.jsonl` | the six frozen cases: prompt, positive predicates, forbidden outcomes, machine signals |
| `fixtures/<CASE>/workspace/` | that case's synthetic codebase |
| `fixtures/<CASE>/check.py` | that case's executable oracle, where one exists |
| `fixtures/MANIFEST.md` | SHA-256 of every fixture byte, frozen before the first run |
| `harness/pilot.py` | build arms, freeze the manifest, run one cell, score every record |
| `harness/build_cases.py` | regenerates `cases.jsonl`; rerunning must reproduce the same bytes |
| `runs/<host>/<arm>/` | one JSON record per run: response, diff, oracle output |
| `SPEC-succession-rule-draft.md` | proposed SPEC 17.1, not in force |

## Pre-committed rules

- Acceptance is regression-free smoke only: a level passes if every case L0
  passed also passes. No improvement and no equivalence is claimed.
- One pass of the ladder. The winner is the most compressed level that did not
  regress. No mid-experiment level is added.
- If L1 regresses, compression is abandoned and 1.0.1 stands.
- Oracles and fixtures are frozen before the first run and are not edited after
  seeing a response.
