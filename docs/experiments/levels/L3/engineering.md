# LeanClarity Engineering Policy

- Understand the execution flow and shared callers before simplifying; fix the shared root cause, not the reported symptom.
- Analysis-only requests get analysis, not code changes.
- Add nothing the outcome does not require: no speculative scaffolding, no single-use indirection.
- Reuse before building: existing code, then platform, then dependency, then new code.
- Smallest correct change, not the shortest diff.
- Never remove protective code to make something smaller.
- Leave a runnable check for non-trivial logic.
