# LeanClarity Engineering Policy

- Understand the request and its relevant execution flow before simplifying. Inspect affected callers and shared paths before changing a shared contract.
- If the user asked only for analysis, explanation, reporting, or review, do not mutate code or force an implementation.
- Skip features and scaffolding that are not required for the requested outcome.
- Prefer, in order: existing project code, the standard library, native platform features, an already-installed dependency, then the minimum new implementation.
- Do not add a one-use abstraction, future-only configuration, wrapper, provider, factory, or file split without a present need.
- Fix the smallest shared root cause instead of patching only the reported symptom. Optimize for the smallest correct change, not the shortest-looking diff.
- Never simplify away trust-boundary validation, security controls, correctness guards, data-loss prevention, accessibility, or failure handling needed to protect the result.
- For a non-trivial change such as a branch, loop, parser, or security-sensitive path, leave the smallest runnable check that would fail if the behavior regressed.
