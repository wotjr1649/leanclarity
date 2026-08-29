# LeanClarity v1.0 Implementation and Verification Plan

## 0. 문서 상태와 사용법

| 항목 | 값 |
|---|---|
| 문서 종류 | Executable Implementation and Verification Plan |
| Plan 버전 | 1.0 |
| 규범 입력 | [LeanClarity_v1.0_SPEC.md](../specs/LeanClarity_v1.0_SPEC.md) |
| 현재 단계 | Phase 0 documentation discovery 완료, 구현 미착수 |
| Task root | `D:\AI_DEV\leancue` |
| 실행 원칙 | 한 phase를 완료하고 exit evidence를 남긴 뒤 다음 phase로 진행 |

이 PLAN은 새 clean context에서도 각 phase를 독립 실행할 수 있게 작성됐다. 실행자는 해당 phase의 `Entry`, `Sources`, `Work`, `Verification`, `Anti-pattern guards`, `Exit evidence`를 먼저 읽는다.

SPEC은 제품 계약을 소유한다. PLAN은 구현 순서와 evidence 형식만 소유하며 SPEC을 완화하거나 재해석하지 않는다. 구현 중 제품 결정이 다시 열리면 해당 phase를 중단하고 새 SPEC revision을 먼저 만든다.

## 1. 공통 실행 규칙

### 1.1 변경 범위

- `D:\AI_DEV\leancue` 안의 LeanClarity task files만 수정한다.
- `D:\AI_DEV\_refs\ponytail`과 `D:\AI_DEV\_refs\i-have-adhd`는 pinned read-only source다.
- 기존 LeanCue SPEC/PLAN은 superseded history로 보존한다.
- phase 시작 전 applicable guidance, file status와 기존 diff를 확인한다.
- unrelated existing file이나 user change를 흡수, 삭제, format하지 않는다.
- 파일 수정은 patch 단위로 수행하고 final artifact를 다시 읽는다.

현재 task root는 git repository가 아니다. Phase 실행 시 git이 생겼다면 normal status/diff를 사용하고, 여전히 없다면 시작 전 relevant file hash와 file list를 기록해 intended-only change를 검증한다. Plan 실행을 위해 git repository를 새로 만들지 않는다.

### 1.2 최소 구현 원칙

- one CommonJS production runtime: `hooks/leanclarity.cjs`
- one host-shared hook map: `hooks/hooks.json`
- one host-local state file: `state.json`
- two canonical policies
- one native Node test file를 우선하고 실제 분리 필요가 증명될 때만 split
- standard library와 host-native plugin capability 우선
- 새 dependency, package manager, framework, installer, adapter, service 또는 database 없음

### 1.3 안전과 authority

다음은 이 PLAN 작성이나 local implementation 요청만으로 허가되지 않는다.

- Claude/Codex user/global config 수정
- plugin 설치, enable, trust 또는 제거
- marketplace 등록
- public publish, registry upload, push 또는 release 생성
- 기존 Ponytail/i-have-adhd/LeanCue plugin disable/delete

Phase 6에서 실제 host state 변경이 필요하면 그 exact host, profile과 effect에 대한 current user authority를 확인한다. 가능한 경우 task-owned isolated profile이나 non-persistent local-load path를 사용한다. Host guard, trust prompt, managed policy와 hook denial을 우회하지 않는다.

### 1.4 evidence 상태

모든 check는 다음 중 하나로 기록한다.

| 상태 | 의미 |
|---|---|
| `PASS` | 실행했고 기대 observation을 직접 확인함 |
| `FAIL` | 실행했고 contract 위반을 확인함 |
| `BLOCKED` | 필요한 authority/environment/host capability가 없어 실행하지 못함 |
| `NOT RUN` | 아직 실행하지 않음 |
| `HOLD` | review/adjudication 또는 candidate rework가 끝나지 않아 PASS/FAIL을 닫지 못함 |
| `N/A` | SPEC상 해당 artifact/configuration에 적용되지 않음 |

`HOLD`는 `RELEASE GO`와 `COMPLETE GO`를 막으며 required review/adjudication 전에는 `PASS`나 `N/A`로 바꾸지 않는다. `should work`, source review 또는 synthetic test를 real host `PASS`로 기록하지 않는다.

### 1.5 rollback

각 phase는 그 phase에서 만든 파일과 변경 line만 되돌릴 수 있어야 한다. unrelated file을 reset/restore/stash하지 않는다. State-write test는 task-owned temp directory만 사용한다. 실제 host test cleanup은 그 test가 만든 plugin/profile state만 제거한다.

## Phase 0 — Documentation Discovery and Contract Freeze

### Entry

- SPEC sections 1–17이 확정 제품 결정을 규범화했다.
- [LeanClarity v1.0 SPEC](../specs/LeanClarity_v1.0_SPEC.md)이 존재한다.
- implementation artifact는 아직 없다.

### Sources

#### Official host sources

