# LeanClarity v1.0 — Phase 1–5 구현 세션 프롬프트

작업 루트는 `D:\AI_DEV\leancue`다. 이 세션의 목표는 canonical SPEC/PLAN을 변경하지 않고 LeanClarity v1.0을 로컬에서 구현하여 `IMPLEMENTATION GO`를 증명하는 것이다. 실제 Claude Code/Codex 설치·설정 변경, host integration, semantic smoke, 배포, commit, push는 이 목표에 포함하지 않는다.

## 첫 행동

1. `D:\AI_DEV\leancue`에서 현재 workspace guidance와 `git status --short --branch`를 확인한다. 모든 기존 파일은 사용자 소유다. 현재 저장소는 새로 초기화됐고 기존 commit이 없으므로 untracked 파일을 삭제·reset·restore 대상으로 취급하지 않는다.
2. 다음 두 문서를 처음부터 끝까지 읽는다.
   - `D:\AI_DEV\leancue\docs\specs\LeanClarity_v1.0_SPEC.md`
   - `D:\AI_DEV\leancue\docs\plans\LeanClarity_v1.0_PLAN.md`
3. `create_goal` tool이 있으면 token budget 없이 다음 objective로 goal을 생성한다. 없으면 같은 문장을 작업 plan의 objective로 기록한다.

```text
Implement LeanClarity v1.0 through PLAN Phases 1–5 and produce evidence sufficient for IMPLEMENTATION GO, without host installation/configuration, remote writes, publishing, or claiming HOST INTEGRATION GO, RELEASE GO, or COMPLETE GO.
```

4. PLAN Phase 1–5를 각각 plan item으로 만들고 한 번에 하나만 `in_progress`로 둔다. Phase entry condition과 verification을 충족하기 전에는 다음 phase로 넘어가지 않는다.

## 확인된 현재 상태

- Branch: `main`
- Remote configuration: `origin = https://github.com/wotjr1649/leanclarity.git`
- Repository: initialized locally, no baseline commit created by the prior session
- Canonical SPEC SHA-256: `0B633AEE5B54546F70FAB717DEEAF50B125529A0413DF5E1CA12E7BFA039955A`
- Canonical PLAN SHA-256: `E30B43CC3A6B43DF74BE1010BA916914DE913E92C1E9DC95D7C3BC81862713C7`
- SPEC/PLAN local links, 24/24 `LCL-*` traceability IDs, 17 behavior IDs와 Markdown fence 검증은 통과했다.
- 두 독립 검토자가 로컬 Phase 1–5 구현 착수를 `GO`로 판정했다.
- 구현 대상 policy/runtime/manifest/hook/test 파일은 아직 생성되지 않았다.
- `D:\AI_DEV\_refs\ponytail`은 revision `2ed6c52c9d7e5e56942508591085fd45dea277d3`, `D:\AI_DEV\_refs\i-have-adhd`는 revision `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c`에서 clean 상태로 확인됐다. 두 clone은 read-only provenance/policy input이다.
- Official host/Node 문서는 2026-08-28에 검토됐지만 version-sensitive API는 구현 직전에 current official source로 다시 확인해야 한다. Source review는 실제 host evidence가 아니다.

Hash나 전제가 달라졌으면 차이를 먼저 조사한다. 사용자 변경을 덮어쓰지 말고, 독립적으로 이해한 task hunk만 수정한다.

## 고정 제품 계약

다음 결정은 구현 편의를 위해 다시 열지 않는다.

- 제품 계보는 `LeanClarity v1.0`, requirement namespace는 `LCL-*`다.
- Default-on, opt-out, model-interpreted development guidance다. Enforcement, security/compliance control, correctness 또는 safety guarantee가 아니다.
- 사용자 surface는 전체 prompt를 `trim()`하고 `toLowerCase()`한 뒤 정확히 일치하는 세 bare prompt뿐이다.

```text
leanclarity
leanclarity on
leanclarity off
```

- `/leanclarity`, `leanclarity status`, punctuation, extra token, internal newline, 문장 속 언급과 alias는 ordinary prompt다.
- Exact command는 `UserPromptSubmit`에서 처리 후 top-level `decision: "block"`으로 original prompt를 model conversation에서 제거한다. 상태 처리 실패 후에도 인식된 command는 block한다.
- Ordinary prompt는 LeanClarity 내부 실패 때문에 차단하지 않는다.
- Claude와 Codex는 각각 plugin-local boolean state 하나를 가지며 서로 동기화하지 않는다. Project/workspace/session override와 session snapshot은 없다.
- Valid data root에서 state가 absent면 defined default ON이다. State 삭제는 ON reset이다. Corrupt/unreadable state는 추측하지 않는다.
- 새 `SessionStart`/`SubagentStart` invocation은 실행 시점 Saved setting을 읽는다. Existing context는 소급 변경하지 않는다.
- 성공한 새 chat/session `startup` 또는 `/clear`만 Main의 clean boundary다. `resume`, `compact`, Claude `fork`는 inherited boundary다.
- 새 Subagent는 Main clean boundary를 기다리지 않고 현재 Saved setting을 즉시 사용한다.
- ON Main = Engineering + separator + Guidance. ON Subagent = Engineering only. OFF = no LeanClarity policy.
- Main에서는 Engineering 또는 Guidance 하나라도 invalid면 둘 다 주입하지 않는다. Subagent에서는 Engineering이 invalid면 아무것도 주입하지 않는다.
- Runtime truncation, summarization, partial injection, embedded fallback policy, backup, journal, migration, cross-host sync를 만들지 않는다.
- Windows 11 x64의 실제 Claude Code/Codex만 release-validated 대상이다. macOS/Linux는 portable-by-design이며 현재 검증 대상이 아니다.

