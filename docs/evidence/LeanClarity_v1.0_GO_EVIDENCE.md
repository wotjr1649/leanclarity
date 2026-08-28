# LeanClarity v1.0 GO Evidence

## Scope of this record

This record covers PLAN Phases 1–5 and the local deterministic `IMPLEMENTATION GO` gate only. `PASS` in the requirement table means the stated Phase 1–5 deterministic slice passed on the frozen candidate. It does not substitute for the separate live-host, semantic, or final-release evidence listed as `NOT RUN` below.

Re-verified on 2026-08-29 after the marketplace catalogs described under Artifact were added for installs from the repository `https://github.com/wotjr1649/leanclarity` and the Phase 6 host workspaces were prepared. The candidate distribution byte set and its aggregate hash are unchanged; only verification assets (`tests/`), the catalogs, `INSTALL.md`, and this record changed.

## Artifact

- LeanClarity version: `1.0.0`
- Candidate root: `D:\AI_DEV\leancue`
- Candidate SHA-256: `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902`
- Candidate identity algorithm: sort the declared candidate paths; for each path emit UTF-8 `<path>\t<byte-count>\t<uppercase-file-SHA-256>\n`; hash those manifest bytes with SHA-256.
- Local OS/architecture: Microsoft Windows 11 Pro `10.0.26200`, x64
- Local Node.js: `v24.19.0`
- Claude Code: `2.1.250`; local strict validation of the plugin manifest and the marketplace catalog; installed for Phase 6 from the directory marketplace (see Claude host results), hook integration not yet observed
- Codex host/version/surface: Codex CLI `0.150.1`; local-path install observed only in a workspace-scoped `CODEX_HOME` (see Codex host results); git-marketplace install on the real profile and session hooks `NOT RUN`
- Model/settings used for behavior smoke: `NOT RUN`

### Candidate distribution byte set

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.claude-plugin/plugin.json` | 283 | `F002B0531D142134E677803F45DFC8066DD172212B7742A6D10DA124B8714318` |
| `.codex-plugin/plugin.json` | 251 | `D52C0CA1BCACD3F562A1F5DE62968AA7E6391E5F40618B1FCD5FCC41960118AD` |
| `LICENSE` | 1081 | `194235421910F63BCF96182F80497501CB54D562DD2F05EF5AE9C545A0EDDD2C` |
| `README.md` | 4481 | `CC5B6331DC7E00F94947476CF029B055CEF846C38B4361B7D0AD1CC540073B12` |
| `THIRD_PARTY_NOTICES.md` | 2734 | `B888BE73EA7F0D0D0A7AA13104A8B7D04E9F7FC4D2F09C098359B26EC26B3257` |
| `hooks/hooks.json` | 724 | `DAD1F45EB9BF28A518D386D7925D829EDCBC22DC25817509E4CC02CE323E66BF` |
| `hooks/leanclarity.cjs` | 11716 | `5CED21FA15CF725ACAEEA96DD7F49B7C393AF9095A6601693A8EC5BA1296E5BE` |
| `policies/engineering.md` | 1176 | `E819E185493315773449596FBCDF48219C12F65839FB1A094F757632257EAA25` |
| `policies/guidance.md` | 1309 | `D50C059F0498CEE86C8F36A57441ECF5C16827A21A17E1712DE15E57621ED7D8` |

`tests/` and `docs/evidence/` are verification assets and are not candidate distribution bytes.

### Marketplace catalogs and install notes (not distributed)

| Path | Host | Purpose |
|---|---|---|
| `.claude-plugin/marketplace.json` | Claude Code (Codex reads it as a legacy-compatible catalog) | Marketplace `leanclarity` whose single entry `leanclarity` uses `"source": "./"`; registered with `claude plugin marketplace add wotjr1649/leanclarity` (or the repository directory) |
| `.agents/plugins/marketplace.json` | Codex | Marketplace `leanclarity` whose single entry `leanclarity` uses the git source `https://github.com/wotjr1649/leanclarity.git` at `main`; registered with `codex plugin marketplace add wotjr1649/leanclarity` |
| `INSTALL.md` | operators | Install, update, and uninstall commands for both hosts until Phase 8 folds them into `README.md` |

