# Draft SPEC amendment — policy-only revision succession

Not in force. This is proposed text for `docs/specs/LeanClarity_v1.0_SPEC.md`. SPEC
section 17 requires a new document version and updated tests/evidence for any normative
change, so nothing here applies until the user accepts it and it is written into the SPEC.

## Why

Without this rule, every compression candidate re-runs the whole PLAN Phase 6 host matrix
even though none of those rows reads policy text. The rule names exactly what may be
inherited and exactly what must be re-run, so a policy-only change costs a context
measurement and a behavior gate rather than a full host re-observation.

The rule buys nothing today: Phase 6 is `BLOCKED` on Claude and two rows short on Codex,
and there is nothing to inherit from a gate that is not yet closed. Its value is entirely
prospective.

## Proposed text — new SPEC section 17.1

> ### 17.1 Policy-only revision succession
>
> A **policy-only revision** is a candidate whose distribution byte set differs from an
> already host-verified predecessor candidate in `policies/engineering.md`,
> `policies/guidance.md`, or both, and in no other file. Every other candidate
> distribution byte — both manifests, `hooks/hooks.json`, `hooks/leanclarity.cjs`,
> `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md` — must be byte-identical to the
> predecessor's.
>
> For a policy-only revision, the predecessor's `HOST INTEGRATION GO` observations are
> inherited for: plugin discovery and trust; hook map registration; event dispatch;
> `SessionStart` source classification and the clean/inherited boundary table of
> section 8.2; exact-command interception and prompt blocking; Saved-setting read,
> write, readback and cross-session persistence; state validity and atomic replace;
> data-root ownership and creation; Subagent scope; and host control when the plugin or
> its hooks are disabled, untrusted or unavailable. Each of those is determined by the
> runtime, the hook map and the manifests, none of which changed, and none of them reads
> policy text.
>
> The following are **not** inherited and must be observed on the revision itself before
> its `HOST INTEGRATION GO`:
>
> - the section 11 context measurement of every canonical file and both compositions;
> - the host context-limit observation for both hosts, that is no Claude file-preview
>   replacement and no Codex `additionalContext` spill at the actual composed size.
>
> Section 15 behavior acceptance is outside this rule. Model output behavior is exactly
> what policy text owns, so a policy-only revision runs the section 15 gate in full as
> any other candidate does.
>
> Inheritance requires all of the following, recorded in the revision's evidence:
>
> - the predecessor rows being inherited were `PASS`, not `BLOCKED` or `NOT RUN`, on a
>   frozen candidate whose aggregate hash is recorded;
> - both aggregate hashes and the per-file byte set of each are recorded;
> - the difference between the two byte sets is shown to be confined to the two policy
>   files;
> - the host, host version and surface of the inherited observation are unchanged. A
>   different host, a different host version, or a surface the predecessor did not
>   exercise inherits nothing.
>
> Inheritance never converts a predecessor's `BLOCKED`, `NOT RUN` or `HOLD` row into a
> `PASS`, and never substitutes for an observation the predecessor never made.

## Consequential edits if accepted

| Location | Change |
|---|---|
| Section 0 | document version `1.2` |
| Section 2.3 | one sentence pointing at 17.1 for the inheritance boundary |
| Section 11 | note that context measurement is never inherited across a policy change |
| Section 17 | the new 17.1 subsection |
| Section 19 | revision-history row for `1.2` |
| PLAN Phase 6 | an entry rule naming 17.1, so a policy-only revision enters Phase 6 with the inherited rows already `PASS` and only the measurement rows open |
| GO evidence | a succession block naming the predecessor hash, the inherited rows and the re-run rows |
| `tests/leanclarity.test.cjs` | the SPEC/PLAN hash pins in the evidence test move to the new documents |

## Open question for the user

Should the rule also allow inheritance in the other direction, that is a predecessor
that is a compressed level and a successor that restores canonical text? The draft is
written symmetrically — it turns only on the byte-set difference, not on which side is
shorter — but say so if you want it restricted to one direction.