## 허용된 구현 범위

PLAN Phase 1–5에서 필요한 다음 파일만 최소한으로 만든다.

```text
policies/engineering.md
policies/guidance.md
hooks/leanclarity.cjs
hooks/hooks.json
.claude-plugin/plugin.json
.codex-plugin/plugin.json
tests/leanclarity.test.cjs
README.md
LICENSE
THIRD_PARTY_NOTICES.md
docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md
```

필요성이 실제로 증명되지 않으면 이 목록 밖의 production abstraction/file을 추가하지 않는다. 특히 `package.json`, `node_modules`, dependency, skill, MCP, app, connector, adapter, installer, statusline, database, telemetry, network code, event별 runtime file과 generic framework를 만들지 않는다. Test-owned temporary directory는 허용한다. Candidate distribution에서는 `tests/`와 `docs/evidence/`를 제외한다.

## 구현 순서

### Phase 1 — Canonical policies

- `engineering.md`는 understand-before-minimize, existing reuse, stdlib/native 우선, smallest-correct/root-cause change, safety/validation/accessibility/data-loss protection, non-trivial change의 최소 runnable check를 소유한다.
- `guidance.md`는 useful result/action first, 필요한 bounded steps, tangent 분리, visible completion/verification, work가 남을 때만 next action을 소유한다.
- Detail/exhaustive/output-format/destructive-action/ambiguity/repeated-failure 예외를 보존한다.
- ADHD/medical framing, dopamine/efficacy claim, Lite/Full/Ultra tier, 고정 list/time/length 제한, Ponytail의 three-line/code-first output template을 넣지 않는다.
- Canonical policy 전체를 runtime, tests, README 또는 evidence에 복사하지 않는다. Test는 file content를 읽어 invariant와 composition을 검사한다.

### Phase 2 — Single runtime and composition

- `hooks/leanclarity.cjs` 하나와 Node standard library만 사용한다. Test import는 side-effect free이고 process I/O는 `require.main === module`에서만 시작한다.
- Raw stdin은 BOM 포함 1 MiB 이하, process start 기준 1,000 ms deadline, `TextDecoder` fatal UTF-8, top-level JSON object 하나로 제한한다.
- Codex native `PLUGIN_ROOT`/`PLUGIN_DATA` 중 하나라도 present면 둘 다 non-empty absolute여야 하며 invalid native pair를 Claude variables로 fallback하지 않는다. Native pair가 모두 absent일 때만 valid `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` pair를 사용한다.
- `SessionStart` source allowlist는 Claude `startup/clear/resume/compact/fork`, Codex `startup/clear/resume/compact`다. Missing/unknown/cross-host source에는 policy를 emit하지 않는다.
- Policy는 fixed path의 non-symlink/non-reparse regular file, 각 1 MiB 이하, fatal UTF-8, trim 후 non-empty여야 한다.
- Stdout은 no bytes 또는 actual event name을 담은 valid JSON object 하나다. Log/banner/stack trace를 stdout에 쓰지 않는다. Fixed user-visible string은 UTF-8 512 bytes 이하다.
- Production runtime에서 `child_process`, shell construction, `eval`, `Function`, dynamic loading, network/socket, database, transcript parsing을 사용하지 않는다.

### Phase 3 — State and commands

- State path는 정확히 `<host plugin data>/state.json`, schema는 key 하나 `enabled: boolean`이다.
- Existing target은 `lstat`으로 regular/non-symlink 여부를 검사한다.
- Write는 same-directory exclusive temp → complete UTF-8 JSON → sync/close → native replace without target pre-delete → target reread/schema/value verification 순서다. 전부 성공한 뒤에만 success를 표시한다.
- Absent 또는 byte-readable regular invalid state만 exact on/off로 repair할 수 있다. Unreadable/directory/symlink/reparse/non-regular target을 자동 삭제·교체하지 않는다.
- Concurrent opposing writes 후 file은 complete valid state여야 하고 각 command는 자신의 readback과 일치할 때만 성공을 보고한다.
- Status는 Saved setting과 적용 경계만 표시한다. Current conversation이 정확히 ON/OFF라고 추정하지 않는다.