The catalogs follow the pinned upstream repositories' layout (Ponytail and i-have-adhd ship the same two files with `source: "./"` and a git `url` source). They are excluded from the candidate distribution and its hash: the candidate byte-set test allowlists exactly these two paths, and a dedicated test pins their content to the candidate plugin identity and repository URL. A marketplace install from the repository root copies the whole repository (see host results), so an installed copy is a superset of the candidate; the runtime reads only its fixed policy paths and the host-provided data root.

## Source baseline

- Official documentation checked: `2026-08-28`; re-checked `2026-08-29` for Claude `--plugin-dir`, marketplace, and plugin-data behavior, the Codex catalog schema, and Codex hook events
- Repository: `https://github.com/wotjr1649/leanclarity` (private during Phases 6–7); the candidate aggregate hash above, not a commit, is the artifact identity
- OpenAI Codex hooks: https://learn.chatgpt.com/docs/hooks
- OpenAI plugin packaging: https://developers.openai.com/plugins/build/plugins
- Anthropic Claude Code hooks: https://code.claude.com/docs/en/hooks
- Anthropic plugin reference: https://code.claude.com/docs/en/plugins-reference
- Node.js file system API: https://nodejs.org/api/fs.html
- Canonical SPEC SHA-256: `0B633AEE5B54546F70FAB717DEEAF50B125529A0413DF5E1CA12E7BFA039955A`
- Canonical PLAN SHA-256: `E30B43CC3A6B43DF74BE1010BA916914DE913E92C1E9DC95D7C3BC81862713C7`
- Ponytail: https://github.com/DietrichGebert/ponytail at `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- i-have-adhd: https://github.com/ayghri/i-have-adhd at `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c`

## Requirement results

The artifact hash in every row is the aggregate candidate identity above.

