# LeanClarity Engineering Policy

- Understand the request and its execution flow before simplifying: inspect affected callers and shared paths, then fix the smallest shared root cause rather than only the reported symptom.
- If the user asked only for analysis, explanation, reporting, or review, do not mutate code.
- Add nothing the requested outcome does not require: no speculative scaffolding, no one-use abstraction, future-only configuration, wrapper, provider, factory, or file split.
- Prefer in order: existing project code, standard library, native platform, already-installed dependency, minimum new implementation.
- Optimize for the smallest correct change, not the shortest-looking diff.
- Never simplify away trust-boundary validation, security controls, correctness guards, data-loss prevention, accessibility, or failure handling.
- For non-trivial logic such as a branch, loop, parser, or security-sensitive path, leave the smallest runnable check that fails if the behavior regresses.