### Phase 4 — Packaging and operator docs

- 두 manifest의 name/version/description/license를 `leanclarity`/`1.0.0`/동일 metadata로 맞춘다.
- Default `hooks/hooks.json`에 `SessionStart`, `UserPromptSubmit`, `SubagentStart` synchronous command handler만 등록하고 하나의 CJS path를 사용한다.
- README는 exact commands, Saved setting, existing/new/clean/inherited context, Main/Subagent 차이, failure semantics, state deletion reset, support 범위와 no network/telemetry를 실제 구현과 일치하게 설명한다.
- LeanClarity MIT LICENSE를 추가한다.
- `THIRD_PARTY_NOTICES.md`에 두 pinned upstream의 source URL/revision, full MIT notice/copyright와 derived LeanClarity policy 위치를 기록한다. Local upstream LICENSE를 정확히 읽고 작성한다.
- 다른 plugin을 자동 탐지·disable·delete하거나 host config를 rewrite하지 않는다.

### Phase 5 — Deterministic IMPLEMENTATION GO gate

- `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`의 deterministic sections에 candidate identity, exact command/check, observation, status와 evidence location을 기록한다.
- Applicable deterministic row는 전부 PASS여야 한다. `HOLD`, `FAIL`, `BLOCKED`, `NOT RUN`을 PASS로 바꾸거나 `N/A`로 숨기지 않는다.
- Candidate distribution byte set은 두 manifest, `hooks/`, `policies/`, `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`다. Exact file list와 hash를 기록한다.

최소 실행 검증:

```powershell
node --check hooks/leanclarity.cjs
node --test tests/leanclarity.test.cjs
```

추가로 다음을 실제로 확인한다.

- policy source/composition/all-or-nothing matrix
- absent/ON/OFF/corrupt/unreadable/non-regular state matrix
- exact command와 모든 near-match ordinary-prompt cases
- recognized command block과 ordinary prompt fail-open
- 1 MiB boundary, invalid UTF-8/JSON, BOM, no-EOF/deadline
- Claude/Codex source allowlist와 event-correct output
- atomic replace/readback와 injected failure seams
- no prompt/session/transcript/path/environment persistence or echo
- no prohibited imports, dependency, network, global config fallback, plugin-root write, old tier/mode artifacts
- JSON parsing, local Markdown links, candidate file list와 context bytes/code points

Test가 실패하면 root cause가 있는 owning phase로 돌아가 한 번에 한 coherent change만 한다. Test/oracle/security/error handling을 약화해 green으로 만들지 않는다.

## Authority와 stop conditions

- 이 프롬프트는 task root 내부 Phase 1–5 파일 작성과 bounded local tests만 허용한다.
- Claude/Codex plugin 설치, enable/trust, user/global config 수정, 실제 plugin-data mutation, Phase 6 host integration에는 별도 current user authority가 필요하다. 수행하지 말고 `Not verified`로 남긴다.
- `git fetch`, `pull`, `push`, tag/release, remote branch 변경, marketplace/registry publish를 수행하지 않는다.
- Commit 또는 stage를 만들지 않는다. 사용자가 별도로 요청할 때까지 working tree 변경으로 남긴다.
- Canonical SPEC/PLAN, historical LeanCue docs와 pinned upstream clone을 구현 편의로 수정하지 않는다.
- Official API가 SPEC과 충돌하거나 command grammar/state/lifecycle/policy scope 같은 제품 결정을 바꿔야 하면 임의 구현하지 않는다. 해당 phase를 중단하고 정확한 충돌, source와 필요한 SPEC revision을 보고한다.
- Unknown/untrusted code 실행이 필요하면 unrelated secrets와 egress 없이 task-contained 환경을 만들 수 있는지 먼저 판단한다. 그렇지 않으면 static inspection으로 대체하고 남은 위험을 기록한다.

## 완료 조건과 최종 보고

완료는 다음을 모두 의미한다.

- PLAN Phase 1–5 applicable work와 verification이 완료됐다.
- 24개 `LCL-*` requirement traceability에서 implementation-owned deterministic rows가 evidence와 연결됐다.
- Candidate distribution과 deterministic test 대상 byte가 일치한다.
- `IMPLEMENTATION GO` 판정을 증거로 내릴 수 있거나, 불가능한 경우 정확한 failing/blocked row가 남아 있다.
- `HOST INTEGRATION GO`, `RELEASE GO`, `COMPLETE GO`는 실제 증거 없이 주장하지 않는다.

최종 응답은 결과를 먼저 쓰고 다음 label을 포함한다.

```text
Verified: 실행한 command와 관찰한 결과
Not verified: Phase 6 이후 실제 host/semantic/release 항목
Blocked by: 남은 blocker가 있을 때만 정확한 requirement와 원인
```

수정한 파일, 핵심 구현, test pass/fail count, candidate hash와 residual risk를 보고한다. 작업이 전부 끝났으면 사용자에게 불필요한 next action을 만들지 않는다.