| Requirement | Applicability rationale | Exact command/interaction | Artifact hash | Host/version/surface | Observation | Status | Evidence location |
|---|---|---|---|---|---|---|---|
| `LCL-PROD-001` | Phase 4 deterministic product copy and no-guarantee boundary | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local Node `v24.19.0` | README and manifests preserve identity, promise, and non-enforcement boundary | PASS | `README.md`; manifest and operator-documentation tests |
| `LCL-SCOPE-001` | Phase 4 support copy must not overclaim unrun platforms or hosts | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local docs only | Windows 11 x64 is the validation target; macOS/Linux and host integration remain unverified | PASS | `README.md` Support status; deferred-host table |
| `LCL-ARCH-001` | Complete Phase 1–5 artifact structure | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local Node `v24.19.0` | Two policies, one CJS runtime, no package/dependency/skill/framework artifact | PASS | candidate byte-set and package-surface tests |
| `LCL-ENG-001` | Phase 1 canonical policy content; semantic behavior is deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local policy review | Required engineering decisions and safety exceptions are present | PASS | `policies/engineering.md`; policy contract tests |
| `LCL-GUIDE-001` | Phase 1 canonical policy content; semantic behavior is deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local policy review | Required communication behavior and detail/safety exceptions are present | PASS | `policies/guidance.md`; policy contract tests |
| `LCL-POL-001` | Canonical source, exact composition, and Main all-or-nothing behavior | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local Node `v24.19.0` | Main contains each policy once and in order; Subagent contains Engineering once; invalid Main source emits neither | PASS | composition and fixed-policy-loading tests |
| `LCL-SWITCH-001` | Host-local boolean state implementation | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Task-owned Windows temp data | Absent is default ON; exact one-boolean schema; Claude/Codex paths remain independent by construction | PASS | absent-state and state-parser tests |
| `LCL-CMD-001` | Parser and block JSON are deterministic; live prompt erasure is deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local process dispatch | Only three normalized bare prompts match; recognized commands return top-level block and never echo prompt text | PASS | command-parser, exact-command, near-match, and process-command tests |
| `LCL-STATUS-001` | Fixed status reason contract | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local process dispatch | Reasons identify Saved ON/OFF plus boundaries and never claim exact Current/Desired context | PASS | exact-command and bounded-message tests |
| `LCL-LIFE-001` | Deterministic source allowlist and reread behavior; live source emission deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Synthetic Claude/Codex payloads | Claude and Codex allowlists differ exactly; every lifecycle dispatch rereads state | PASS | source-allowlist and lifecycle-reread tests |
| `LCL-SUB-001` | Deterministic Subagent composition | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Synthetic `SubagentStart` | ON emits Engineering only; OFF/invalid state emits no policy | PASS | composition, fixed-policy-loading, and lifecycle tests |
| `LCL-HOOK-001` | Shared hook-map schema; live discovery deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs`; `claude plugin validate <materialized candidate> --strict` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Node `v24.19.0`; Claude Code `2.1.250` validator | Exactly three synchronous command handlers use one quoted CJS path; strict Claude plugin-manifest validation passed on the materialized candidate byte set | PASS | `hooks/hooks.json`; shared-hook-map test; validator output |
| `LCL-RUN-001` | Production runtime/import surface | `node --check hooks/leanclarity.cjs`; `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local Node `v24.19.0` | Syntax passed; imports are only `node:fs`, `node:path`, and `node:util`; import is side-effect free | PASS | runtime static/import tests; 349-line runtime observation |
| `LCL-INPUT-001` | Bounded strict process input | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local child processes, Node `v24.19.0` | Fatal UTF-8, BOM, JSON/object, exact 1 MiB, oversized, complete/partial no-EOF, and about-1-second deadline cases passed | PASS | strict-input, BOM, oversized-process, and no-EOF tests |
| `LCL-OUTPUT-001` | Deterministic stdout shape; live host consumption deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local child processes | Output is empty or one parseable JSON object; context output uses the actual event name; no banner/log/stack | PASS | emit, production-entrypoint, and fail-open tests |
| `LCL-STATE-001` | Strict state, native replace, readback, and concurrency | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Windows 11 Pro; Node `v24.19.0`; task-owned temp data | Native rename replaced existing state without pre-delete; five pre-replace failure seams preserved target; readback and opposing writers remained truthful/valid | PASS | atomic-state, injected-failure, readback, and concurrent-writer tests |
| `LCL-FAIL-001` | Deterministic failure matrix | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local synthetic/process cases | Ordinary prompts fail open; recognized commands block on errors; corrupt/unreadable/non-regular policy/state behavior matches contract | PASS | policy/state failure, command-error, and ordinary-prompt tests |
| `LCL-MEASURE-001` | Local context measurement only; live Claude/Codex limit behavior deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local UTF-8/code-point measurement | Engineering `1175/1175`, Guidance `1308/1308`, Main `2486/2486`, Subagent `1176/1176` bytes/code points after canonical trim/composition | PASS | context-measurement diagnostics below |
| `LCL-SEC-001` | Phase 2–5 static/adversarial privacy and mutation surface | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local runtime/process audit | No prohibited execution/egress/database/persistence/fallback API; prompt/session/path markers are neither echoed nor persisted; plugin root is unchanged by commands | PASS | production static, process non-disclosure, and plugin-root immutability tests |
| `LCL-PKG-001` | Local manifests, paths, README, candidate bytes, and the local catalog; live Codex session discovery deferred | `node --test --test-concurrency=1 tests/leanclarity.test.cjs`; `claude plugin validate <materialized candidate> --strict`; `claude plugin validate . --strict`; workspace-`CODEX_HOME` `codex plugin marketplace add` / `list` / `add` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Node `v24.19.0`; Claude Code `2.1.250` validator; Codex CLI `0.150.1` workspace home | Three candidate JSON files parse; metadata agrees; shared paths exist; README matches behavior; strict Claude validation passed for the plugin manifest (materialized candidate) and the marketplace catalog (repo root); the local catalog names only `leanclarity` and stays out of the candidate; Codex discovered and installed `leanclarity@leancue` `1.0.0` from the Phase 6 workspace catalog with exactly the nine candidate files | PASS | manifest, hook-map, README, candidate, catalog, JSON/link tests; Codex host results |
| `LCL-MIG-001` | No automatic migration/coexistence mutation | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local source/docs audit | No old alias/state import/detection code; README provides manual host-control guidance only | PASS | README coexistence section; production static/package tests |
| `LCL-LIC-001` | Distribution license and pinned attribution | `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Local artifact audit | LeanClarity MIT license and two complete upstream MIT notices, URLs, revisions, copyrights, and derived-policy paths are present | PASS | `LICENSE`; `THIRD_PARTY_NOTICES.md`; notice test |
| `LCL-BEH-001` | Requires Phase 7 real-host/model 3-run semantic smoke | Not run — PLAN Phase 7 | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Claude/Codex models not exercised | Seventeen frozen semantic cases have no run records | NOT RUN | SPEC section 15; PLAN Phase 7 |
| `LCL-GO-001` | Full tested-release identity and all-gate audit belong to Phase 8 | Not run — PLAN Phase 8 | `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | Release surface not exercised | Phase 5 candidate identity is frozen, but HOST INTEGRATION, behavior, RELEASE, and COMPLETE gates remain open | NOT RUN | PLAN Phase 8; Final gates below |

