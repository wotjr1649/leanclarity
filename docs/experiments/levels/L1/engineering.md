# LeanClarity Engineering Policy

- Understand the request and its execution flow before simplifying. Inspect affected callers and shared paths before changing a shared contract.
- If the user asked only for analysis, explanation, reporting, or review, do not mutate code.
- Skip features and scaffolding the requested outcome does not require.
- Prefer in order: existing project code, standard library, native platform, already-installed dependency, minimum new implementation.
- Do not add a one-use abstraction, future-only configuration, wrapper, provider, factory, or file split without present need.
- Fix the smallest shared root cause, not just the reported symptom. Optimize for the smallest correct change, not the shortest-looking diff.
- Never simplify away trust-boundary validation, security controls, correctness guards, data-loss prevention, accessibility, or failure handling.
- For non-trivial logic such as a branch, loop, parser, or security-sensitive path, leave the smallest runnable check that fails if the behavior regresses.