- [OpenAI — Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI — Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [OpenAI — Slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Anthropic — Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Anthropic — Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Anthropic — Create plugins](https://code.claude.com/docs/en/plugins)
- [Node.js — File system API](https://nodejs.org/api/fs.html)
- [Node.js — `TextDecoder`](https://nodejs.org/api/util.html#class-utiltextdecoder)

#### Pinned local upstream

- [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), local `D:\AI_DEV\_refs\ponytail` at `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd), local `D:\AI_DEV\_refs\i-have-adhd` at `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c`

Read-only policy and attribution inputs:

- `D:\AI_DEV\_refs\ponytail\skills\ponytail\SKILL.md`
- `D:\AI_DEV\_refs\ponytail\LICENSE`
- `D:\AI_DEV\_refs\i-have-adhd\skills\i-have-adhd\SKILL.md`
- `D:\AI_DEV\_refs\i-have-adhd\evals\cases.jsonl`
- `D:\AI_DEV\_refs\i-have-adhd\evals\rubric.md`
- `D:\AI_DEV\_refs\i-have-adhd\LICENSE`

### Allowed host/API baseline

| Surface | Allowed baseline |
|---|---|
| Claude manifest | `.claude-plugin/plugin.json`; default `hooks/hooks.json` discovery |
| Codex manifest | required `.codex-plugin/plugin.json`; default `hooks/hooks.json` discovery |
| Events | `SessionStart`, `UserPromptSubmit`, `SubagentStart` |
| Claude sources | `startup`, `resume`, `clear`, `compact`, `fork` |
| Codex sources | `startup`, `resume`, `clear`, `compact` |
| Context output | `hookSpecificOutput.hookEventName` + `additionalContext` |
| Command block | top-level `decision: "block"` + `reason` |
| Claude paths | `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` |
| Codex paths | `PLUGIN_ROOT`, `PLUGIN_DATA`; Claude compatibility variables also provided |
| Production Node APIs | CommonJS, `node:fs`, `node:path`, process/stdin/stdout, UTF-8 decode |
| Test-only Node APIs | `node:test`, `node:assert/strict`, `node:child_process`, task-owned temp directories |

이 baseline은 2026-08-28 official pages에서 확인했다. Implementation은 unfamiliar/changed field에 의존하기 전에 관련 page를 다시 열어야 한다. Linked schema `main` branch가 installed release보다 새로울 수 있으므로 actual release-host observation이 support를 결정한다.

### Confirmed technical constraints

- Claude `UserPromptSubmit decision:block` prevents processing and erases the prompt from context; `reason` is user-visible.
- Codex documents the same block shape for `UserPromptSubmit`.
- `UserPromptSubmit` matcher is not used; omit it.
- Claude/Codex `SubagentStart` adds context but cannot stop subagent creation.
- 2026-08-28 docs에서 Claude hook output string은 10,000 characters 이후 file-preview replacement를 사용한다.
- 2026-08-28 docs에서 Codex는 `additionalContext` handler당 default 약 2,500 tokens 이후 spill한다.
- 위 두 수치는 runtime constant나 universal limit이 아니라 Phase 6에서 exact host/version에 대해 다시 확인할 release baseline이다.
- Codex hook handler docs expose command strings, not Claude's newer exec-form `args`; the shared map therefore uses one quoted command string and validates it on Windows.
- Node `fs.rename` documents overwrite of an existing target; Windows behavior must still be observed in Phase 3.

### Work

1. Compare official pages against the SPEC event, output, variable and limit claims.
2. Confirm both upstream HEADs and LICENSE notices.
3. Confirm SPEC sections 1–17이 확정 제품 결정을 직접 규범화하고 외부 Q-number contract에 의존하지 않는지 확인한다.
4. Confirm no unresolved product choice is disguised as an implementation TODO.
5. Freeze the requirement ID list and phase traceability table.

### Verification

- Parse every local Markdown link in SPEC/PLAN and confirm the target exists or is explicitly future-created.
- Search new normative docs for stale command/mode vocabulary.
- Confirm all requirement IDs match `LCL-[A-Z]+-[0-9]{3}` and are unique.
- Confirm official links resolve to the named official domain.
- Confirm upstream working trees are clean and HEADs match the pinned revisions.

### Anti-pattern guards

- Do not copy an old LeanCue requirement and merely rename `LC` to `LCL`.
- Do not infer exact `Current` state from a session ID or transcript.
- Do not convert the plain prompt command into a skill or slash command.
- Do not add session state, history, telemetry or migration for possible future use.
- Do not treat name-search results as trademark clearance.

### Exit evidence

- `LCL-PROD-001`, `LCL-SCOPE-001` and the complete normative ID list frozen.
- Source URL/revision table recorded.
- SPEC GO remains evidence-backed; other gates remain NOT VERIFIED.

### Current phase result

`PASS` for documentation discovery performed during SPEC/PLAN authoring. Re-run if official docs or installed host versions changed before implementation.

## Phase 1 — Canonical Policies

### Entry

- Phase 0 is `PASS`.
- SPEC sections 5–6 and 14–15 are frozen.
- No implementation policy file exists, or existing task-owned files have been inspected.

### Files

- `policies/engineering.md`
- `policies/guidance.md`
- `tests/leanclarity.test.cjs`

### Sources

- SPEC sections 5.3 and 6
- `D:\AI_DEV\_refs\ponytail\skills\ponytail\SKILL.md`
- `D:\AI_DEV\_refs\i-have-adhd\skills\i-have-adhd\SKILL.md`
- `D:\AI_DEV\_refs\i-have-adhd\evals\cases.jsonl`
- `D:\AI_DEV\_refs\i-have-adhd\evals\rubric.md`

### Work

1. Write `engineering.md` as LeanClarity's compact first-party Engineering contract.
2. Preserve understand-before-minimize, reuse ladder, smallest-correct/root-cause, safety and one-runnable-check behavior.
3. State that report/explanation-only tasks do not force implementation.
4. Write `guidance.md` with action-first, bounded steps, tangent suppression, visible progress and conditional next action.
5. Preserve detail/exhaustive/output-format/destructive/ambiguity/repeated-failure exceptions.
6. Remove medical framing, rigid list/time/length templates and Ponytail output formatting.
7. Keep each concept's rule and exception together; do not restate environment facts or runtime behavior inside policies.
8. Add policy tests before runtime code.

Canonical files should read as stable model guidance, not as a history of upstream decisions. Attribution belongs in notices, not in every model-visible turn.

### Verification

Run:

```powershell
node --test tests/leanclarity.test.cjs
```

Policy checks must prove:

- two files exist as non-symlink/non-reparse regular files, are each at most 1 MiB raw bytes, valid UTF-8 and non-empty after trim;
- each has one clear product/policy heading;
- no Lite/Full/Ultra sentinel or independent switch exists;
- no ADHD/diagnosis/treatment/dopamine/efficacy framing exists;
- no fixed list cap, mandatory estimate or three-line output template exists;
- Engineering owns decisions, Guidance owns communication;
- safety, detail, exhaustive findings and evidence truthfulness exceptions remain;
- full policy text is not copied into tests or another source.

Record each file and composed Main/Subagent UTF-8 byte/code-point measurement. These are observations, not authoring caps.

### Anti-pattern guards

- Do not concatenate the two upstream SKILL files.
- Do not preserve intensity labels as hidden internal tiers.
- Do not add frontmatter, sentinels or a policy parser.
- Do not optimize wording by deleting a safety/detail exception.
- Do not put runtime/state/command instructions in model-visible policy.

### Exit evidence

- `LCL-ENG-001`, `LCL-GUIDE-001`, policy-source portion of `LCL-POL-001`: `PASS`.
- Policy hashes and measurements recorded.
- No runtime or host claim is marked `PASS`.

### Rollback

Remove only Phase 1-created policy/test hunks. Upstream sources and historical LeanCue docs remain untouched.

## Phase 2 — Pure Hook Runtime and Composition

### Entry

- Phase 1 is `PASS`.
- Actual Node version is recorded.
- Official hook input/output pages have been re-opened for the installed development baseline.

### Files

- `hooks/leanclarity.cjs`
- `tests/leanclarity.test.cjs`

### Sources

- SPEC sections 6, 8 and 9
- [Claude hooks: input/output and events](https://code.claude.com/docs/en/hooks)
- [Codex hooks: inputs, outputs and limitations](https://learn.chatgpt.com/docs/hooks)
- [Node file-system API](https://nodejs.org/api/fs.html)

### Work

Implement one CommonJS file with pure seams plus a thin process runner.

Minimum seams:

```text
decodeInput(rawBytes)
parseEvent(value)
parseCommand(prompt)
resolvePluginRoot(env)
resolveDataRoot(env)
loadPolicies(pluginRoot)
composeMain(engineering, guidance)
composeSubagent(engineering)
dispatch(event, dependencies)
emit(result)
```

Functions may use different names if fewer functions remain clearer. Do not create a class, provider, registry, factory or file per event.

Runtime behavior:

1. Bound stdin to 1 MiB raw bytes including BOM and 1,000 ms from process start.
2. Decode with `TextDecoder` fatal mode, tolerate one BOM and parse one top-level object.
3. Validate only event-specific fields the runtime uses. For `SessionStart`, require Claude `startup/clear/resume/compact/fork` or Codex `startup/clear/resume/compact` according to the native host environment.
4. `PLUGIN_ROOT`/`PLUGIN_DATA` 중 하나라도 present이면 Codex pair로 식별하고 둘 다 non-empty absolute path인지 요구한다. Present-but-invalid native pair는 Claude pair로 fallback하지 않는다. 둘 다 absent일 때만 valid Claude root/data pair를 사용하며 inconsistent/missing pair에는 cwd/home fallback을 사용하지 않는다.
5. Read fixed policy paths only.
6. Main policy loading is all-or-nothing; Subagent requires Engineering only.
7. Compose canonical text exactly as SPEC section 6.3.
8. Emit empty stdout or one JSON object with actual event name.
9. Top-level unexpected failures emit no policy and exit without blocking ordinary host work.
10. Export test seams only; run process I/O only when `require.main === module`.
11. Select status/error/diagnostic text from a fixed catalog and cap every user-visible string at 512 UTF-8 bytes.

### Verification

Run:

```powershell
node --check hooks/leanclarity.cjs
node --test tests/leanclarity.test.cjs
```

Required cases:

- empty, malformed, BOM, null, array and scalar input;
- invalid UTF-8;
- exactly 1 MiB and 1 MiB + 1 byte;
- complete and partial input without EOF, with bounded termination around the 1,000 ms process-start deadline;
- unsupported/missing event;
- Claude/Codex valid, missing, unknown and cross-host `SessionStart source`;
- event-specific wrong/missing field;
- path with spaces and Windows separators;
- primary/fallback environment-variable precedence;
- no data-root fallback to cwd/home/global config;
- valid Main contains both canonical texts once and in order;
- valid Subagent contains Engineering once and zero Guidance;
- one invalid Main policy emits neither;
- invalid Engineering emits no Subagent policy;
- oversized, symlink/reparse or non-regular policy emits no policy;
- output is empty or one parseable JSON object;
- `hookEventName` matches actual event;
- stdout contains no log/banner/stack;
- fixed status/error/diagnostic strings are at most 512 UTF-8 bytes;
- importing the module starts no stdin read, timer, stdout write or state mutation.

Tests may use `node:child_process` to exercise the production entrypoint. Production code may not import it.

### Anti-pattern guards

- Do not implement persistence, locks or session identity in this phase.
- Do not repeat policies on `UserPromptSubmit`.
- Do not inspect transcript or prompt content beyond exact command parsing seam.
- Do not add host-specific runtime files.
- Do not return a fixed `SessionStart` event name for `SubagentStart`.
- Do not rely on `suppressOutput` or unsupported output fields.

### Exit evidence

- `LCL-ARCH-001`, `LCL-POL-001`, `LCL-RUN-001`, `LCL-INPUT-001`, composition part of `LCL-OUTPUT-001`: deterministic `PASS`.
- Runtime line count and imports recorded for later minimality review.

### Rollback

Remove only Phase 2 runtime/test hunks. Keep the canonical policy files from Phase 1.

## Phase 3 — Saved State and Control Commands

### Entry

- Phase 2 is `PASS`.
- SPEC sections 7 and 10 are frozen.
- Windows task-owned temp directories are available for state tests.

### Files

- `hooks/leanclarity.cjs`
- `tests/leanclarity.test.cjs`

### Sources

- SPEC sections 7 and 10
- [Node `fs.rename`](https://nodejs.org/api/fs.html#fsrenameoldpath-newpath-callback)
- [Claude `UserPromptSubmit`](https://code.claude.com/docs/en/hooks#userpromptsubmit)
- [Codex `UserPromptSubmit`](https://learn.chatgpt.com/docs/hooks#userpromptsubmit)
- Claude/Codex plugin-data documentation from Phase 0

### Work

1. Resolve `PLUGIN_DATA` before `CLAUDE_PLUGIN_DATA`; reject missing/empty/non-absolute root without fallback.
2. Use exactly `<data-root>/state.json`.
3. Implement absent state as defined default ON.
4. Use `lstat`; accept only a non-symlink/non-reparse regular file containing an object with only boolean `enabled`.
5. Treat existing malformed/unreadable/invalid/non-regular state as unavailable; do not guess.
6. Implement same-directory exclusive temp write, file sync/close, native replace, target reread and exact value verification.
7. Never delete the target before replacement.
8. Allow exact `on/off` to repair only absent state or a byte-readable regular file with invalid UTF-8/JSON/schema. Unreadable, directory, symlink/reparse and other non-regular targets fail without deletion.
9. Implement the three normalized exact commands and no aliases.
10. Return `decision: "block"` and fixed bounded status/error reason for recognized commands.
11. Keep ordinary prompt as a zero-output, zero-mutation no-op.
12. Read Saved setting independently on every `SessionStart` and `SubagentStart` invocation.

### Deterministic transition matrix

| Initial storage | Input | Required storage/result |
|---|---|---|
| absent | `SessionStart` | default ON composition; file creation not required |
| absent | `leanclarity` | reports ON; no write |
| absent | `leanclarity on` | valid explicit `true` state after verified write |
| absent | `leanclarity off` | valid explicit `false` state after verified write |
| ON | `leanclarity off` | verified OFF state; current context not rewritten |
| OFF | `leanclarity on` | verified ON state; current context not rewritten |
| ON/OFF | same-value command | verified canonical requested state; success allowed |
| readable regular but invalid | `leanclarity` | error + command block; no guessed status |
| readable regular but invalid | exact on/off | repair succeeds only after replace/readback |
| unreadable/non-regular | exact command | error + command block; no automatic repair |
| corrupt/unavailable | lifecycle | no injection + bounded diagnostic |
| OFF | lifecycle | no policy and no policy-read requirement |

### Command parser cases

Accepted after `trim()` + `toLowerCase()`:

```text
leanclarity
leanclarity on
leanclarity off
```

Test accepted surrounding whitespace and case variants. Test these as ordinary prompts:

- `/leanclarity`
- `leanclarity status`
- `leanclarity on.`
- `leanclarity off now`
- prompt with internal newline
- sentence containing the command text
- homoglyph or zero-width modification
- empty/whitespace-only prompt

### State and failure cases

- missing data-root variables;
- invalid/non-absolute data root;
- existing state directory, symlink/reparse point or other non-regular target;
- malformed JSON, null/array/scalar;
- missing/unknown keys and non-boolean value;
- invalid UTF-8;
- read-only/unwritable task-owned test path;
- temp create/write/sync/close/rename/readback failure injected through test seam;
- old valid target preserved on pre-replace failure;
- replace/readback failure reports error without claiming rollback or target value;
- no success reason on any failed step;
- concurrent opposing writes leave one complete valid state;
- each command claims success only when its readback matches;
- state deletion after OFF restores defined default ON;
- no state file contains prompt/session/path/history.

### Windows atomic-replace observation

Run a direct task-owned integration test on the actual release Node version:

1. Write valid target OFF.
2. Write same-directory temp ON.
3. Rename temp over existing target without pre-delete.
4. Reread and verify ON.
5. Repeat ON → OFF.
6. Confirm no partial JSON and no orphan temp remains after success.

This observation is required for `LCL-STATE-001`; Node documentation alone is insufficient.

### Verification

```powershell
node --check hooks/leanclarity.cjs
node --test tests/leanclarity.test.cjs
```

### Anti-pattern guards

- No schema version, migration table, session file, history, backup or journal.
- No lock unless an observed race makes the one-file contract incorrect.
- No state write under plugin root.
- No fallback to `.claude`, `.codex`, home, repo or upstream config.
- No `Current`, `Desired`, parent-state or inherited-state field.
- No command output containing raw exception/path/state content.

### Exit evidence

- `LCL-SWITCH-001`, `LCL-CMD-001`, `LCL-STATUS-001`, `LCL-STATE-001`, deterministic portion of `LCL-LIFE-001` and `LCL-FAIL-001`: `PASS`.
- Windows Node version and replace observation recorded.

### Rollback

Remove Phase 3 code/test hunks and all task-temp state. Never remove real host plugin-data in this phase.

## Phase 4 — Packaging, License and Operator Documentation

### Entry

- Phases 1–3 are `PASS`.
- Actual runtime paths and outputs are stable.
- No host installation is required to create package files.

### Files

- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `hooks/hooks.json`
- `README.md`
- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `tests/leanclarity.test.cjs`

### Sources

- SPEC sections 5, 9 and 13–14
- [Claude plugin manifest and default locations](https://code.claude.com/docs/en/plugins-reference)
- [Codex plugin structure and manifest](https://developers.openai.com/plugins/build/plugins)
- [Claude hook configuration](https://code.claude.com/docs/en/hooks)
- [Codex hook configuration](https://learn.chatgpt.com/docs/hooks)
- both pinned upstream LICENSE files

### Work

1. Create minimal Claude and Codex manifests with matching `leanclarity`, `1.0.0`, description and MIT metadata.
2. Use default `hooks/hooks.json`; omit duplicate manifest `hooks` fields.
3. Register exactly `SessionStart`, `UserPromptSubmit`, `SubagentStart` as synchronous command hooks.
4. Use one quoted compatibility command: `node "${CLAUDE_PLUGIN_ROOT}/hooks/leanclarity.cjs"`.
5. Set a small explicit timeout validated on Windows; do not use `async`.
6. Omit `UserPromptSubmit` matcher and unsupported/custom fields.
7. Write README from observed runtime behavior, including plain prompts and clean/inherited boundary.
8. Explain that deleting plugin-data resets Saved setting to default ON.
9. Explain manual coexistence cleanup without detecting or mutating other plugins.
10. Add LeanClarity MIT license and full notices for both pinned upstreams.
11. In each notice record source name/URL/revision, full MIT text/copyright and the derived LeanClarity policy location.
12. Define the candidate distribution as only the two manifests, `hooks/`, `policies/`, `README.md`, `LICENSE` and `THIRD_PARTY_NOTICES.md`; exclude `tests/` and `docs/evidence/`.

### Verification

Local deterministic checks:

- both manifests parse as JSON;
- names/version/description/license agree;
- `.codex-plugin/plugin.json` exists;
- hook map parses and has exactly three event keys;
- every handler invokes the same CJS path;
- every referenced file exists;
- no `skills`, `mcpServers`, `apps`, `commandWindows` or `async` field;
- no `package.json`, `node_modules`, installer, statusline or adapter;
- README command strings and state/failure semantics match tests;
- full two upstream MIT notices, source URLs, revisions, copyrights and derived-policy locations exist;
- candidate distribution file list contains no tests or evidence and every included byte is hashable;
- no runtime source is copied into README/notices.

If Claude CLI is locally available without permanent install:

```powershell
claude plugin validate . --strict
```

Supported Codex version이 official validator command를 제공하지 않고 SPEC도 이를 요구하지 않으면 validator row는 근거를 적어 `N/A`로 둔다. Codex discovery/trust는 documented host workflow로 증명한다. Required supported-host evidence 자체를 실행할 수 없을 때만 `BLOCKED`를 사용한다.

### Anti-pattern guards

- Do not add placeholder homepage/repository/privacy URLs.
- Do not create a marketplace entry merely to complete packaging.
- Do not claim public availability or install the plugin globally.
- Do not add a discoverable skill for status commands.
- Do not state that “private policy” is confidential.
- Do not describe preliminary name search as legal clearance.

### Exit evidence

- `LCL-PKG-001`, `LCL-MIG-001`, `LCL-LIC-001`: local `PASS`.
- Host validation rows remain `NOT RUN` or `BLOCKED` until Phase 6.

### Rollback

Remove only Phase 4-created package/document files or hunks. Do not touch host config or upstream files.

## Phase 5 — Deterministic Local Verification and Context Measurement

### Entry

- Phases 1–4 are locally complete.
- Phase 1–4 source tree exists and the exact candidate distribution file set is identifiable.
- No known deterministic test is failing.

### Files

- `tests/leanclarity.test.cjs`
- `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md` (initial deterministic sections)

### Work

Consolidate the smallest complete regression suite. Do not create a test framework.

Required groups:

1. Policy source and composition
2. Command parser and status text
3. State validity and atomic replacement
4. Lifecycle dispatch and Main/Subagent scope
5. Input/output process behavior
6. Failure and non-disclosure matrix
7. Packaging/static invariants
8. Context measurement

### Full deterministic matrix

Every applicable row must pass.

| Saved setting | Event/target | Expected |
|---|---|---|
| absent/default ON | Main SessionStart | Engineering + Guidance once |
| explicit ON | Main SessionStart | Engineering + Guidance once |
| explicit ON | SubagentStart | Engineering once; Guidance zero |
| explicit OFF | Main SessionStart | zero LeanClarity policy |
| explicit OFF | SubagentStart | zero LeanClarity policy |
| corrupt | Main/Subagent | zero policy + bounded diagnostic |
| any | ordinary UserPromptSubmit | zero policy, zero mutation, no block |
| valid/corrupt | exact command | block original prompt; truthful status/error |

### Static security checks

Search production files for:

- `child_process`, `eval`, `Function`, dynamic import;
- `http`, `https`, `net`, `tls`, `fetch`, WebSocket;
- SQLite/database/telemetry/analytics/registry;
- global config/home/repository fallback;
- prompt/session/transcript persistence;
- plugin-root writes;
- `skills/`, `package.json`, dependency imports;
- old mode/sentinel/command aliases;
- duplicated full policy text.

Static search is supporting evidence. Runnable behavior tests remain required.

### Context measurement

Record for Engineering, Guidance, Main and Subagent:

- UTF-8 bytes;
- Unicode code points;
- occurrence count in composition;
- Codex observed spill result in Phase 6;
- Claude observed file-preview replacement result in Phase 6.

The 2026-08-28 documented Claude/Codex values are comparison baselines only. Record the exact release-host contract and observation; do not encode those values as runtime constants. Do not add a runtime truncator or raise `additionalContextLimit` to make the test green. If local composition is already implausibly near a host ceiling, edit canonical policies and rerun Phase 1 behavior/static checks.

### Verification commands

```powershell
node --check hooks/leanclarity.cjs
node --test tests/leanclarity.test.cjs
```

Also parse every JSON and verify Markdown links/files with task-local read-only commands. Record the exact command, exit code and observed count in evidence.

### Anti-pattern guards

- No skipped test converted to PASS.
- No flaky test retried until it happens to pass.
- No production behavior mocked as the only evidence.
- No test-only policy fallback.
- No arbitrary aggregate score hiding an individual deterministic failure.

### Exit evidence

- All deterministic requirements through `LCL-SEC-001`: `PASS` locally.
- `IMPLEMENTATION GO` becomes `GO` only after final tree/static/package audit passes.
- `HOST INTEGRATION GO` and `RELEASE GO` remain `NOT VERIFIED`.

### Rollback

Fix the root cause in the owning phase. Do not weaken the failing oracle in Phase 5.

## Phase 6 — Real Windows Host Integration

### Entry

- `IMPLEMENTATION GO` is `GO`.
- Exact Windows 11 x64, Node, Claude Code and Codex versions are recorded.
- The release candidate artifact/hash is frozen for this phase.
- Required host-state effects have explicit user authority.
- Test prompts and evidence are synthetic and secret-free.
- If the candidate is a policy-only revision under SPEC 17.1, the inherited rows enter this
  phase already `PASS` and only the context measurement and the host context-limit proof are
  open. Record the predecessor aggregate hash, both byte sets, and the proof that the diff is
  confined to the two policy files before claiming any inherited row.

### Authority checkpoint

Before any persistent host mutation, record:

```text
Host and exact profile
Install/load method
Files/settings the host will change
How test-created state will be removed
Whether the action is temporary or persistent
User authority covering that exact effect
```

Prefer Claude `--plugin-dir` or an equivalent official non-persistent path when it proves the row. For Codex, use the current official local-plugin workflow; do not hand-edit global config if a native command/UI owns it. If authority or capability is absent, mark affected rows `BLOCKED` and continue independent read-only checks.

### Sources

Re-open the current official pages from Phase 0 and record retrieval date/version assumptions. Use installed host help/validation output only after reviewing its effect.

For every lifecycle row, record `documented`, `observed` or `unsupported` for the exact host/version/surface. Separately distinguish: host did not invoke the hook, host invoked it and runtime returned output, and runtime failed after invocation. Synthetic dispatch proves runtime handling only.

### Claude Code matrix

Observe with the actual candidate:

| Scenario | Required observation |
|---|---|
| plugin discovery | manifest and three hooks load without warning/error |
| `startup`, absent state | Main receives both policies; default ON |
| exact status command | reason shown; original command absent from model conversation |
| `off`, then ordinary prompt | Saved OFF shown; existing context disclaimer; ordinary prompt proceeds |
| new chat after OFF | no LeanClarity policy |
| `/clear` after OFF | no LeanClarity policy |
| `on`, then new chat/clear | both policies return |
| new Subagent after ON | Engineering only |
| new Subagent after OFF | no LeanClarity policy |
| `resume` | new event uses Saved setting; no exact prior-context claim |
| `compact` | new event uses Saved setting; inherited-context disclaimer remains true |
| `fork` | if current host emits it, same inherited-boundary rule |
| invalid policy/state in isolated data | all-or-nothing/no-guess diagnostics; host remains usable |
| hook/plugin disabled | LeanClarity does not self-enable or bypass host control |

Use `/hooks`, `/plugin`, `/reload-plugins`, debug output or current official equivalents only as read/validation tools. Record commands and observations without copying private transcript data.

### Codex matrix

Observe the same product semantics for:

- plugin discovery/trust;
- `startup`, `clear`, `resume`, `compact`;
- exact three commands and prompt blocking;
- ordinary prompt no-op;
- Main/Subagent scope;
- ON/OFF persistence across clean context;
- invalid policy/state fail-open behavior;
- plugin disabled, untrusted or hooks disabled;
- actual `PLUGIN_ROOT`/`PLUGIN_DATA` ownership;
- no spill at the default `additionalContext` threshold.

Do not claim Codex `fork` unless the installed official host documents and emits it. Record each Codex surface separately if both desktop and CLI are included in release copy.

### Cross-host state isolation

With both hosts available:

1. Save Claude OFF and Codex ON.
2. Open clean contexts in both.
3. Confirm Claude injects nothing and Codex injects per ON.
4. Reverse the settings and repeat.
5. Confirm neither host reads or writes the other's plugin-data.

### Command-context proof

For each host and each exact command, collect evidence that:

- user-visible status/error appeared;
- host reported the prompt blocked/ended;
- model did not answer the command as a task;
- command text/status was not added as model-visible additional context;
- state changed only after verified write for on/off.

### Host context-limit proof

- Claude: under the exact release-host contract, no file-preview replacement for Main/Subagent output.
- Codex: under the exact release-host contract, no spill file/preview for Main/Subagent output.
- Record actual composed size and host observation.
- If either spills, return to Phase 1; do not truncate at runtime.

### Anti-pattern guards

- No synthetic payload substitutes for a claimed live source.
- No host config edit to bypass a failed plugin/trust path.
- No real user prompt/transcript in evidence.
- No unsupported platform/surface marked GO.
- No automatic cleanup of pre-existing plugin data or other plugins.

### Exit evidence

- Every claimed Windows Claude/Codex row is `PASS` on the frozen artifact.
- `LCL-SCOPE-001`, host portions of `LCL-CMD-001`, `LCL-LIFE-001`, `LCL-SUB-001`, `LCL-HOOK-001`, `LCL-OUTPUT-001`, `LCL-STATE-001`, `LCL-FAIL-001`, `LCL-MEASURE-001` and `LCL-PKG-001`: `PASS`.
- Only then set `HOST INTEGRATION GO = GO`.

### Rollback

Remove only test-created installation/profile/state through the same official host mechanism. Preserve pre-existing plugins and host settings.

## Phase 7 — Semantic Behavior Smoke Gate

### Entry

- `HOST INTEGRATION GO` is `GO` for both hosts.
- Candidate artifact, host/model versions and settings are frozen.
- SPEC section 15 case/oracle table is unchanged.
- Reviewers and evidence location are known.

### Files

- `tests/behavior-cases.jsonl` (exact prompt/fixture and oracle records)
- `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`

`behavior-cases.jsonl` is data, not a shipped eval framework. Keep only fields needed to reproduce section 15.

### Work

1. Materialize every `BEH-*` case from SPEC section 15.2 with one focused, test-owned, synthetic, secret-free fixture.
2. Freeze positive/forbidden predicates and any multi-turn or repeated-failure turn sequence before running the model.
3. Run each case three times per host with the same model/settings/prompt.
4. Freeze and record exposed sampling/seed controls; if the host exposes none, record that fact.
5. Preserve raw response references only for these reviewed synthetic fixtures within task evidence; do not copy arbitrary user prompts, workspace content, transcripts, paths, environment dumps or secrets.
6. Review every positive predicate and forbidden outcome per run and record rationale.
7. General cases require at least 2/3 per host.
8. Critical cases require zero observed unsafe simplification in all three runs per host.
9. One critical unsafe observation returns the candidate to policy review; do not average it away.

### Required evidence fields

```text
LeanClarity version and artifact hash
OS
host, host version and surface
model and relevant settings, including exposed sampling/seed controls
case ID
synthetic fixture path/hash and exact prompt/turn sequence stored there
positive oracle
forbidden outcomes
run 1/2/3 result
review rationale and reviewer
case PASS/FAIL/HOLD
```

### Review rules

- Exact wording equality is not an oracle.
- A judge that merely repeats the LeanClarity policy is not independent evidence.
- A primary reviewer marks ambiguity as HOLD. Reviewer disagreement requires an independent second review and recorded adjudication before PASS.
- Material findings may not be capped to make Guidance appear concise.
- Critical failure cannot be hidden in an aggregate pass rate.
- `2/3` is reported only as a smoke threshold, never a confidence/reliability statistic.
- `0/3 unsafe` is reported as observed evidence, never a safety guarantee.
- No ON/OFF causal superiority claim is made without a separate paired study.

### Anti-pattern guards

- Do not change prompts/oracles after seeing a bad response without invalidating and rerunning the entire affected case.
- Do not silently change model/settings between runs.
- Do not replace failed runs with extra runs.
- Do not describe base-host behavior as caused by LeanClarity.
- Do not use medical/ADHD efficacy criteria.

### Exit evidence

- Every general case passes 2/3 per host.
- Every critical case has zero observed unsafe outcome per host.
- `LCL-BEH-001 = PASS` with the explicit non-statistical caveat.
- Any failed case keeps `RELEASE GO` and `COMPLETE GO` on HOLD.

### Rollback

Behavior failure returns to the owning canonical policy and invalidates affected Phase 5–7 evidence. Do not weaken the oracle.

## Phase 8 — Release Audit and COMPLETE GO

### Entry

- Phases 0–7 applicable rows are `PASS`.
- Candidate artifact is frozen and identifiable.
- No product or host contract changed after its evidence was collected.

### Files

- `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`
- release candidate tree only

### Work

1. Materialize and hash the candidate distribution: two manifests, `hooks/`, `policies/`, `README.md`, `LICENSE` and `THIRD_PARTY_NOTICES.md`; exclude tests and evidence.
2. Re-run deterministic tests and package/static scans on that artifact.
3. Validate Claude manifest/hook map with the actual supported Claude version.
4. Reconfirm Codex plugin discovery on the actual supported Codex version.
5. Recheck README against observed command, state, lifecycle, failure and support behavior.
6. Recheck MIT license and both full pinned notices.
7. Search for stale LeanCue mode architecture and prohibited artifacts.
8. Confirm macOS/Linux remain portable-by-design, not verified.
9. Confirm no public/base-host improvement or security guarantee appears.
10. Complete the traceability matrix with evidence links.

### Stale/prohibited search

Review every occurrence, rather than requiring blind zero counts, for:

```text
LeanCue
leancue
Build
Focus
Lite
Full
Ultra
defaults
/leanclarity
skills/
package.json
node_modules
telemetry
analytics
MCP
```

Allowed occurrences are limited to explicit history/migration/attribution/testing statements. Active runtime/output/manifests may not contain old product/mode vocabulary or slash aliases.

### Final gate rules

```text
SPEC GO           = all normative decisions closed
IMPLEMENTATION GO = all deterministic local requirements PASS
HOST INTEGRATION GO = all claimed Windows host rows PASS
RELEASE GO        = behavior, package, docs, license and artifact audit PASS
COMPLETE GO       = all four gates GO
```

Any applicable `FAIL`, `BLOCKED`, `NOT RUN` or `HOLD` prevents COMPLETE GO. `N/A` is permitted only for a surface the SPEC support matrix excluded before testing; it cannot hide a required supported surface.

### Anti-pattern guards

- Do not publish, push, tag or install merely because the audit passes.
- Do not edit evidence to match a different artifact.
- Do not reuse evidence after policy/runtime/package changes.
- Do not grant GO from source review alone.
- Do not claim trademark clearance from preliminary name search.

### Exit evidence

- Final requirement table contains status, exact check, observation, artifact hash and evidence location.
- All four gates are either honestly GO or the remaining HOLD/BLOCKED reason is explicit.
- Public release remains a separate authorized action.

### Rollback

Return to the earliest owning phase for any failure. Rebuild the candidate identity and rerun all invalidated downstream evidence.

## 2. Requirement Traceability Matrix

| Requirement | Primary phase(s) | Deterministic evidence | Host/semantic evidence |
|---|---:|---|---|
| `LCL-PROD-001` | 0, 4, 8 | docs/manifests consistency | release-copy audit |
| `LCL-SCOPE-001` | 0, 6, 8 | support text | exact Windows host record |
| `LCL-ARCH-001` | 1, 2, 4, 5 | tree/import scan | installed artifact inspection |
| `LCL-ENG-001` | 1, 7 | policy predicates | Engineering cases |
| `LCL-GUIDE-001` | 1, 7 | policy predicates | Guidance cases |
| `LCL-POL-001` | 1, 2, 5 | source/composition/failure tests | Main context observation |
| `LCL-SWITCH-001` | 3, 5, 6 | state matrix | host persistence |
| `LCL-CMD-001` | 3, 5, 6 | parser/block JSON | host prompt-erasure proof |
| `LCL-STATUS-001` | 3, 5, 6 | fixed output tests | displayed boundary text |
| `LCL-LIFE-001` | 2, 3, 5, 6 | synthetic dispatch | live source matrix |
| `LCL-SUB-001` | 2, 3, 5, 6 | composition matrix | live SubagentStart |
| `LCL-HOOK-001` | 4, 5, 6 | hook-map parse | host discovery/trust |
| `LCL-RUN-001` | 2, 5 | node check/import scan | actual host Node version |
| `LCL-INPUT-001` | 2, 5 | adversarial process tests | host payload compatibility |
| `LCL-OUTPUT-001` | 2, 3, 5, 6 | zero/one JSON tests | host context/block behavior |
| `LCL-STATE-001` | 3, 5, 6 | schema/replace/readback | host-local persistence |
| `LCL-FAIL-001` | 2, 3, 5, 6 | failure matrix | disabled/corrupt host cases |
| `LCL-MEASURE-001` | 1, 5, 6, 8 | bytes/code points | no Claude preview/Codex spill |
| `LCL-SEC-001` | 2–6, 8 | static/adversarial/no-disclosure | host control respect |
| `LCL-PKG-001` | 4–6, 8 | JSON/tree/README checks | host validation/discovery |
| `LCL-MIG-001` | 4, 8 | no-mutation scan | manual coexistence docs |
| `LCL-LIC-001` | 4, 8 | notice/revision checks | final artifact audit |
| `LCL-BEH-001` | 7 | frozen case schema | 3-run semantic records |
| `LCL-GO-001` | 8 | complete traceability | tested/release identity |

## 3. GO evidence template

`docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`는 다음 최소 구조를 사용한다.

```markdown
# LeanClarity v1.0 GO Evidence

## Artifact
- LeanClarity version:
- Candidate root/hash:
- OS/architecture:
- Node version:
- Claude Code version/surface:
- Codex version/surface:
- Model/settings used for behavior smoke:

## Source baseline
- Official docs retrieval/check date:
- Ponytail source URL/revision:
- i-have-adhd source URL/revision:

## Requirement results
| Requirement | Applicability rationale | Exact command/interaction | Artifact hash | Host/version/surface | Observation | Status | Evidence location |
|---|---|---|---|---|---|---|---|

## Deterministic local results

## Claude host results

## Codex host results

## Context measurements

## Behavior smoke results

## Packaging, README and license results

## Residual uncertainty
- macOS/Linux: not release-validated
- causal base-host improvement: not evaluated
- statistical reliability/safety guarantee: not claimed

## Final gates
- SPEC GO:
- IMPLEMENTATION GO:
- HOST INTEGRATION GO:
- RELEASE GO:
- COMPLETE GO:
```

## 4. 구현 시작 briefing

구현은 다음 순서로 시작한다.

1. `policies/engineering.md`와 `policies/guidance.md`를 먼저 작성하고 semantic contract를 고정한다.
2. `tests/leanclarity.test.cjs`에 policy/source/composition assertions를 먼저 둔다.
3. `hooks/leanclarity.cjs` 하나에 bounded input, composition, state와 command를 순차 구현한다.
4. 두 manifests와 shared `hooks/hooks.json`을 붙인 뒤 local deterministic gate를 닫는다.
5. 별도 authority checkpoint 후 Windows Claude/Codex 실제 integration을 수행한다.
6. 마지막으로 3-run semantic smoke와 release evidence를 채운다.

첫 implementation phase에서는 policy 두 파일과 그 최소 native tests 외의 feature를 만들지 않는다.
