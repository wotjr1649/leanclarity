# LeanClarity

LeanClarity is default-on, opt-out development guidance for Claude Code and Codex. It steers the model toward the smallest correct engineering solution and clear, actionable communication.

LeanClarity is model-interpreted guidance, not deterministic enforcement, a correctness guarantee, a security boundary, or a compliance control. Host instructions, permissions, trust, sandboxing, and managed policy remain authoritative.

## How it applies

The host must install, enable, trust, and run the plugin hooks. That host readiness is separate from LeanClarity's Saved setting, which defaults to `ON` when `state.json` is absent under a valid plugin-data root.

- Main context while ON: Engineering Policy, then Guidance Policy.
- New subagent context while ON: Engineering Policy only.
- OFF: no LeanClarity policy injection.

Canonical policy sources are [Engineering Policy](policies/engineering.md) and [Guidance Policy](policies/guidance.md).

## Control prompts

Submit one of these plain prompts:

```text
leanclarity
leanclarity on
leanclarity off
```

LeanClarity applies `trim()` and `toLowerCase()` to the whole prompt, then requires an exact match. `/leanclarity`, `leanclarity status`, punctuation, extra tokens, internal newlines, aliases, and mentions inside a sentence are ordinary prompts.

`leanclarity` reports the Saved setting and its application boundaries without claiming the current conversation is exactly ON or OFF. `on` and `off` save a verified boolean. Each recognized control prompt is blocked from the model conversation after hook handling.

## Saved setting and context boundaries

Each host owns one independent file at `<host plugin data>/state.json` with exactly one boolean key, `enabled`. Claude and Codex do not synchronize it. Deleting that host's state resets the defined default to ON.

Saved-setting changes are not retroactive:

- A successful new chat/session `startup` or `/clear` is a clean Main boundary.
- `resume` and `compact` are inherited boundaries; prior context can remain.
- Claude `fork` is also inherited. Codex `fork` is not claimed by v1.
- A newly started subagent reads the Saved setting immediately without waiting for a clean Main boundary.

Every new eligible `SessionStart` or `SubagentStart` invocation rereads the Saved setting.

## Failure behavior

- An ordinary prompt remains fail-open and is never blocked by an internal LeanClarity failure.
- A recognized control prompt remains blocked even when state handling fails, and receives a fixed bounded error instead of raw prompt, path, state, or exception data.
- Corrupt or unreadable state is never guessed as ON or OFF. Exact `on`/`off` can repair absent or byte-readable regular invalid state, but never a directory, link, reparse point, other non-regular target, or unreadable I/O target.
- Main policy injection is all-or-nothing: invalid Engineering or Guidance means neither is injected. A subagent requires only a valid Engineering Policy.
- Existing contexts are not rewritten, canceled, or stripped when the Saved setting changes.

## Privacy and dependencies

The runtime uses the Node.js standard library only. It has no network, telemetry, analytics, database, registry, package dependency, transcript parsing, or global-host configuration fallback. Mutable state is written only to host-provided plugin data; the plugin root is read-only at runtime.

## Support status

LeanClarity v1 targets release validation on Windows 11 x64 with actual Claude Code, Codex, and their hook-launched Node.js version. macOS and Linux are portable-by-design but not release-validated. Local deterministic implementation evidence does not by itself grant host integration, release, or complete status.

The plugin itself does not install, enable, trust, disable, or uninstall plugins. Host uninstall and data-retention behavior must be verified on the exact host version; LeanClarity never deletes plugin data itself.

## Coexistence and provenance

LeanClarity does not detect, migrate, disable, or delete LeanCue, Ponytail, or i-have-adhd. If overlapping guidance is enabled, disable it manually through the host's own plugin controls.

LeanClarity is MIT licensed. Derived-policy attribution is in [Third-Party Notices](THIRD_PARTY_NOTICES.md). The normative product contract is the [LeanClarity v1.0 SPEC](docs/specs/LeanClarity_v1.0_SPEC.md), and implementation gates are in the [LeanClarity v1.0 PLAN](docs/plans/LeanClarity_v1.0_PLAN.md).