## Deterministic local results

| Check | Observation | Status |
|---|---|---|
| `node --check hooks/leanclarity.cjs` | Exit `0`, no syntax error | PASS |
| `node --test --test-concurrency=1 tests/leanclarity.test.cjs` | `50` tests (45 top-level + 5 subtests), `50` pass, `0` fail/cancel/skip/todo | PASS |
| `claude plugin validate <materialized candidate> --strict` | Claude Code `2.1.250`, isolated config, nonessential traffic disabled; the nine candidate files were materialized into a task-owned temporary directory (aggregate hash equal to the candidate), `Validating plugin manifest` passed; temporary directory removed | PASS |
| `claude plugin validate . --strict` | Same isolation; with `.claude-plugin/marketplace.json` present the validator reports `Validating marketplace manifest` and passed | PASS |
| Candidate byte audit | Exact nine regular files after allowlisting the two marketplace catalogs; aggregate hash `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902` | PASS |
| Candidate JSON parse | `3/3` JSON files parsed | PASS |
| Marketplace catalog content | `2/2` catalogs parse and name only `leanclarity`; the Claude catalog carries the candidate description and no `$schema` (the previously referenced schema URL resolved to HTTP 404); the Codex catalog pins the repository git URL at `main` | PASS |
| Codex legacy catalog compatibility (isolated `CODEX_HOME`) | On a temporary copy of the candidate plus `.claude-plugin/marketplace.json`, `codex plugin marketplace add` registered the marketplace from that Claude-format catalog, `codex plugin list` surfaced the plugin, and `codex plugin add` installed `1.0.0`; temporary home and copy removed | PASS |
| Codex local-path install (workspace `CODEX_HOME`, before the catalogs were renamed) | In `D:\AI_DEV\leanclarity_codex`, `codex plugin marketplace add` registered the workspace catalog and `codex plugin add` installed `1.0.0` into `.codex-home/plugins/cache/` with exactly the nine candidate files (aggregate hash equal); `codex plugin list` reported `installed, enabled`; real `~/.codex` config fingerprint and cache listing unchanged. Superseded by the git-marketplace install path | PASS |
| LeanClarity local Markdown links | `11/11` local targets resolved across the audited Markdown set (now including `INSTALL.md`) | PASS |
| Production static scan | Only three allowed Node imports; prohibited execution, egress, persistence, and fallback patterns absent | PASS |

The host test guard rejected uncapped `node --test tests/leanclarity.test.cjs` before execution because it lacked a concurrency limit. The executed equivalent added `--test-concurrency=1`; no test was omitted.

### Supplemental non-gating tool check

