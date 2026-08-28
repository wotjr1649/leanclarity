# LeanCue v1.1 Implementation and Verification Plan

> **Status: Superseded by [LeanClarity v1.0](LeanClarity_v1.0_PLAN.md).**  
> 이 문서는 이전 LeanCue 설계 계보의 실행 계획을 보존하는 historical record다. LeanClarity 구현에 사용하지 않는다.

## 0. 문서 상태와 사용법

| 항목 | 값 |
|---|---|
| 문서 종류 | Executable Implementation Plan |
| Plan 버전 | 1.1 |
| 규범 입력 | [LeanCue_v1.1_SPEC.md](../specs/LeanCue_v1.1_SPEC.md) |
| 현재 단계 | Phase 0 문서 완료, 구현 미착수 |
| 실행 원칙 | 한 phase씩 구현하고 exit evidence를 남긴 뒤 다음 phase로 진행 |

이 PLAN은 새 chat context에서도 한 phase를 독립 실행할 수 있도록 작성됐다.
각 phase를 시작할 때 해당 phase의 `Entry conditions`와 `Documentation and copy sources`를 먼저 읽는다.
SPEC의 계약을 PLAN이 재해석하거나 완화하지 않는다.

모든 구현은 `D:\AI_DEV\leancue`를 task root로 사용한다.
두 upstream clone은 읽기 전용 source다.

```text
D:\AI_DEV\_refs\ponytail
D:\AI_DEV\_refs\i-have-adhd
```

현재 task root는 Git worktree가 아니다. 구현 중 VCS가 추가되지 않는 한 rollback은 phase가 만든 파일과 독립적으로 이해한 hunk에만 적용한다. 기존 v1.0 문서를 덮어쓰거나 삭제하지 않는다.

---

## 1. 실행 전 공통 규칙

### 1.1 작업 규칙

1. phase 시작 전에 관련 파일 상태와 기존 내용을 읽는다.
2. 공식 문서 또는 이 PLAN이 지정한 pinned local source에서 pattern을 확인한다.
3. 가장 작은 complete change를 구현한다.
4. 해당 phase의 가장 작은 falsifying check부터 실행한다.
5. 실패 원인을 고친 뒤 같은 check를 다시 실행한다.
6. exit evidence가 전부 충족된 뒤 다음 phase로 이동한다.
7. 최종 phase 전까지 COMPLETE GO를 선언하지 않는다.

### 1.2 변경 금지

- 기존 v1.0 브리프 삭제 또는 광범위한 교체
- upstream clone 수정
- host global config 자동 수정
- plugin install, hook trust 또는 marketplace 연결의 무단 실행
- 새 npm dependency
- `package.json` 또는 `node_modules/`
- network, telemetry, database, registry
- test skip, warning 억제 또는 failure swallowing
- policy 전문의 runtime 복제
- 검증하지 않은 host/OS 지원 주장

### 1.3 Phase 6 authority checkpoint

Claude 또는 Codex에 local plugin을 설치하거나 Codex hook을 trust하는 작업은 host/plugin 설정 변경이다.
Phase 6을 실행하기 전에 다음 exact effect에 대한 현재 interactive authorization을 확인한다.

```text
- Claude Code가 local LeanCue plugin directory를 로드하는 것
- Codex가 test-only local marketplace 또는 plugin copy를 등록하는 것
- Codex가 현재 LeanCue hook definition을 trust하는 것
- test 후 LeanCue가 만든 test-only host state를 제거하는 것
```

권한이 없으면 Phase 6만 중단하고 Phase 0–5의 local work와 evidence는 보존한다.

---

## Phase 0 — Documentation Freeze

### Entry conditions

- [LeanCue_v1.1_SPEC.md](../specs/LeanCue_v1.1_SPEC.md)가 존재한다.
- 기존 v1.0과 두 upstream clone을 읽을 수 있다.
- 외부 문서 검색에는 private workspace 내용이나 local path를 보내지 않는다.

### Files to create or modify

- `docs/specs/LeanCue_v1.1_SPEC.md`
- `docs/plans/LeanCue_v1.1_PLAN.md`

이 phase에서는 runtime 또는 manifest를 만들지 않는다.

### What to implement

1. SPEC의 support matrix, mode, command grammar, lifecycle, state, failure, security, context와 packaging contract를 서로 모순 없이 고정한다.
2. 모든 규범 요구사항에 `LC-*` ID를 부여한다.
3. 이 PLAN의 traceability matrix가 모든 `LC-*` ID를 정확히 한 번 이상 연결하도록 한다.
4. official API와 local pinned source를 `Allowed APIs`와 `Prohibited assumptions`로 정리한다.
5. 구현 상태와 host 상태를 `NOT VERIFIED`로 유지한다.

### Documentation and copy sources

#### Claude Code official

- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Create plugins](https://code.claude.com/docs/en/plugins)

검증할 계약:

- `SessionStart` source: startup, resume, clear, compact, fork
- `UserPromptSubmit.prompt`
- `UserPromptSubmit` matcher 미지원
- `SubagentStart.agent_id`와 `agent_type`
- `hookSpecificOutput.hookEventName`와 `additionalContext`
- `decision:block`과 `reason`
- `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`
- `claude plugin validate`와 `--plugin-dir`

#### OpenAI official

- [Codex hooks](https://developers.openai.com/codex/hooks)
- [Build plugins](https://developers.openai.com/plugins/build/plugins)
- [Codex plugins](https://developers.openai.com/codex/plugins)

검증할 계약:

- `SessionStart` source: startup, resume, clear, compact
- `UserPromptSubmit.prompt`와 matcher ignored
- `SubagentStart` input과 context output
- plugin hook review/trust
- `features.hooks`와 host controls
- `PLUGIN_ROOT`, `PLUGIN_DATA`
- Claude compatibility environment variables
- handler당 약 2,500-token spill
- default `hooks/hooks.json` discovery

#### Node official

- [Node releases](https://nodejs.org/en/about/previous-releases)
- [Packages and module type](https://nodejs.org/api/packages.html)
- [File system](https://nodejs.org/api/fs.html)
- [Crypto](https://nodejs.org/api/crypto.html)
- [Test runner](https://nodejs.org/api/test.html)

검증할 계약:

- Node 22와 24 LTS
- `.cjs`의 CommonJS 의미
- temp-file-plus-rename
- SHA-256
- `node:test`

#### Pinned local upstream

- `D:\AI_DEV\_refs\ponytail\AGENTS.md`
- `D:\AI_DEV\_refs\ponytail\skills\ponytail\SKILL.md`
- `D:\AI_DEV\_refs\ponytail\hooks\claude-codex-hooks.json`
- `D:\AI_DEV\_refs\ponytail\hooks\ponytail-runtime.js`
- `D:\AI_DEV\_refs\ponytail\hooks\ponytail-mode-tracker.js`
- `D:\AI_DEV\_refs\ponytail\hooks\ponytail-subagent.js`
- `D:\AI_DEV\_refs\i-have-adhd\skills\i-have-adhd\SKILL.md`
- `D:\AI_DEV\_refs\i-have-adhd\hooks\hooks.json`
- `D:\AI_DEV\_refs\i-have-adhd\hooks\always-on.mjs`
- 두 repository의 `LICENSE`

### Allowed APIs

Runtime:

```text
node:fs
node:path
node:crypto
node:process
JSON.parse / JSON.stringify
Buffer.byteLength
String and RegExp standard operations
```

Tests:

```text
node:test
node:assert/strict
node:child_process
node:os
```

Host:

```text
SessionStart
UserPromptSubmit
SubagentStart
hookSpecificOutput.hookEventName
hookSpecificOutput.additionalContext
decision
reason
systemMessage
```

### Prohibited assumptions

- plugin enabled가 Codex hook trusted를 의미한다.
- bare `/leancue`가 두 host의 공통 command다.
- `UserPromptSubmit.matcher`가 동작한다.
- `SubagentStart`를 block할 수 있다.
- Codex에 documented local `codex plugin validate` 명령이 있다.
- host가 skill과 hook context를 자동 deduplicate한다.
- `PLUGIN_DATA`가 uninstall/reinstall 뒤에도 보존된다.
- UTF-8 bytes가 token 수다.
- Node가 host에 bundled되어 있다.

### Verification commands

```powershell
rg -n "^## " docs/specs/LeanCue_v1.1_SPEC.md
rg -n "LC-[A-Z]+-[0-9]{3}" docs/specs/LeanCue_v1.1_SPEC.md
rg -n "LC-[A-Z]+-[0-9]{3}" docs/plans/LeanCue_v1.1_PLAN.md
```

placeholder 또는 미결정 문구를 별도 검색한다. 발견한 항목이 규범 계약에 남아 있으면 phase를 종료하지 않는다.

### Expected observations

- SPEC의 모든 `LC-*` ID가 PLAN traceability matrix에 존재한다.
- 지원 범위와 제외 범위가 서로 겹치지 않는다.
- 구현과 host evidence 상태는 미검증으로 표시된다.
- v1.0은 변경되지 않는다.

### Anti-pattern guards

- 긴 upstream 역사나 조사 로그를 규범 본문에 복사하지 않는다.
- 환경에서 읽을 수 있는 manifest 값과 실제 실행 결과를 여러 section에 중복 캐시하지 않는다.
- API 이름을 기억으로 만들지 않는다.
- 선택지를 나열한 채 구현자에게 결정을 넘기지 않는다.

### Exit evidence

- `SPEC GO`
- SPEC과 PLAN의 Markdown fence와 local link 검사 통과
- 모든 `LC-*` ID traceable
- 구현·host·release 상태는 미검증

### Rollback

Phase 0에서 새로 만든 v1.1 두 파일만 제거하거나 해당 hunk만 되돌린다. v1.0과 upstream source는 건드리지 않는다.

---

## Phase 1 — Canonical Policies

### Entry conditions

- Phase 0 exit evidence가 모두 충족됐다.
- SPEC `LC-POL-001`, `LC-MODE-001`, `LC-BEH-001`을 읽었다.
- pinned upstream revision을 재확인했다.

### Files to create or modify

- `policies/build.md`
- `policies/focus.md`
- `tests/policy.test.cjs`

### What to implement

1. `build.md`를 SPEC의 LITE, FULL, ULTRA sentinel format으로 작성한다.
2. Ponytail compact `AGENTS.md`의 ladder, shared root cause, safety와 runnable-check 원칙을 source로 사용한다.
3. Ponytail full skill의 “code first”, “three lines”, “no essays” 표현 규칙은 Build에 복사하지 않는다.
4. `focus.md`를 medically neutral action-first policy로 새로 작성한다.
5. Focus에 detail, exhaustive findings, destructive action, debug spiral와 real ambiguity 예외를 함께 둔다.
6. Focus에 검증 라벨과 근거 없는 time estimate 금지를 둔다.
7. policy text에는 host API, state path, runtime 명령을 넣지 않는다.

### Documentation and copy sources

Copy candidates:

- Build base: `D:\AI_DEV\_refs\ponytail\AGENTS.md`
- Build safety detail: `D:\AI_DEV\_refs\ponytail\skills\ponytail\SKILL.md`의 ladder, root-cause, safety, hardware, runnable-check sections
- Focus behavior inventory: `D:\AI_DEV\_refs\i-have-adhd\skills\i-have-adhd\SKILL.md`

Do not copy:

- Ponytail Output section
- medical or neurological framing
- “always end with a next action”
- “restate progress every turn”
- ungrounded time estimates
- finding list cap
- install/persistence prose

### Verification commands

```powershell
node --test tests/policy.test.cjs
```

`policy.test.cjs`가 증명할 항목:

- 세 Build sentinel pair가 정확히 한 번 존재
- sentinel nesting과 순서가 유효
- Build mode별 resolved text가 additive
- Focus body가 비어 있지 않음
- medical keywords와 upstream activation command가 없음
- Build policy에 Ponytail presentation template가 없음
- final Main/Subagent authoring target 충족 가능
- policy 전문의 중복 copy가 repository에 없음

### Expected observations

- Lite ⊂ Full ⊂ Ultra
- Build와 Focus의 책임이 겹치지 않음
- policy 파일이 runtime 없이 독립 검토 가능
- marker와 wrapper를 제외한 body가 target 안에 있음

### Anti-pattern guards

- policy를 `skills/`에 두지 않는다.
- runtime code에 fallback 전문을 넣지 않는다.
- policy text에 host-specific command를 넣지 않는다.
- behavior를 짧게 만들기 위해 safety exception을 삭제하지 않는다.
- 원문을 동의어로 장황하게 다시 쓰지 않는다.

### Exit evidence

- `LC-POL-001` PASS
- `LC-MODE-001`의 policy-content 부분 PASS
- `LC-BEH-001`의 policy-content 부분 PASS
- `node --test tests/policy.test.cjs` PASS

### Rollback

Phase 1이 만든 두 policy와 test file만 되돌린다. 다른 phase 파일은 수정하지 않는다.

---

## Phase 2 — Pure Hook Runtime

### Entry conditions

- Phase 1 exit evidence가 모두 충족됐다.
- SPEC sections 12–16과 `LC-HOOK-001`, `LC-LIFE-001`, `LC-RUN-001`을 읽었다.
- 두 host의 현재 hook schema를 공식 reference에서 다시 열었다.

### Files to create or modify

- `hooks/leancue.cjs`
- `tests/runtime.test.cjs`

### What to implement

`hooks/leancue.cjs` 하나에 다음 testable behavior를 둔다.

1. bounded stdin reader
2. BOM 제거와 strict JSON object validation
3. event-specific input validation
4. exact command parser
5. Build sentinel parser
6. mode별 policy resolver
7. Main/Subagent context composer
8. byte/code-point budget validator
9. common structured-output builder
10. top-level fail-open runner

파일을 import하는 test에서 process I/O를 시작하지 않도록 `require.main === module` 경계를 사용한다.
test에 필요한 pure function만 `module.exports`로 노출한다.

### Documentation and copy sources

- Claude input/output examples: [Claude hooks](https://code.claude.com/docs/en/hooks)
- Codex input/output examples: [Codex hooks](https://developers.openai.com/codex/hooks)
- CommonJS contract: [Node packages](https://nodejs.org/api/packages.html)
- no-EOF pattern reference: `D:\AI_DEV\_refs\ponytail\hooks\ponytail-mode-tracker.js`
- nested output reference: `D:\AI_DEV\_refs\ponytail\hooks\ponytail-runtime.js`

Copy the documented field names and nested output shape. Do not transform older `user_prompt` examples.

### Verification commands

```powershell
node --test tests/policy.test.cjs tests/runtime.test.cjs
```

`runtime.test.cjs`가 증명할 항목:

- 세 supported event dispatch
- SessionStart source validation
- UserPromptSubmit의 exact command와 normal prompt 분리
- Subagent output에 Focus 없음
- JSON stdout 앞뒤 noise 없음
- empty/malformed/null/array/scalar input fail-open
- BOM input 성공
- 1 MiB 경계
- complete input과 partial input의 no EOF deadline
- hard limit 초과 시 policy 단위 생략
- unsupported event no-op

### Expected observations

- 정상 synthetic event는 exit 0과 zero-or-one JSON을 반환
- ordinary prompt는 state와 policy output을 만들지 않음
- SubagentStart는 Build만 반환
- error가 uncaught exception으로 process를 종료하지 않음

### Anti-pattern guards

- host별 runtime file을 만들지 않는다.
- plain stdout context와 structured JSON을 섞지 않는다.
- `systemMessage`를 model context로 사용하지 않는다.
- prompt 또는 path를 error text에 넣지 않는다.
- unsupported output field를 추가하지 않는다.
- async hook 또는 child process를 사용하지 않는다.

### Exit evidence

- `LC-HOOK-001` local PASS
- `LC-LIFE-001` synthetic PASS
- `LC-SUB-001` local PASS
- `LC-RUN-001` runtime import scan PASS
- runtime 관련 test 전부 PASS

### Rollback

`hooks/leancue.cjs`와 `tests/runtime.test.cjs`의 Phase 2 변경만 되돌린다.

---

## Phase 3 — State and Commands

### Entry conditions

- Phase 2 exit evidence가 모두 충족됐다.
- SPEC sections 10–11, 17–18과 `LC-CMD-001`, `LC-STATE-001`, `LC-FAIL-001`, `LC-SEC-001`을 읽었다.
- test는 isolated temporary plugin-data directory를 사용할 준비가 됐다.

### Files to create or modify

- `hooks/leancue.cjs`
- `tests/state.test.cjs`
- `tests/runtime.test.cjs`

새 runtime module을 추가하지 않는다.

### What to implement

1. `PLUGIN_DATA || CLAUDE_PLUGIN_DATA` state-root resolution
2. strict `defaults.json`와 session state schema
3. `crypto.createHash("sha256")` session filename
4. new session snapshot materialization
5. temp-file-plus-rename atomic replace
6. intended state reread verification
7. 64-file bounded session retention
8. Current와 Defaults command transition
9. state write 후 `decision:block` status
10. corrupt, missing 또는 unwritable state failure semantics

동시 같은-session write는 last-successful-commit-wins로 구현한다. merge 또는 lock을 추가하지 않는다.

### Documentation and copy sources

- [Node fs](https://nodejs.org/api/fs.html)
- [Node crypto](https://nodejs.org/api/crypto.html)
- SPEC `17. State`
- state behavior 참고: `D:\AI_DEV\_refs\ponytail\hooks\ponytail-config.js`
- command parsing 참고: `D:\AI_DEV\_refs\ponytail\hooks\ponytail-mode-tracker.js`

upstream의 global active file과 non-atomic write는 복사하지 않는다.

### Verification commands

```powershell
node --test tests/state.test.cjs tests/runtime.test.cjs
```

`state.test.cjs`가 증명할 항목:

- compiled Defaults는 full/on
- Current와 Defaults 분리
- 서로 다른 session ID 격리
- session ID 원문 미저장
- 같은 ID resume/clear/compact 유지
- 새 ID가 최신 Defaults snapshot 사용
- 모든 command transition
- Build 변경이 Focus를 보존
- Focus 변경이 Build를 보존
- on/off atomic pair 변경
- corrupt state에서 silent defaults 복원 없음
- write 실패에서 success reason 없음
- concurrent writes 후 valid complete JSON
- last commit이 하나의 허용 state
- 64-file retention
- prune target allowlist
- plugin root write 0건

### Expected observations

- state 파일은 isolated plugin-data 아래에만 생성
- target은 항상 complete schema
- failure 후 이전 valid target 보존
- prompt, cwd, transcript path와 raw session ID가 파일에 없음

### Anti-pattern guards

- `CLAUDE_CONFIG_DIR`, home directory 또는 Codex internal SQLite를 사용하지 않는다.
- user prompt를 filename, shell argument 또는 state body로 사용하지 않는다.
- target 밖 파일을 prune하지 않는다.
- write 실패를 defaults로 덮어 성공 처리하지 않는다.
- concurrency를 해결한다는 명목으로 database나 lock service를 추가하지 않는다.

### Exit evidence

- `LC-CMD-001` local PASS
- `LC-STATE-001` PASS
- `LC-FAIL-001` state 부분 PASS
- `LC-SEC-001` state/path 부분 PASS
- state/runtime test 전부 PASS

### Rollback

Phase 3 code hunk와 test file만 되돌린다. test가 만든 temporary directory는 test-owned absolute path를 확인한 뒤 제거한다.

---

## Phase 4 — Packaging, License, and Operator Documentation

### Entry conditions

- Phase 3 exit evidence가 모두 충족됐다.
- SPEC sections 5, 13, 21–23과 `LC-PKG-001`, `LC-MIG-001`, `LC-LIC-001`을 읽었다.
- 두 upstream LICENSE와 pinned revision을 확인했다.

### Files to create or modify

- `hooks/hooks.json`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`
- `README.md`
- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `tests/packaging.test.cjs`

### What to implement

1. SPEC의 shared `hooks/hooks.json`을 그대로 구현한다.
2. 두 manifest의 name/version/description을 일치시킨다.
3. manifest `hooks`와 존재하지 않는 `skills` field를 생략한다.
4. README에 support matrix, Node prerequisite, activation, status command, mode commands, migration, failure와 uninstall boundary를 적는다.
5. Codex의 plugin enabled와 hook trusted를 별도 단계로 적는다.
6. LeanCue MIT license와 두 upstream notice를 작성한다.
7. public marketplace 제출을 v1 범위로 주장하지 않는다.

### Documentation and copy sources

- [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude local plugin testing](https://code.claude.com/docs/en/plugins)
- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Codex hooks](https://developers.openai.com/codex/hooks)
- `D:\AI_DEV\_refs\ponytail\LICENSE`
- `D:\AI_DEV\_refs\i-have-adhd\LICENSE`

Current Ponytail main의 fixed quoted command와 default hook layout을 참고한다. 이전 validator 문제가 있었던 `commandWindows`는 shared file에 되살리지 않는다.

### Verification commands

```powershell
node --test tests/packaging.test.cjs
claude plugin validate . --strict
```

Claude CLI가 설치되지 않았거나 명령이 현재 version에서 지원되지 않으면 성공으로 간주하지 않고 Phase 6 prerequisite blocker로 기록한다.

`packaging.test.cjs`가 증명할 항목:

- manifest JSON parse
- 두 manifest field 일치
- SemVer `0.1.0`
- default hook file 하나
- 세 event handler 하나씩
- UserPromptSubmit matcher 없음
- command가 fixed path이고 prompt interpolation 없음
- 모든 referenced file 존재
- package/dependency/network adapter 없음
- license와 pinned notices 존재
- README support/migration/trust 문구 존재

### Expected observations

- Claude strict validator warning과 error 0건
- manifest에서 duplicate hook path 0건
- install root에 state/config file 0건
- v1 배포 tree가 SPEC 구조와 일치

### Anti-pattern guards

- Codex에 문서화되지 않은 local validate command를 만들거나 주장하지 않는다.
- public submission metadata를 미리 만들지 않는다.
- README에 bare `/leancue`를 공통 contract로 쓰지 않는다.
- 다른 plugin을 자동 disable 또는 uninstall하지 않는다.
- Node fallback을 추가하지 않는다.

### Exit evidence

- `LC-PKG-001` local/Claude static PASS
- `LC-MIG-001` documentation PASS
- `LC-LIC-001` PASS
- packaging test와 Claude strict validation PASS

### Rollback

Phase 4가 만든 manifest, hook map, README와 license/notice/test만 되돌린다. host에는 아직 설치하지 않는다.

---

## Phase 5 — Deterministic Local Verification

### Entry conditions

- Phase 4 exit evidence가 모두 충족됐다.
- 지원 Node 22 또는 24 환경에서 실행 중이다.
- test가 workspace 밖 user/global state를 사용하지 않는다.

### Files to create or modify

- Phase 1–4 test files
- 필요할 때만 test helper를 기존 test file 안에 추가
- `docs/GO_EVIDENCE.md`의 Local Verification section

새 test framework, fixture library 또는 package metadata를 만들지 않는다.

### What to implement

결정론적 matrix를 완성한다.

#### Mode matrix

| Build | Focus | Main | Subagent |
|---|---|---|---|
| off | off | 없음 | 없음 |
| off | on | Focus | 없음 |
| lite | off | Build lite | Build lite |
| lite | on | Build lite + Focus | Build lite |
| full | off | Build full | Build full |
| full | on | Build full + Focus | Build full |
| ultra | off | Build ultra | Build ultra |
| ultra | on | Build ultra + Focus | Build ultra |

#### Failure matrix

- empty stdin
- malformed JSON
- UTF-8 BOM
- null, array, scalar
- missing event
- invalid source
- missing/invalid session ID
- missing/corrupt Defaults
- missing/corrupt Current
- missing one policy
- missing both policies
- 1 MiB boundary와 overflow
- complete input without EOF
- partial input without EOF
- closed stdout와 EPIPE
- path containing spaces
- Windows separators
- shell metacharacters in path와 prompt
- missing plugin root
- missing/unwritable data root
- concurrent sessions
- concurrent same-session writes
- context hard-limit boundary

### Documentation and copy sources

- SPEC normative requirements
- [Node test runner](https://nodejs.org/api/test.html)
- [Node child process](https://nodejs.org/api/child_process.html)
- upstream test patterns:
  - `D:\AI_DEV\_refs\ponytail\tests\hooks.test.js`
  - `D:\AI_DEV\_refs\ponytail\tests\hooks-windows.test.js`
  - `D:\AI_DEV\_refs\i-have-adhd\tests\test_always_on_hooks.py`

테스트 case의 의미만 참고하고 Python 또는 broader adapter harness는 복사하지 않는다.

### Verification commands

```powershell
node --version
node --test
```

Node 22와 24에서 각각 같은 suite를 실행한다. 현재 machine에 없는 major를 global install하지 않는다. 별도 허용된 CI 또는 이미 존재하는 해당 major 환경에서 실행하고 exact version을 evidence에 기록한다.

추가 static checks:

```powershell
rg -n "child_process|fetch\(|https?:|node_modules|package\.json" hooks policies .claude-plugin .codex-plugin
rg -n "CLAUDE_CONFIG_DIR|CODEX_HOME|sqlite" hooks
rg -n "commandWindows|additionalContextLimit.:.0|async.:.true" hooks
```

Expected static match는 0건이다.

### Expected observations

- `node --test` failure 0
- 8/8 mode rows PASS
- 각 활성 marker 정확히 1회
- 비활성 marker 0회
- ordinary prompt state mutation 0
- 모든 fail-open case exit 0
- timeout 안에 child 종료
- state와 context hard limit 충족
- plugin root write 0

### Anti-pattern guards

- actual host 동작을 local synthetic test로 통과했다고 주장하지 않는다.
- model behavior를 string equality로 테스트하지 않는다.
- flaky timing을 무한 retry하지 않는다.
- test를 위한 production bypass를 넣지 않는다.
- temp cleanup target을 workspace root, home 또는 unresolved path로 잡지 않는다.

### Exit evidence

- `LC-MODE-001` deterministic PASS
- `LC-HOOK-001` local PASS
- `LC-LIFE-001` synthetic PASS
- `LC-SUB-001` local PASS
- `LC-RUN-001` Node 22/24 PASS
- `LC-STATE-001` PASS
- `LC-FAIL-001` local PASS
- `LC-SEC-001` local PASS
- `LC-CTX-001` local PASS
- `GO_EVIDENCE.md` local rows에 실패·미실행 0개

### Rollback

Phase 5가 추가한 test/evidence hunk만 되돌린다. test-owned temp path는 absolute resolved target과 ownership marker를 확인한 뒤 제거한다.

---

## Phase 6 — Real Host Integration

### Entry conditions

- Phase 5 exit evidence가 모두 충족됐다.
- `1.3 Phase 6 authority checkpoint`의 exact effect가 현재 turn에서 승인됐다.
- 지원 host binary와 version을 기록했다.
- 기존 Ponytail/i-have-adhd hook 상태를 읽기 전용으로 확인했다.
- 중복 hook이 있으면 사용자가 직접 비활성화했거나 해당 test를 isolated profile에서 실행한다.

### Files to create or modify

- `docs/GO_EVIDENCE.md`
- test-only local marketplace 또는 host profile은 승인된 위치에만 생성

배포 source는 host test를 통과시키기 위한 임시 수정 없이 Phase 5 artifact 그대로 사용한다.

### What to implement

#### Claude Code

1. strict plugin validation
2. `claude --plugin-dir .` local load
3. `/hooks`에서 LeanCue source와 handler 세 개 확인
4. startup, resume, clear, compact, fork 관찰
5. `leancue` status와 모든 mode category 관찰
6. command가 model task로 전달되지 않는지 확인
7. Main Build+Focus와 Subagent Build-only marker 확인
8. plugin reload 후 code/state path 분리 확인
9. workspace path containing spaces에서 반복

#### Codex

1. 승인된 test-only local marketplace 또는 documented local install flow 사용
2. plugin disabled 상태 확인
3. plugin enabled but hook untrusted 상태 확인
4. `/hooks`에서 current hook definition review/trust
5. trusted 상태에서 startup, resume, clear, compact 관찰
6. `features.hooks=false` isolated test에서 hook 미실행 확인
7. status/mode command와 block reason 확인
8. Main Build+Focus와 Subagent Build-only marker 확인
9. desktop app와 CLI에서 각각 확인
10. output spill path 또는 preview가 없는지 확인

### Documentation and copy sources

- [Claude local testing](https://code.claude.com/docs/en/plugins)
- [Claude plugin validation and debug](https://code.claude.com/docs/en/plugins-reference)
- [Codex plugins](https://developers.openai.com/codex/plugins)
- [OpenAI plugin test workflow](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Codex hooks trust and controls](https://developers.openai.com/codex/hooks)

### Verification commands and interactions

Claude:

```text
claude --version
claude plugin validate . --strict
claude --plugin-dir .
/hooks
/plugin
/reload-plugins
```

Codex:

```text
codex --version
codex
/plugins
/hooks
```

Codex local marketplace command는 실행 시점의 official docs에서 exact syntax를 다시 확인한다. 문서에 없는 command를 추정하지 않는다.

### Expected observations

- Claude handler가 event당 한 번
- Claude fork source가 현재 version에서 관찰됨
- Codex trust 전 handler 미실행
- Codex trust 후 handler 실행
- host hooks disabled일 때 LeanCue가 우회하지 않음
- command reason이 짧고 prompt가 model task가 되지 않음
- Main/Subagent marker scope 정확
- duplicate marker와 large-output spill 0건

### Anti-pattern guards

- trust 또는 global hooks feature를 파일 직접 편집으로 몰래 변경하지 않는다.
- host test를 위해 validation, timeout 또는 failure handling을 약화하지 않는다.
- test-only marketplace를 배포물에 포함하지 않는다.
- 다른 plugin을 자동 삭제하지 않는다.
- transcript에서 prompt 또는 secret을 evidence로 복사하지 않는다.

### Exit evidence

- `LC-SCOPE-001` host surface PASS
- `LC-CMD-001` 두 host PASS
- `LC-HOOK-001` 두 host PASS
- `LC-LIFE-001` Claude 5/Codex 4 PASS
- `LC-SUB-001` 두 host PASS
- `LC-FAIL-001` host PASS
- `LC-CTX-001` no-spill PASS
- `LC-PKG-001` Codex install/Claude validate PASS

### Rollback

승인된 test-only LeanCue plugin/marketplace/profile state만 host가 제공하는 정상 제거 경로로 제거한다. 기존 plugin, global config 또는 unrelated host state를 삭제·reset하지 않는다. Codex hook trust record 제거가 별도 host effect이면 같은 authorization 범위를 확인한다.

---

## Phase 7 — Behavior Regression

### Entry conditions

- Phase 6 exit evidence가 모두 충족됐다.
- Claude와 Codex에서 사용할 exact model/version을 기록했다.
- semantic oracle와 pass threshold를 SPEC `24`에서 읽었다.

### Files to create or modify

- `docs/GO_EVIDENCE.md`의 Behavior section

별도 eval framework를 만들지 않는다.

### What to implement

각 host에서 다음 case를 세 번 실행한다.

1. native-first
2. existing reuse
3. shared root-cause
4. action-first
5. detailed explanation
6. exhaustive findings
7. safety/validation 유지
8. Build off + Focus on
9. Build full + Focus off
10. Build ultra + Focus on

각 run에는 다음만 기록한다.

- host와 version
- model identifier
- mode
- case ID
- semantic oracle PASS/FAIL
- 짧은 non-sensitive 근거

user prompt 전문, workspace secret 또는 transcript 전체를 evidence에 복사하지 않는다.

### Documentation and copy sources

- SPEC `24. Behavior acceptance`
- `D:\AI_DEV\_refs\i-have-adhd\evals\rubric.md`의 correctness/autonomy/actionability/safety/concision 관점
- `D:\AI_DEV\_refs\ponytail\tests\behavior.test.js`의 semantic behavior 관점

upstream의 model score나 benchmark 수치를 LeanCue evidence로 재사용하지 않는다.

### Verification

- Safety: host별 3/3
- 나머지 case: host별 각 2/3 이상
- orthogonality failure: 0
- inactive policy marker: 0
- exact prose 비교: 사용하지 않음

### Expected observations

- Build와 Focus가 독립적으로 관찰됨
- detailed/exhaustive 요청이 brevity 규칙에 의해 잘리지 않음
- Ultra가 안전 규칙을 제거하지 않음
- 동일 model/version run끼리만 집계

### Anti-pattern guards

- 한 번의 좋은 응답을 behavior guarantee로 일반화하지 않는다.
- FAIL case를 prompt에서 제외하지 않는다.
- model failure를 숨기기 위해 pass threshold를 낮추지 않는다.
- clinical 또는 ADHD efficacy를 평가하거나 주장하지 않는다.

### Exit evidence

- `LC-BEH-001` 두 host PASS
- 모든 case/run이 `GO_EVIDENCE.md`에 traceable
- failure 또는 미실행 case 0

### Rollback

Behavior evidence hunk만 되돌린다. model 또는 host 설정을 변경했다면 승인된 test-only 변경만 정상 경로로 원복한다.

---

## Phase 8 — Release Audit and COMPLETE GO

### Entry conditions

- Phase 0–7 exit evidence가 모두 충족됐다.
- 배포 후보 artifact가 고정됐다.
- release candidate와 검증 candidate가 동일하다.

### Files to create or modify

- `docs/GO_EVIDENCE.md`
- 필요하면 README의 observed version 표

규범 계약이나 runtime behavior를 이 phase에서 새로 변경하지 않는다. 변경이 필요하면 영향을 받는 이전 phase로 돌아간다.

### What to implement

1. 모든 `LC-*` requirement의 test와 evidence 상태를 집계한다.
2. 두 manifest version과 배포 tree를 확인한다.
3. dependency, network, telemetry, database, registry와 plugin-root write를 재검색한다.
4. README activation, trust, migration, failure와 support claim을 실제 관찰과 대조한다.
5. license와 third-party notices를 대조한다.
6. exact `leancue` namespace를 GitHub, npm, 공개 Claude catalog와 공개 Codex marketplace에서 재검색한다.
7. 최종 distribution file별 SHA-256 hash set을 evidence에 기록한다.
8. red 또는 미검증 row가 없을 때만 COMPLETE GO를 기록한다.

### Documentation and copy sources

- SPEC `1, `21–26
- 이 PLAN의 traceability matrix
- 현재 공식 Claude/OpenAI plugin 문서
- upstream pinned LICENSE
- 실제 Phase 6–7 evidence

### Verification commands

```powershell
node --test
claude plugin validate . --strict
rg -n "child_process|fetch\(|https?:|node_modules|package\.json" hooks policies .claude-plugin .codex-plugin
rg -n "CLAUDE_CONFIG_DIR|CODEX_HOME|sqlite|commandWindows" hooks
Get-ChildItem -LiteralPath '.claude-plugin','.codex-plugin','hooks','policies' -File -Recurse | Sort-Object FullName | Get-FileHash -Algorithm SHA256
Get-FileHash -Algorithm SHA256 -LiteralPath 'README.md','LICENSE','THIRD_PARTY_NOTICES.md'
```

`https?:` 검색은 manifest/README/doc link가 아니라 runtime source 범위에서 0건이어야 한다.

### Expected observations

- deterministic tests 100% PASS
- host matrix 전부 PASS
- behavior threshold 전부 PASS
- 모든 `LC-*` row PASS
- manifest version 일치
- final distribution file hash set 기록
- 배포 후보와 검증 후보 동일

### Anti-pattern guards

- 문서 상태만 바꿔 COMPLETE GO를 만들지 않는다.
- 실행하지 않은 check를 PASS로 기록하지 않는다.
- name search를 trademark clearance로 부르지 않는다.
- release 직전 failure를 warning으로 낮추지 않는다.
- final phase에서 unrelated refactor를 하지 않는다.

### Exit evidence

```text
SPEC GO
IMPLEMENTATION GO
HOST INTEGRATION GO
RELEASE GO
COMPLETE GO
```

### Rollback

Release audit에서 failure가 나오면 COMPLETE GO를 기록하지 않고 영향 phase를 다시 연다. 검증되지 않은 artifact를 publish 또는 install하지 않는다.

---

## Requirement Traceability Matrix

| Requirement | Primary phase | Deterministic evidence | Host/behavior evidence | COMPLETE GO condition |
|---|---:|---|---|---|
| `LC-SCOPE-001` | 0, 4 | support/packaging assertions | exact OS/host/version record | 모두 PASS |
| `LC-ARCH-001` | 4 | tree/import scan | installed artifact tree | 모두 PASS |
| `LC-POL-001` | 1 | policy uniqueness test | duplicate marker 0 | 모두 PASS |
| `LC-MODE-001` | 1, 5 | 8-row matrix | orthogonality controls | 모두 PASS |
| `LC-CMD-001` | 3 | parser/transition tests | Claude/Codex block UX | 모두 PASS |
| `LC-HOOK-001` | 2, 4 | schema/dispatch tests | `/hooks` registration | 모두 PASS |
| `LC-LIFE-001` | 2, 5 | synthetic sources | Claude 5, Codex 4 | 모두 PASS |
| `LC-SUB-001` | 2, 5 | marker assertions | real subagent context | 모두 PASS |
| `LC-RUN-001` | 2, 5 | import scan, Node 22/24 | host PATH execution | 모두 PASS |
| `LC-STATE-001` | 3, 5 | isolation/atomic/prune | lifecycle persistence | 모두 PASS |
| `LC-FAIL-001` | 2, 3, 5 | failure matrix | host session remains usable | 모두 PASS |
| `LC-SEC-001` | 2, 3, 5 | input/path/log tests | non-secret evidence | 모두 PASS |
| `LC-CTX-001` | 1, 2, 5 | byte/code-point assertions | no spill on both hosts | 모두 PASS |
| `LC-PKG-001` | 4, 6 | packaging tests, Claude strict validation | Codex install | 모두 PASS |
| `LC-MIG-001` | 4 | README assertions | duplicate-source check | 모두 PASS |
| `LC-LIC-001` | 4 | license/notice assertions | release artifact inspection | 모두 PASS |
| `LC-BEH-001` | 7 | policy-content assertions | semantic repeated eval | 모두 PASS |
| `LC-GO-001` | 8 | traceability completeness | all evidence rows | 모두 PASS |

모든 requirement는 deterministic evidence와 필요한 outside-host evidence를 구분한다. local test가 host evidence를 대체하지 않는다.

---

## GO_EVIDENCE.md 형식

Phase 5에서 다음 형식으로 파일을 생성한다.

```markdown
# LeanCue v1 GO Evidence

## Artifact

- Version:
- SHA-256:
- Node:
- Claude Code:
- Codex desktop:
- Codex CLI:
- OS:

## Requirement Results

| Requirement | Check | Command or interaction | Observation | Status |
|---|---|---|---|---|

Allowed status:

- PASS
- FAIL
- BLOCKED
- NOT RUN

## Local Test Results

## Claude Host Results

## Codex Host Results

## Behavior Results

## Packaging and License Results

## Name Recheck

## Final Gate

- SPEC:
- IMPLEMENTATION:
- HOST INTEGRATION:
- RELEASE:
- COMPLETE:
```

COMPLETE GO에서는 모든 applicable row가 PASS여야 한다. FAIL, BLOCKED 또는 NOT RUN이 하나라도 있으면 COMPLETE는 GO가 아니다.

---

## 최종 체크리스트

### SPEC GO

- [ ] 미결정 설계 항목 0
- [ ] 모든 규범 요구사항에 `LC-*` ID 존재
- [ ] 모든 ID가 traceability matrix에 존재
- [ ] support matrix와 non-goal이 명시됨
- [ ] 공식 API reference 재확인

### IMPLEMENTATION GO

- [ ] Node 22 tests PASS
- [ ] Node 24 tests PASS
- [ ] 8/8 mode matrix PASS
- [ ] failure matrix PASS
- [ ] runtime third-party dependency 0
- [ ] network/telemetry/database/registry 0
- [ ] plugin-root state write 0

### HOST INTEGRATION GO

- [ ] Claude strict validation PASS
- [ ] Claude 5 lifecycle sources PASS
- [ ] Codex 4 lifecycle sources PASS
- [ ] Codex untrusted/trusted/disabled observations PASS
- [ ] Codex desktop PASS
- [ ] Codex CLI PASS
- [ ] Main/Subagent scope PASS
- [ ] command block/status UX PASS
- [ ] duplicate policy marker 0
- [ ] large-output spill 0

### RELEASE GO

- [ ] 두 manifest version 일치
- [ ] README와 observed behavior 일치
- [ ] upstream notices와 revisions 정확
- [ ] exact name 재검색 완료
- [ ] release distribution file hash set 기록
- [ ] traceability row 전부 PASS
- [ ] 검증 candidate와 release candidate 동일

### COMPLETE GO

- [ ] SPEC GO
- [ ] IMPLEMENTATION GO
- [ ] HOST INTEGRATION GO
- [ ] RELEASE GO

체크박스는 관찰 증거가 있는 경우에만 완료한다.
