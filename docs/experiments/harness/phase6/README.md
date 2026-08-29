# Phase 6 host matrix scripts

The scripts that produced the `HOST INTEGRATION GO` rows in
[`docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`](../../../evidence/LeanClarity_v1.0_GO_EVIDENCE.md)
under `Phase 6 row coverage`, against candidate `1.0.2` on Windows 11 Pro `10.0.26200` x64 with
Claude Code `2.1.251` and Codex CLI `0.150.1`.

Tracked so the gate rows are reproducible. They are evidence scaffolding, not part of the
candidate distribution byte set.

| Script | Rows it produces |
|---|---|
| `claude_phase6.py` | Claude matrix: discovery, `startup`/`resume`/`fork` sources, three commands, near match, OFF persistence, `SubagentStart` scope, invalid state, invalid policy, host control, context limit |
| `claude_compact.py` | Claude `SessionStart:compact`, reached by pushing a large fixture through `--resume` under `--autocompact 100000` |
| `codex_rest.py` | Codex near match, hook control, invalid state, subagent delegation |
| `codex_gaps.py` | Codex subagent under OFF, corrupted policy all-or-nothing |
| `codex_compact.py` | Codex `compact` and `clear` sources |
| `crosshost.py` | Cross-host state isolation, both directions |

## Running

Each script derives the repository root from its own location and writes only under `.pilot/`,
which is gitignored and machine-local. `.pilot/` must hold two authenticated isolated profiles:

```
CLAUDE_CONFIG_DIR=<repo>/.pilot/claude-config claude auth login
CODEX_HOME=<repo>/.pilot/codex-home codex login
```

Without them Claude has no credentials and every Codex request is `401 Unauthorized`. The
isolation, the required flags and the measured host constraints are documented in
[`docs/experiments/PROTOCOL.md`](../../PROTOCOL.md).

The pinned model in `claude_phase6.py` is the one Phase 6 was run under. Phase 6 observes hook
wiring, state and lifecycle, none of which read policy text or depend on the model. Phase 7 pins
different models for a different reason — see
[`LeanClarity_v1.0_PHASE7_PROTOCOL.md`](../../../evidence/LeanClarity_v1.0_PHASE7_PROTOCOL.md).

One-off evidence-patching scripts from the same session are deliberately not tracked; they edited
the evidence document and reproduce nothing.