`python C:\Users\js\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py D:\AI_DEV\leancue` could not start because that external helper's `yaml` module is absent. Status: `BLOCKED`. It is not a SPEC/PLAN gate, no project or global dependency was installed, and the current official Claude strict validator plus project packaging checks passed. Its required-field checks (for example `interface.displayName` and `interface.defaultPrompt`) mirror the ChatGPT plugin-ingestion schema; the Codex CLI local install accepted the minimal candidate manifest without them (see Codex host results).

## Claude host results

Preparation only; every Claude matrix row in PLAN Phase 6 remains `NOT RUN`.

- Observed registry state on 2026-08-29: marketplace `leancue` registered from directory `D:\AI_DEV\leancue` (`2026-08-28T15:57:39Z`); plugin `leanclarity@leancue` version `1.0.0` installed at `2026-08-28T15:57:43Z` with scope `local` for project `D:\AI_DEV\leanclarity_claude`, whose `.claude/settings.local.json` enables `leanclarity@leancue`. The install predates this re-verification and was not performed by this record's deterministic runs.
- `claude plugin list` run from `D:\AI_DEV\leanclarity_claude` reports `leanclarity@leancue` `1.0.0`, `Scope: local`, `Status: enabled`; that workspace's `.claude/settings.local.json` enables only `leanclarity@leancue` and sets every other installed plugin to `false`, and the user-level `~/.claude/settings.json` does not enable it. This workspace is Claude-only; it carries no Codex catalog.
- Installed copy `~/.claude/plugins/cache/leancue/leanclarity/1.0.0/`: all nine candidate files are byte-identical to the frozen candidate (`cmp`); the copy also contains the catalog, `docs/`, and `tests/`, which the runtime never reads.
- Plugin data directory `~/.claude/plugins/data/leanclarity-leancue/` exists and is empty: `state.json` is absent, so the Saved setting is the defined default ON and no control prompt has been processed yet.
- As of this record the workspace still runs the directory-marketplace install `leanclarity@leancue`; the git-marketplace reinstall as `leanclarity@leanclarity` at local scope (`INSTALL.md`) has not been observed.
- Not observed: hook invocation, `SessionStart` source emission, control-prompt blocking, `SubagentStart` context, persistence across clean boundaries, and context-limit behavior.

## Codex host results

Preparation only; every Codex matrix row in PLAN Phase 6 remains `NOT RUN`.

- Real profile on 2026-08-29: no `leancue` marketplace and no `leanclarity` plugin entry in `~/.codex/config.toml`; nothing for LeanClarity under `~/.codex/plugins/cache/`. The real profile was not modified by this record.
- Codex CLI `codex-cli 0.150.1` lists only marketplaces registered with `codex plugin marketplace add`; a repository catalog is not discovered implicitly from the working directory, even for a trusted project. Plugin enablement is a user-level `[plugins."<plugin>@<marketplace>"] enabled` entry with no per-project scope, so the operator install path is the user-profile git-marketplace install in `INSTALL.md` (`codex plugin marketplace add wotjr1649/leanclarity`, `codex plugin add leanclarity@leanclarity`), the same path the pinned upstream plugins use on this machine.
- Local-path observation before the catalogs were renamed (workspace `D:\AI_DEV\leanclarity_codex`, workspace-scoped `CODEX_HOME` `.codex-home/` with `[features] hooks = true` and a trusted-project entry): `codex plugin marketplace add` of the workspace catalog and `codex plugin add` installed version `1.0.0` into the workspace cache with exactly the nine candidate files (aggregate hash `F3C0096EADA6575D0E6CB9827BA979249C7D0EC0D84D108A69F31264BF91E902`), accepting the minimal `.codex-plugin/plugin.json` without `interface` fields; `codex plugin list` reported `installed, enabled`; the real `~/.codex/config.toml` fingerprint and cache listing were unchanged. This workspace install is superseded by the git-marketplace path and is not part of the Phase 6 matrix.
- Isolated-home observations (temporary homes, removed): Codex accepts the Claude-format `.claude-plugin/marketplace.json` as a legacy-compatible catalog, and installing from the repository root copies the whole repository including `.git/`, `docs/`, `tests/`, and the catalogs.
- Remaining before matrix runs: the git-marketplace install on the real profile, per-plugin hook trust review via `/hooks`, and the Codex `SessionStart` source set `startup`, `resume`, `clear`, `compact` (matches the runtime allowlist). `[features] hooks = true` is already present in the real profile.
- Not observed: hook trust, hook invocation, control-prompt blocking, `SubagentStart` context, `PLUGIN_ROOT`/`PLUGIN_DATA` ownership, `${CLAUDE_PLUGIN_ROOT}` expansion of the hook command on Windows, and spill behavior.

## Context measurements

| Composition | UTF-8 bytes | Unicode code points | Engineering occurrences | Guidance occurrences | Live host limit observation |
|---|---:|---:|---:|---:|---|
| Engineering canonical trim | 1175 | 1175 | 1 | 0 | NOT RUN |
| Guidance canonical trim | 1308 | 1308 | 0 | 1 | NOT RUN |
| Main | 2486 | 2486 | 1 | 1 | NOT RUN |
| Subagent | 1176 | 1176 | 1 | 0 | NOT RUN |

No runtime truncation, summarization, partial injection, or `additionalContextLimit` override exists.

## Deferred live-host and semantic results

| Phase | Requirements/surface | Status | Reason |
|---|---|---|---|
| Phase 6 Claude host | `LCL-SCOPE-001`, `LCL-CMD-001`, `LCL-LIFE-001`, `LCL-SUB-001`, `LCL-HOOK-001`, `LCL-OUTPUT-001`, `LCL-STATE-001`, `LCL-FAIL-001`, `LCL-MEASURE-001`, `LCL-PKG-001`, host-control portion of `LCL-SEC-001` | NOT RUN | Plugin installed and enabled for Phase 6 (see Claude host results); no live hook invocation has been observed or recorded yet |
| Phase 6 Codex host | Same applicable host surfaces, including native plugin-data ownership and no context spill | NOT RUN | Git-marketplace install on the real profile, hook trust, and live hook invocation were not performed (see Codex host results) |
| Phase 7 behavior smoke | `LCL-ENG-001`, `LCL-GUIDE-001`, `LCL-BEH-001`; 17 cases × 3 runs × 2 hosts | NOT RUN | Requires successful Phase 6 and frozen real host/model settings |
| Phase 8 release audit | `LCL-GO-001`, release artifact identity, final docs/host/behavior consolidation | NOT RUN | HOST INTEGRATION and behavior gates are incomplete |

## Residual uncertainty

- macOS/Linux: portable-by-design, not release-validated.
- Actual Claude/Codex command blocking, lifecycle source emission, SubagentStart context, persistence, and context-limit behavior: not verified.
- Model semantic behavior, causal improvement, statistical reliability, and safety guarantees: not evaluated or claimed.
- Codex provides no required official local validator in the frozen PLAN; actual discovery/trust remains a Phase 6 observation.
- The isolated Claude validator temp directory was removed after validation. It was outside the candidate distribution, and no generated file content was inspected or copied.
- A marketplace install from the repository root copies the whole repository (Claude: the catalogs, `INSTALL.md`, `docs/`, `tests/`; Codex local-path installs additionally `.git/`), so an installed copy is a superset of the nine-file candidate. The release packaging source that ships exactly the candidate byte set is a Phase 8 decision.
- The repository `https://github.com/wotjr1649/leanclarity` is private for Phase 6–7 installs; public visibility, release tags, and any registry listing are Phase 8 release actions. Marketplace installs from it need host git access to the private repository.

## Final gates

- SPEC GO: `GO` (canonical SPEC/PLAN hashes unchanged)
- IMPLEMENTATION GO: `GO` (all 22 applicable Phase 1–5 deterministic requirement slices PASS on the frozen candidate)
- HOST INTEGRATION GO: `NOT VERIFIED`
- RELEASE GO: `NOT VERIFIED`
- COMPLETE GO: `NOT GRANTED`
