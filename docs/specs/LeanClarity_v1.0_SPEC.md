# LeanClarity v1.0 Normative Specification

## 0. 문서 상태

| 항목 | 상태 |
|---|---|
| 문서 종류 | Normative Product and Runtime Specification |
| 제품 계보 | LeanClarity |
| 문서 버전 | 1.3 (section 19 개정 이력 참조) |
| 설계 상태 | SPEC GO |
| 구현 상태 | NOT VERIFIED |
| Host 통합 상태 | NOT VERIFIED |
| Release 상태 | NOT VERIFIED |
| 최종 판정 | COMPLETE GO NOT GRANTED |

이 문서는 LeanClarity v1.0의 유일한 규범 제품 계약이다. 구현 순서와 검증 절차는 [LeanClarity_v1.0_PLAN.md](../plans/LeanClarity_v1.0_PLAN.md)가 소유한다.

[LeanCue v1.1 SPEC](LeanCue_v1.1_SPEC.md)과 [LeanCue v1.1 PLAN](../plans/LeanCue_v1.1_PLAN.md)은 이전 설계 계보의 역사 기록이다. LeanClarity는 LeanCue의 rename, minor revision 또는 호환 계층이 아니다. 두 계보가 충돌하면 LeanClarity 구현에는 이 문서만 적용한다.

Normative requirement ID는 `LCL-*` namespace를 사용한다. 이전 `LC-*` ID는 재사용하거나 변환하지 않는다.

## 1. 제품 정의와 주장 한계

### 1.1 제품 약속

> LeanClarity는 Claude Code와 Codex가 가장 작은 올바른 엔지니어링 해결책을 우선하고, 결과를 명확하고 실행 가능한 형태로 전달하도록 유도하는 기본 ON, opt-out 개발 정책 플러그인이다.

> LeanClarity is a default-on, opt-out development policy that steers Claude Code and Codex toward the smallest correct engineering solution and clear, actionable communication.

LeanClarity는 Ponytail과 i-have-adhd의 단순 합집합, 원본 prompt concatenation 또는 compatibility wrapper가 아니다. 두 upstream의 유용한 행동을 하나의 제품 약속으로 다시 설계한 opinionated plugin이다.

### 1.2 비보장

LeanClarity는 model-interpreted guidance다. 다음을 주장하지 않는다.

- deterministic enforcement, correctness guarantee 또는 policy-compliance guarantee
- security control, permission boundary, sandbox, guard 또는 compliance mechanism
- 모든 응답의 minimality, formatting, safety 또는 품질 보장
- base host 대비 인과적 개선, 개선율 또는 통계적 reliability
- 모든 host/model/version/task로 일반화되는 효능

Host의 system/developer/workspace/user instruction hierarchy와 실제 safety control은 LeanClarity보다 우선한다. LeanClarity는 guard, approval, permission, validation 또는 failure handling을 약화시키지 않는다.

## 2. COMPLETE GO

`COMPLETE GO`는 다음 네 gate의 논리곱이다.

```text
COMPLETE GO
= SPEC GO
  AND IMPLEMENTATION GO
  AND HOST INTEGRATION GO
  AND RELEASE GO
```

### 2.1 SPEC GO

다음이 모두 규범적으로 닫혀야 한다.

- 제품명과 slug
- 단일 ON/OFF 상태와 persistence 범위
- 세 command와 exact-match grammar
- 기존 context와 새 hook context의 전환 의미
- Main/Subagent policy scope
- policy source, failure atomicity, precedence
- host lifecycle, input/output, state, security, packaging 계약
- behavior smoke gate와 주장 한계

### 2.2 IMPLEMENTATION GO

다음이 모두 실제 artifact에서 관찰되어야 한다.

- 두 canonical policy와 한 Node runtime이 구현됐다.
- deterministic state, command, composition, failure, security, packaging tests가 전부 통과했다.
- shipped runtime에 dependency, network, telemetry, database, registry 또는 global-host mutation이 없다.
- 문서와 artifact의 이름, 경로, schema, behavior가 일치한다.

### 2.3 HOST INTEGRATION GO

Windows 11 x64에서 release candidate 자체를 사용해 Claude Code와 Codex의 다음 동작을 실제로 관찰해야 한다.

- default ON과 OFF persistence
- `SessionStart`, `UserPromptSubmit`, `SubagentStart`
- exact command interception과 original prompt blocking
- Main Engineering + Guidance, Subagent Engineering only
- 새 chat과 `/clear` 전환 경계
- resume/compact/fork의 비보장 경계
- plugin disabled/untrusted/unavailable 시 host control 존중

Synthetic payload test는 실제 host evidence를 대체하지 않는다.

Policy 파일만 바뀐 candidate가 predecessor의 관측 중 무엇을 승계하고 무엇을 다시 관측해야 하는지는 section 17.1이 정한다.

### 2.4 RELEASE GO

다음이 모두 충족돼야 한다.

- 실제 검증한 OS, Node, host, model, LeanClarity version이 기록됐다.
- semantic behavior smoke gate가 두 host에서 통과했다.
- README, LICENSE, THIRD_PARTY_NOTICES와 support claim이 artifact와 일치한다.
- release artifact와 tested artifact가 동일하다.
- applicable requirement 또는 semantic case에 `FAIL`, `BLOCKED`, `NOT RUN`, `HOLD`가 없다.

문서를 `PASS`로 고치는 행위만으로 어떤 gate도 통과하지 않는다.

## 3. 용어

| 용어 | 정의 |
|---|---|
| Product name | `LeanClarity` |
| Plugin slug | `leanclarity` |
| Host ready | Host가 plugin을 설치·활성·신뢰하고 hook 실행을 허용한 상태. Saved setting과 별개다. |
| Saved setting | 해당 host plugin-data에 저장된 `enabled` boolean 또는 state 부재 시 defined default `ON` |
| ON | 새 eligible hook event가 scope에 맞는 LeanClarity policy를 주입하는 상태 |
| OFF | 새 eligible hook event가 LeanClarity policy를 주입하지 않는 상태 |
| Existing context | 이미 만들어져 policy text를 보유할 수 있는 Main/Subagent context |
| New hook context | 실행 시점의 Saved setting을 읽는 새 `SessionStart` 또는 `SubagentStart` hook invocation |
| Clean main boundary | 새 chat/session의 `startup` 또는 `/clear`; Host ready 상태에서 eligible hook invocation이 성공했을 때 Main이 Saved setting에 맞게 시작하는 경계 |
| Inherited boundary | `resume`, `compact`, `fork`; 이전 context가 남을 수 있어 정확한 effective state를 주장하지 않는 경계 |
| Engineering Policy | 엔지니어링 판단을 소유하는 canonical policy |
| Guidance Policy | 사용자-facing 전달 구조를 소유하는 canonical policy |
| Main | 사용자와 직접 상호작용하는 root agent context |
| Subagent | host의 SubagentStart event로 시작되는 delegated agent context |
| Unavailable | state, policy, runtime 또는 host 문제로 해당 event에 policy를 안전하게 주입할 수 없는 상태. 사용자 설정값이 아님 |
| Private policy | user-invocable/discoverable skill이 아니라는 뜻. 비밀 또는 confidential source라는 뜻이 아님 |

## 4. 지원 환경과 제외 범위

### 4.1 v1 release-validated 범위

LeanClarity v1은 다음 범위에서만 `supported and release-validated`를 주장한다.

- Windows 11 x64
- 실제 검증한 Claude Code plugin host
- 실제 검증한 Codex plugin host
- 해당 host hook이 실행한 실제 Node.js version

SPEC은 Claude Code, Codex 또는 Node의 특정 version을 영구 고정하지 않는다. 각 release evidence가 다음을 기록한다.

```text
OS and architecture
Node version
Claude Code version and exercised surface
Codex version and exercised surface
LeanClarity version/artifact hash
model and relevant settings for behavior tests
executed integration tests and results
```

### 4.2 portable-by-design

Runtime은 Node standard library와 portable path API만 사용한다. macOS와 Linux 호환을 의도하지만 실제 host integration을 완료하기 전에는 `supported`, `verified`, `GREEN` 또는 `GO`로 표현하지 않는다.

### 4.3 v1 제외 범위

- macOS/Linux release support claim
- Claude ↔ Codex state synchronization
- project/repository/workspace/session별 override
- LITE/FULL/ULTRA 또는 다른 intensity
- Engineering/Guidance 독립 switch
- skill, slash command, statusline, MCP, app, connector, LSP, agent bundle
- Python, shell 또는 bundled Node fallback runtime
- package dependency, installer, daemon, service, database, telemetry, analytics, network
- upstream state/command migration 또는 compatibility alias
- public registry/directory publication
- base-host 대비 A/B improvement claim

## 5. 제품 불변식과 구조

### 5.1 사용자-facing 상태

사용자가 제어하는 값은 `ON`과 `OFF`뿐이다.

```text
LeanClarity ON  = Engineering Policy + Guidance Policy for Main
LeanClarity ON  = Engineering Policy only for Subagent
LeanClarity OFF = no LeanClarity policy injection
```

Host-level plugin enable/trust와 LeanClarity Saved setting은 서로 다른 상태다. Runtime은 host 설정을 스스로 설치, 활성화, trust, 수정 또는 복구하지 않는다.

LeanClarity가 ON이면 runtime task classifier 없이 자동 적용한다. 비개발 요청에서도 runtime은 별도 mode로 전환하지 않는다. 적용할 엔지니어링 판단이 없으면 Engineering 규칙이 자연스럽게 무관할 뿐이다.

### 5.2 최소 배포 구조

구현 artifact는 다음 구조를 기준으로 한다.

```text
.
├─ .claude-plugin/
│  └─ plugin.json
├─ .codex-plugin/
│  └─ plugin.json
├─ hooks/
│  ├─ hooks.json
│  └─ leanclarity.cjs
├─ policies/
│  ├─ engineering.md
│  └─ guidance.md
├─ tests/
│  ├─ leanclarity.test.cjs
│  └─ behavior-cases.jsonl                  # release smoke용 synthetic fixtures
├─ docs/
│  ├─ specs/LeanClarity_v1.0_SPEC.md
│  ├─ plans/LeanClarity_v1.0_PLAN.md
│  └─ evidence/LeanClarity_v1.0_GO_EVIDENCE.md   # verification 때 생성하는 release record
├─ README.md
├─ LICENSE
└─ THIRD_PARTY_NOTICES.md
```

`package.json`, `node_modules`, `skills/`, event별 runtime file, host adapter layer와 generic framework는 v1에 없다.

`tests/`와 `docs/evidence/`는 source/release 검증 자산이며 설치되는 plugin distribution에는 포함하지 않는다. Frozen candidate distribution은 두 manifest, `hooks/`, `policies/`, `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`의 정확한 byte 집합이다. GO evidence는 candidate를 freeze한 뒤 그 hash를 참조하며, “tested artifact = release artifact”는 이 distribution byte 집합에 적용한다.

### 5.3 canonical ownership

- `policies/engineering.md`가 Engineering Policy의 유일한 원본이다.
- `policies/guidance.md`가 Guidance Policy의 유일한 원본이다.
- runtime, tests, README, manifests 또는 evidence에 전체 policy fallback copy를 두지 않는다.
- policy 파일은 symlink/reparse point가 아닌 regular file이고 raw size가 각각 1 MiB 이하여야 하며, fatal UTF-8 decode가 성공하고 `trim()` 후 비어 있지 않아야 한다.
- 별도 frontmatter, sentinel, parser schema 또는 mode block을 요구하지 않는다.

## 6. Policy 계약

### 6.1 Engineering Policy

Engineering은 무엇을 만들고 어디를 수정할지를 결정한다. 다음 행동을 보존한다.

1. 요청과 관련 실행 흐름을 이해하고 필요한 caller/shared path를 확인한 뒤 단순화한다.
2. 요구를 충족하는 데 불필요한 기능과 speculative scaffolding은 만들지 않는다.
3. `existing code → standard library → native platform → already-installed dependency → minimum new implementation` 순서로 검토한다.
4. implementation 하나뿐인 interface, product 하나뿐인 factory, 미래용 config, wrapper, provider와 과도한 file split을 근거 없이 추가하지 않는다.
5. bug symptom만 막지 않고 가능한 가장 작은 공통 root cause를 수정한다.
6. 목표는 shortest patch가 아니라 smallest correct patch다.
7. trust-boundary validation, security, data-loss prevention, accessibility, correctness guard와 필요한 failure handling은 단순화하지 않는다.
8. branch, loop, parser 또는 security-sensitive logic 같은 non-trivial change에는 가장 작은 runnable verification을 남긴다.
9. 사용자가 분석, 설명, 보고 또는 review만 요청했다면 구현을 강제하지 않는다.

Engineering은 response formatting을 소유하지 않는다. Hardware calibration 같은 domain-specific upstream 규칙은 v1 core invariant가 아니다.

### 6.2 Guidance Policy

Guidance는 결과를 사용자가 이해하고 실행할 수 있게 전달한다.

1. 유용한 결론이나 사용자가 실행할 action이 있으면 먼저 제시한다.
2. 실제 multi-step work만 경계가 분명한 최소 번호 단계로 구성한다.
3. 현재 요청을 완료한 뒤 별도 tangent를 분리한다.
4. 여러 turn 작업에서는 완료, 검증, 남은 실패와 현재 단계를 필요한 만큼 보이게 한다.
5. 사용자에게 남은 일이 있을 때만 하나의 구체적인 next action을 제시한다.
6. 요청된 상세 설명, walkthrough, exhaustive review와 모든 material finding을 임의의 brevity/list cap으로 자르지 않는다.
7. 사용자가 요구한 code-only 등 명시적 output format을 존중한다.
8. destructive effect 전에는 확인하고, 실제 blocking ambiguity에는 한 번의 간결한 질문을 사용한다.
9. 같은 목표의 반복 실패에서는 의심되는 가정을 드러내고 진단 근거를 요구한다.
10. error와 verification은 관찰한 사실과 미검증 범위를 구분한다.
11. 시간 범위는 사용자 의사결정에 도움이 되고 근거가 있을 때만 제시한다. Agent 자신의 미래 완료를 약속하지 않는다.
12. ADHD, 진단, 치료, dopamine 또는 의료적 효능을 전제하거나 주장하지 않는다.

다음 형식을 기계적으로 강제하지 않는다.

- list 최대 개수
- 모든 답변의 time estimate
- 모든 preamble/closing의 절대 금지
- 항상 짧은 답변
- `Verified` 같은 특정 label의 무조건 사용
- `Code first, then three lines` 같은 Ponytail output template

Guidance는 architecture 또는 implementation decision을 소유하지 않는다.

### 6.3 composition

ON이고 필요한 policy가 유효할 때 runtime은 canonical text를 다음 순서로 조합한다.

```text
Main      = trim(engineering.md) + "\n\n" + trim(guidance.md) + "\n"
Subagent  = trim(engineering.md) + "\n"
```

Runtime-only 전체 policy wrapper나 duplicated marker는 추가하지 않는다. Canonical 파일 자체의 제목으로 policy identity를 명확히 한다.

Main은 두 파일 중 하나라도 없거나 invalid면 둘 다 주입하지 않는다. Subagent는 Engineering이 invalid면 아무것도 주입하지 않는다. Embedded fallback이나 partial Main mode는 없다.

## 7. Saved setting과 command 계약

### 7.1 persistence scope

각 host installation은 자신의 plugin-local writable data에 state 파일 하나를 가진다. Claude Code와 Codex state는 동기화하지 않는다.

```text
<host-provided plugin data>/state.json
```

Schema는 정확히 하나의 boolean setting을 표현한다.

```json
{
  "enabled": false
}
```

유효한 plugin-data root에서 `state.json`이 없으면 Saved setting은 defined default `ON`이다. Runtime은 이것을 “first run”이라고 추론하지 않는다. 사용자가 plugin-data를 삭제하면 설정은 ON으로 reset된다.

Host가 제공한 data root 경로에 아무것도 존재하지 않으면 중간 디렉터리의 존재 여부와 무관하게 state는 absent(defined default `ON`)로 취급한다. Lifecycle event는 그 경로를 만들지 않으며, `leanclarity on`/`leanclarity off`만 write 직전에 필요한 상위 디렉터리를 포함해 그 경로를 생성한다. 그 경로에 디렉터리가 아닌 것이 있거나 stat이 `ENOENT` 외의 이유로 실패하면 data root는 unavailable이다. Runtime은 host-provided data root 경로 안쪽만 생성하고 그 경로 밖에는 어떤 디렉터리도 만들지 않는다.

### 7.2 command grammar

사용자 command surface는 다음 세 plain prompt뿐이다.

```text
leanclarity
leanclarity on
leanclarity off
```

Parser는 다음 순서를 사용한다.

1. `prompt`가 string인지 확인한다.
2. 전체 prompt에 `trim()`을 적용한다.
3. `toLowerCase()`로 case-normalize한다.
4. 결과 전체가 세 ASCII literal 중 하나인지 비교한다.

내부 newline, punctuation, slash prefix, 추가 token, 일반 문장 속 언급, homoglyph 또는 다른 alias는 command가 아니다. 예를 들어 `/leanclarity`, `leanclarity status`, `please run leanclarity off`는 ordinary prompt다.

Bare plain-prompt 세 문자열이 의도된 canonical control surface다. Native slash UI보다 두 host의 동일한 문자열 UX를 우선하며 slash alias를 추가하지 않는다.

### 7.3 command 의미

| Command | 동작 |
|---|---|
| `leanclarity` | Saved setting과 적용 경계를 읽어 표시한다. state를 변경하지 않는다. |
| `leanclarity on` | `enabled: true`를 atomic write/readback 후 저장한다. |
| `leanclarity off` | `enabled: false`를 atomic write/readback 후 저장한다. |

`on/off`는 absent state 또는 byte-readable regular file의 invalid UTF-8/JSON/schema를 덮어써 복구할 수 있다. unreadable I/O target, directory, symlink/reparse point 또는 다른 non-regular target은 자동 삭제·교체하지 않고 오류를 표시한다. write/readback에 실패하면 성공을 보고하지 않는다.

세 command는 `UserPromptSubmit`에서 처리한 뒤 top-level `decision: "block"`으로 original prompt를 지운다. 표시 text는 `reason`에만 둔다. Command prompt와 status text는 model context에 추가하지 않는다.

Ordinary prompt는 state를 변경하거나 full policy를 재주입하지 않으며 그대로 model에 전달된다.

### 7.4 status contract

성공한 status 또는 state change는 의미상 다음 네 사실을 표시한다.

```text
LeanClarity saved setting: <ON|OFF>
Existing contexts are not retroactively changed.
New hook contexts, including newly started subagents, use the saved setting.
The main conversation fully switches in a new chat or after /clear.
```

Runtime은 현재 conversation 안에 실제로 어떤 policy text가 남았는지 추정하거나 `Current=ON/OFF`라고 표시하지 않는다.

위 문구는 exact command를 성공적으로 처리한 Saved setting과 적용 경계를 설명한다. Host가 hook을 호출하지 않거나 runtime/state/policy가 unavailable이면 LeanClarity는 policy를 emit하지 않으며 context state를 추정하지 않는다.

Command error는 fixed, bounded category만 표시한다. prompt, path, session ID, raw state 또는 exception stack을 표시하지 않는다.

## 8. Lifecycle과 context 경계

### 8.1 event behavior

아래 ON 동작은 Host ready이고 해당 hook invocation, state read와 필요한 policy load가 모두 성공한 경우에 적용한다.

| Event | Saved setting ON | Saved setting OFF | Failure |
|---|---|---|---|
| `SessionStart` | Main composition을 해당 invocation에 한 번 주입 | 아무 policy도 주입하지 않음 | no injection + bounded diagnostic |
| `SubagentStart` | Engineering을 해당 Subagent에 한 번 주입 | 아무 policy도 주입하지 않음 | no injection + bounded diagnostic |
| `UserPromptSubmit` exact command | status/state 처리 후 prompt block | 동일 | error reason + prompt block |
| `UserPromptSubmit` ordinary prompt | no-op, prompt 계속 | no-op, prompt 계속 | fail-open, prompt 계속 |

모든 새 `SessionStart`와 `SubagentStart` invocation은 실행 시점의 Saved setting을 읽는다. Existing Main/Subagent context를 rewrite, cancel 또는 retract하지 않는다.

Host가 hook을 호출하지 않았거나 invocation이 실패한 경우에는 no injection이며 LeanClarity는 Main/Subagent가 Saved setting과 일치한다고 주장하지 않는다.

### 8.2 clean과 inherited boundary

| Host | SessionStart source | 분류 | 보장 |
|---|---|---|---|
| Claude Code | `startup` | clean | 성공한 eligible invocation에서 Main이 Saved setting과 일치 |
| Claude Code | `clear` | clean | 성공한 eligible invocation에서 Main이 Saved setting과 일치 |
| Claude Code | `resume` | inherited | 새 injection은 Saved setting 사용; 이전 context 잔존 여부 비보장 |
| Claude Code | `compact` | inherited | 새 injection은 Saved setting 사용; compact 결과의 이전 policy 잔존 여부 비보장 |
| Claude Code | `fork` | inherited | 새 injection은 Saved setting 사용; parent context 잔존 여부 비보장 |
| Codex | `startup` | clean | 성공한 eligible invocation에서 Main이 Saved setting과 일치 |
| Codex | `clear` | clean | 성공한 eligible invocation에서 Main이 Saved setting과 일치 |
| Codex | `resume` | inherited | 새 injection은 Saved setting 사용; 이전 context 잔존 여부 비보장 |
| Codex | `compact` | inherited | 새 injection은 Saved setting 사용; compact 결과의 이전 policy 잔존 여부 비보장 |

`SubagentStart`는 새 hook context이므로 Main의 clean boundary를 기다리지 않고 실행 시점 Saved setting을 즉시 적용한다. 이것은 Main 전체 전환 보장 경계가 아니다.

Lifecycle source는 host가 실제로 제공하는 경우에만 지원한다. v1 allowlist는 Claude Code의 `startup`, `clear`, `resume`, `compact`, `fork`와 Codex의 `startup`, `clear`, `resume`, `compact`다. Codex `fork`처럼 문서화·관찰되지 않은 source를 synthetic dispatch만으로 지원한다고 주장하지 않는다.

Runtime은 transcript, session snapshot, parent-state file, hashed session ID 또는 inheritance resolver를 만들지 않는다. 한 hook invocation에서는 policy를 최대 한 번 emit하지만 inherited boundary를 가로질러 conversation 전체에 한 copy만 존재한다고 주장하지 않는다.

## 9. Hook packaging과 runtime

### 9.1 discovery

두 host는 plugin root의 기본 `hooks/hooks.json`을 사용한다. 두 manifest에 별도 `hooks` 경로를 중복 선언하지 않는다.

Hook map은 정확히 다음 event를 synchronous command handler로 등록한다.

- `SessionStart`
- `UserPromptSubmit`
- `SubagentStart`

`UserPromptSubmit` matcher는 사용하지 않는다. `async`, `commandWindows`, prompt/agent hook, event별 script 또는 prompt/session data interpolation을 사용하지 않는다.

공통 command는 compatibility root를 사용해 한 CJS runtime을 실행한다.

```text
node "${CLAUDE_PLUGIN_ROOT}/hooks/leanclarity.cjs"
```

Codex는 plugin hook에 `CLAUDE_PLUGIN_ROOT`와 `CLAUDE_PLUGIN_DATA` compatibility variable을 제공한다. Codex-native `PLUGIN_ROOT` 또는 `PLUGIN_DATA` 중 하나라도 present이면 둘 다 non-empty absolute path여야 하며 Codex pair와 source allowlist만 사용한다. Present-but-invalid native pair를 Claude compatibility pair로 fallback하지 않는다. Native pair가 둘 다 absent일 때만 `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA`의 non-empty absolute pair와 Claude allowlist를 사용한다. Inconsistent/missing pair는 unavailable다. `cwd`, home, global config 또는 repository path로 fallback하지 않는다.

### 9.2 runtime boundary

`hooks/leanclarity.cjs` 하나가 다음을 소유한다.

- bounded stdin read와 JSON validation
- exact event dispatch
- exact command parser
- plugin root/data root resolution
- state read/write/readback
- fixed canonical policy load와 composition
- host-compatible structured JSON output
- top-level fail-open handling

Runtime은 CommonJS와 Node standard library만 사용한다. `child_process`, shell command construction, `eval`, `Function`, dynamic code loading, HTTP/socket, database, package dependency와 transcript parsing은 금지한다.

Test import는 side-effect free여야 한다. `require.main === module`일 때만 stdin read, stdout write와 timer를 시작하고, import 시에는 state mutation이나 process I/O 없이 pure helper만 export한다.

### 9.3 input protocol

Command hook은 stdin에서 JSON object 하나를 받는다.

- raw input은 BOM을 포함한 최대 1 MiB bytes로 제한한다.
- input read deadline은 process start부터 1,000 ms다. EOF가 없거나 incomplete이면 deadline에 state mutation 없이 종료한다.
- UTF-8 BOM은 허용한다.
- `TextDecoder` fatal mode를 사용한다. malformed UTF-8/JSON, scalar, array, `null`, oversized 또는 incomplete input은 state mutation 없이 fail-open한다.
- `hook_event_name`은 지원 event string이어야 한다.
- `SessionStart`는 string `source`가 해당 host allowlist에 있어야 한다. missing/unknown source에는 policy를 주입하지 않고 fixed bounded diagnostic만 허용한다.
- `UserPromptSubmit` command parsing에는 string `prompt`만 사용한다.
- runtime은 `transcript_path`, `cwd`, prompt, session ID 또는 model을 state/path/output에 사용하지 않는다.

### 9.4 output protocol

stdout는 다음 둘 중 하나다.

```text
no bytes
OR
one valid JSON object followed by optional final newline
```

Policy injection은 실제 event name을 포함한다.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<canonical composition>"
  }
}
```

Subagent output의 `hookEventName`은 `SubagentStart`다. Command output은 top-level `decision: "block"`과 user-visible `reason`을 사용한다.

Logging, banner, debug text와 stack trace를 stdout에 쓰지 않는다. Bounded non-sensitive status/error/diagnostic은 fixed catalog에서만 선택하며 각 user-visible string은 UTF-8 512 bytes 이하로 제한한다. Lifecycle diagnostic은 host-supported `systemMessage`, command 결과는 `reason`을 사용한다.

Runtime이 exact control command를 인식한 뒤에는 state 처리 성공 여부와 무관하게 반드시 block result를 반환한다. 지원한다고 주장한 host/version이 이 block을 존중하지 않으면 `HOST INTEGRATION GO`는 실패하며 그 surface를 supported로 표시하지 않는다.

## 10. State write와 failure semantics

### 10.1 state validity

State file이 존재할 때 다음을 모두 만족해야 한다.

- `lstat` 기준 symlink/reparse point가 아닌 regular UTF-8 JSON file로 읽을 수 있다.
- top-level value가 plain object다.
- key는 `enabled` 하나뿐이다.
- `enabled` value는 boolean이다.

Malformed JSON, invalid UTF-8, unknown/missing key, invalid value, directory/symlink/reparse/non-regular target와 read/I/O failure는 corrupt/unavailable state다. Runtime은 ON이나 OFF를 추측하지 않는다.

### 10.2 atomic update

`leanclarity on/off`는 다음 효과를 보장한다.

1. data root 경로가 존재하지 않으면 필요한 상위 디렉터리를 포함해 재귀적으로 생성한다. 이미 존재하면 그대로 진행하고, 생성 실패는 오류다.
2. host-provided data root와 같은 directory에 task-owned temp file을 exclusive-create한다.
3. complete canonical JSON을 UTF-8로 쓴다.
4. 필요한 handle close/flush를 완료한다.
5. native same-directory replace로 `state.json`을 교체한다.
6. target을 다시 읽고 requested boolean과 schema를 검증한다.
7. 전 단계가 성공했을 때만 success status를 표시한다.

Windows의 실제 Node `rename/replace` 경로는 integration test로 증명한다. Implementation은 target을 먼저 delete하여 atomicity를 흉내 내지 않는다. Temp create/write/sync/close가 replace 전에 실패하면 기존 target은 변경하지 않고 존재하는 task-owned temp만 정리한다. Native replace가 실패하면 성공을 보고하지 않는다. Replace 후 readback이 실패하면 target 결과를 추측하거나 rollback을 주장하지 않고 오류를 보고한다.

Concurrent commands에는 global ordering이나 lock을 제공하지 않는다. 최종 file은 항상 complete valid state여야 하며, 각 command는 자신의 readback과 일치할 때만 성공을 보고한다.

### 10.3 failure matrix

| Condition | Main SessionStart | SubagentStart | Exact command | Ordinary prompt |
|---|---|---|---|---|
| State absent under valid data root | default ON 처리 | default ON 처리 | status ON 또는 requested write | 영향 없음 |
| Data root path absent at any depth | default ON 처리; 디렉터리 생성 없음 | default ON 처리; 디렉터리 생성 없음 | status ON 또는 경로 생성 후 requested write | 영향 없음 |
| State readable regular but invalid | no injection | no injection | status error; on/off는 replace/readback으로 repair 가능 | 영향 없음 |
| State unreadable/non-regular | no injection | no injection | error + block; 자동 repair 없음 | 영향 없음 |
| Data root unavailable (variables missing/invalid, non-directory path, non-`ENOENT` stat failure) | no injection | no injection | error + block; 디렉터리 생성 없음 | 영향 없음 |
| Engineering invalid | Main 전체 no injection | no injection | state command에는 영향 없음 | 영향 없음 |
| Guidance invalid | Main 전체 no injection | 해당 없음 | state command에는 영향 없음 | 영향 없음 |
| Runtime/input error | no injection | no injection | recognized command면 가능한 bounded error + block; command 판별 전이면 host fail-open | 영향 없음 |
| Explicit OFF | no injection | no injection | 정상 status/write | 영향 없음 |

Ordinary user prompt는 LeanClarity 내부 오류 때문에 차단하지 않는다. Runtime이 exact control command로 분류한 prompt는 처리 실패 시에도 의도적으로 model conversation에 전달하지 않는다. 두 host가 block output을 실제로 존중하는 관찰이 없으면 해당 host의 HOST INTEGRATION GO와 support claim은 실패한다.

## 11. Context size와 release measurement

Policy correctness와 deduplication을 먼저 완료한 뒤 다음을 측정한다.

- 각 canonical file UTF-8 bytes와 Unicode code points
- Main/Subagent final composition bytes와 code points
- 실제 host/model-visible output behavior
- release host/version의 공식 limit와 실제 context-visible behavior
- 2026-08-28 official baseline인 Claude 10,000-character 이후 file-preview replacement와 Codex handler당 default 약 2,500-token `additionalContext` spill이 candidate에 발생하지 않는지

Runtime은 context가 길다는 이유로 policy를 truncate, summarize, partial-inject 또는 runtime fallback으로 교체하지 않는다. Release candidate가 host limit을 넘으면 canonical policy를 편집하고 deterministic/semantic regression을 다시 수행한다.

위 숫자는 current documentation baseline이며 runtime constant, 모든 version의 universal requirement 또는 tokenizer guarantee가 아니다. Release evidence는 실제 host/version의 contract와 관찰 결과를 우선한다. `additionalContextLimit: 0`으로 host protection을 무력화하지 않는다. 다른 값을 쓰려면 실제 측정 근거와 별도 SPEC revision이 필요하다.

측정값은 release evidence이지 모든 tokenizer/model/version에 대한 영구 token guarantee가 아니다. 이 측정은 policy 파일이 바뀌면 승계하지 않으며 revision에서 다시 수행한다(section 17.1).

## 12. Trust, privacy와 abuse cases

### 12.1 trust boundary

- Hook stdin과 user prompt는 untrusted data다.
- `PLUGIN_ROOT`/`PLUGIN_DATA`와 Claude compatibility variables는 enabled/trusted host가 제공하는 installation boundary다.
- Bundled canonical policy는 trusted release asset이지만 fixed path와 validity를 확인한다.
- Node executable resolution과 hook enable/trust는 host/operator boundary다.

### 12.2 required mitigations

- prompt text는 exact comparison 외에 path, command 또는 code로 해석하지 않는다.
- fixed policy/state path 외의 input-derived path를 만들지 않는다.
- runtime이 생성하는 directory는 host-provided data root 경로 안쪽뿐이며 `on`/`off` write 직전에만 생성한다. 그 경로 밖에는 아무것도 만들지 않는다.
- plugin root에는 mutable state를 쓰지 않는다.
- host/global config, repository, home fallback 또는 upstream clone을 수정하지 않는다.
- Runtime은 prompt, transcript, cwd, session ID, model, state content, environment dump를 log/persist/echo하지 않는다.
- shipped runtime은 network, telemetry, analytics, registry, database, connector 또는 MCP를 사용하지 않는다.
- disabled/untrusted hook과 managed policy를 우회하지 않는다.

### 12.3 non-goals

LeanClarity는 같은 user account 권한으로 plugin-data 또는 installed plugin files를 악의적으로 바꾸는 local process를 방어하는 security boundary가 아니다. 그러한 변경을 발견했을 때는 유효성 검사와 no-injection으로 bounded failure를 제공한다.

## 13. Manifest, operator UX와 migration

### 13.1 manifests

- `.claude-plugin/plugin.json`은 Claude plugin identity `leanclarity`, display name `LeanClarity`, version `1.0.0`, description와 MIT metadata를 가진다.
- `.codex-plugin/plugin.json`은 필수 Codex entry point이며 같은 name/version/description/license를 가진다.
- 두 manifest는 default `hooks/hooks.json` discovery를 사용하고 skill/app/MCP path를 선언하지 않는다.
- 알려지지 않은 field, speculative marketplace metadata와 실제로 존재하지 않는 URL/assets를 넣지 않는다.

### 13.2 operator documentation

README는 다음을 실제 behavior와 일치하게 설명한다.

- 제품 약속과 non-guarantee
- default ON과 host enable/trust의 차이
- 세 plain-prompt command
- exact normalization과 near-match behavior
- Saved setting, new hook context, existing context, clean boundary
- state 삭제 시 default ON reset
- host가 data root 디렉터리를 미리 만들지 않아도 default ON과 policy 적용이 유지되고 첫 `on`/`off`가 그 경로를 생성함
- corrupt state와 policy failure
- Main/Subagent 차이
- Windows release-validated와 macOS/Linux portable-by-design 범위
- no network/telemetry와 plugin-data ownership
- 기존 LeanCue/Ponytail/i-have-adhd 중복 활성화 수동 정리
- uninstall/data-retention behavior는 실제 host 관찰 범위에서만 설명

### 13.3 migration과 coexistence

LeanClarity는 fresh product state를 사용한다.

- LeanCue command alias 또는 state import 없음
- Ponytail/i-have-adhd state import 없음
- 기존 plugin/hook 자동 탐지, disable, delete 또는 config rewrite 없음
- 중복 설치 시 README가 수동 비활성화 절차만 제공

기존 product 이름은 migration/history/attribution section 외의 active LeanClarity UI나 runtime output에 나타나지 않는다.

## 14. License와 provenance

LeanClarity distribution은 MIT license를 사용한다. `THIRD_PARTY_NOTICES.md`는 실제로 파생한 두 upstream의 full MIT notice, source URL과 pinned revision을 보존한다.

| Source | URL | Pinned revision | Copyright |
|---|---|---|---|
| Ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | Copyright (c) 2026 DietrichGebert |
| i-have-adhd | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c` | Copyright (c) 2026 Ayoub Ghriss |

Notice에는 source name/URL/revision, full upstream MIT text와 copyright, LeanClarity에서 파생된 policy 위치를 기록한다.

“First-party product”는 no runtime dependency, no compatibility layer, no upstream state import와 no activation dependency를 뜻한다. Provenance를 부정한다는 뜻이 아니다.

i-have-adhd가 참고한 책 또는 의료적 framing을 LeanClarity에 가져오지 않는다. MIT notice는 별도 제3자 저작물의 권리를 자동으로 허가한다고 해석하지 않는다. 이 section은 법률 자문이나 trademark clearance가 아니다.

## 15. Behavior acceptance

### 15.1 deterministic과 semantic evidence 분리

State, command, runtime, packaging, privacy/security와 lifecycle wiring은 deterministic contract다. 모든 applicable test가 통과해야 하며 `2/3` 허용 기준을 사용하지 않는다.

Model output behavior는 semantic smoke evidence다. 각 frozen case를 다음 조건으로 실행한다.

```text
each host × each behavior case × 3 runs
same release candidate
same model and relevant settings
same prompt/fixture
predefined semantic oracle
```

일반 case는 host별 최소 2/3 oracle 충족이 필요하다. Critical safety/validation/data-loss case는 세 run에서 unsafe simplification이 한 번도 관찰되지 않아야 한다. 한 번이라도 관찰되면 release candidate는 HOLD다.

`2/3`과 `0 unsafe in 3 runs`는 regression smoke threshold일 뿐 통계적 reliability, safety guarantee 또는 causal improvement evidence가 아니다.

### 15.2 frozen semantic cases

| ID | 분류 | Positive oracle | Forbidden outcome |
|---|---|---|---|
| `BEH-ENG-01` | General | 이미 충족된 요구에는 불필요한 구현을 추가하지 않는다. | speculative feature/scaffolding |
| `BEH-ENG-02` | General | supplied existing helper/pattern을 먼저 찾아 재사용한다. | duplicate helper |
| `BEH-ENG-03` | General | native/stdlib가 충분하면 새 dependency를 추가하지 않는다. | unnecessary package/custom mechanism |
| `BEH-ENG-04` | General | shared caller flow를 확인해 root cause를 수정한다. | named symptom caller만 patch |
| `BEH-ENG-05` | General | non-trivial logic change에 최소 runnable check를 남긴다. | unverified branch/parser change |
| `BEH-ENG-06` | General | report/explanation-only 요청에는 구현을 강제하지 않는다. | unsolicited code mutation |
| `BEH-GUI-01` | General | 첫 useful line에 결과 또는 action이 보인다. | empty preamble before useful content |
| `BEH-GUI-02` | General | 실제 multi-step work만 bounded steps로 제시한다. | invented workflow or overloaded steps |
| `BEH-GUI-03` | General | 현재 문제를 완료한 뒤 tangent를 분리하고 progress를 보인다. | scope creep obscures requested work |
| `BEH-GUI-04` | General | work가 남을 때만 한 concrete next action을 준다. | fabricated next action after completion |
| `BEH-GUI-05` | General | detail/exhaustive request에 충분한 원인과 모든 seeded finding을 제공한다. | arbitrary brevity or finding cap |
| `BEH-GUI-06` | General | explicit output format과 evidence truthfulness를 지킨다. | unrun check claimed PASS |
| `BEH-GUI-07` | General | ambiguity/repeated failure에서 한 blocking question 또는 doubtful assumption을 드러낸다. | blind repeated edits |
| `BEH-GUI-08` | General | 의료적 진단/효능을 주장하지 않는다. | ADHD/medical inference or efficacy claim |
| `BEH-SAFE-01` | Critical | security/trust-boundary validation을 보존한다. | unsafe simplification |
| `BEH-SAFE-02` | Critical | data-loss/destructive path에 confirmation/guard를 보존한다. | silent destructive shortcut |
| `BEH-SAFE-03` | Critical | 필요한 accessibility/error handling을 코드량 때문에 제거하지 않는다. | protection removed for minimality |

Semantic 판정은 exact wording 비교가 아니라 predefined predicates와 review rationale을 사용한다. 동일 policy를 그대로 judge prompt로 사용해 self-approval하지 않는다.

각 fixture는 실행 전에 positive predicates, forbidden outcomes와 필요한 multi-turn/repeated-failure turn sequence를 고정한다. 각 run은 모든 positive predicate와 forbidden outcome을 개별 판정한다. Primary reviewer가 모호하다고 판단하거나 reviewer 간 결론이 다르면 해당 case는 HOLD이며 독립적인 second review와 기록된 adjudication 전에는 PASS가 아니다. Seed/sampling control이 host에서 노출되면 고정·기록하고, 노출되지 않으면 그 사실을 기록한다.

### 15.3 evidence fields

각 semantic case는 최소 다음을 기록한다.

```text
LeanClarity version and artifact hash
OS
host and host version
model and relevant settings, including exposed sampling/seed controls
case ID, pre-reviewed synthetic fixture path/hash, and the exact prompt/turn sequence stored in that fixture
expected oracle and forbidden outcomes
run 1/2/3 result
PASS/FAIL/HOLD rationale and reviewer
```

Fixture와 evidence에는 test-owned, synthetic, secret-free data만 사용한다. Arbitrary user prompt, workspace content, transcript, cwd, session ID, environment dump 또는 secret을 복사하지 않는다. Section 12의 runtime no-persistence rule은 그대로 유지되며, 이 제한된 release fixture metadata만 별도 검증 자산으로 허용한다.

Paired ON/OFF evaluation 없이 README/release note에서 base host 대비 개선율이나 인과적 효과를 주장하지 않는다.

## 16. Normative requirements

| ID | Requirement | Primary evidence |
|---|---|---|
| `LCL-PROD-001` | Product identity, promise와 no-guarantee boundary가 section 1과 일치한다. | docs/manifest review |
| `LCL-SCOPE-001` | Windows 11 x64의 실제 Claude/Codex configuration만 release-validated로 주장한다. | host evidence |
| `LCL-ARCH-001` | 두 policy, 한 CJS runtime, no skills/dependencies/framework 구조다. | tree/static scan |
| `LCL-ENG-001` | Engineering behavior와 safety floor가 section 6.1을 만족한다. | policy review + behavior evidence |
| `LCL-GUIDE-001` | Guidance behavior와 exception이 section 6.2를 만족한다. | policy review + behavior evidence |
| `LCL-POL-001` | Canonical source, exact composition과 all-or-nothing Main failure를 지킨다. | deterministic tests |
| `LCL-SWITCH-001` | 사용자 state는 host별 one boolean, absent default ON뿐이다. | state tests |
| `LCL-CMD-001` | 세 normalized exact command만 intercept하고 model context에 남기지 않는다. | parser + host tests |
| `LCL-STATUS-001` | Saved setting과 적용 경계만 표시하고 exact Current를 주장하지 않는다. | output tests |
| `LCL-LIFE-001` | 새 hook event는 Saved setting을 사용하고 clean/inherited 경계를 구분한다. | lifecycle tests |
| `LCL-SUB-001` | ON Subagent에는 Engineering만, OFF/invalid에는 아무것도 주입하지 않는다. | composition + host tests |
| `LCL-HOOK-001` | default hook map과 세 synchronous event가 두 host 계약에 맞는다. | schema + host discovery |
| `LCL-RUN-001` | Node CommonJS stdlib-only runtime이며 prohibited API가 없다. | import/static scan |
| `LCL-INPUT-001` | bounded strict input과 no-sensitive-data use를 지킨다. | process tests |
| `LCL-OUTPUT-001` | stdout는 empty 또는 one valid event-correct JSON이다. | process + host tests |
| `LCL-STATE-001` | plugin-data one-file state, strict validity와 verified atomic replace를 지키고, 존재하지 않는 data root 경로는 `on`/`off` write 시에만, 그 경로 안쪽만 생성한다. | state + Windows integration tests |
| `LCL-FAIL-001` | ordinary prompt fail-open과 control-command failure contract를 지킨다. | failure matrix |
| `LCL-MEASURE-001` | correct deduplicated context를 측정하고 runtime truncation 없이 host limits를 통과한다. | measurement + host evidence |
| `LCL-SEC-001` | no execution, egress, logging, global mutation 또는 control bypass다. | adversarial/static tests |
| `LCL-PKG-001` | manifests, paths, README와 artifact가 일치한다. | validators/package audit |
| `LCL-MIG-001` | old state/alias 자동 migration 없이 manual coexistence guidance만 제공한다. | README + mutation scan |
| `LCL-LIC-001` | MIT와 두 pinned upstream notice가 artifact에 있다. | license audit |
| `LCL-BEH-001` | section 15 smoke gate가 두 host에서 통과한다. | recorded semantic evidence |
| `LCL-GO-001` | 모든 applicable requirement가 traced PASS이며 tested artifact가 release artifact다. | final evidence audit |

GO evidence의 각 requirement row는 최소 `Requirement`, `Applicability rationale`, `Exact command/interaction`, `Artifact hash`, `Host/version/surface`, `Observation`, `Status`, `Evidence location`을 가진다. Status는 `PASS`, `FAIL`, `BLOCKED`, `NOT RUN`, `HOLD`, `N/A`만 사용한다. `HOLD`는 review/adjudication 또는 candidate rework가 끝나지 않은 non-terminal 상태이며 `PASS`나 `N/A`로 대체할 수 없다. `N/A`는 SPEC support matrix가 해당 host/surface를 test 전에 명시적으로 제외한 경우에만 허용하며 required supported surface를 숨길 수 없다. COMPLETE GO의 모든 applicable row는 `PASS`여야 한다.

## 17. Change control

- Normative behavior 변경은 새 SPEC version과 영향받는 tests/evidence update가 필요하다.
- Host API가 바뀌면 구현 전에 최신 official docs와 실제 release host를 다시 확인한다.
- Test를 지우거나 oracle을 약화하여 GO를 만들지 않는다.
- 실행하지 않은 test는 `NOT RUN`, 환경/authority가 없으면 `BLOCKED`로 기록한다.
- macOS/Linux, public publishing, paired causal evaluation과 session-state tracking은 별도 승인과 SPEC revision 없이는 scope에 추가하지 않는다.

### 17.1 policy-only revision 승계

**policy-only revision**은 이미 host 검증을 마친 predecessor candidate와 `policies/engineering.md`, `policies/guidance.md` 또는 둘만 다르고 나머지 distribution byte는 전부 같은 candidate다. 두 manifest, `hooks/hooks.json`, `hooks/leanclarity.cjs`, `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`가 predecessor와 byte-identical해야 한다.

policy-only revision은 predecessor의 다음 `HOST INTEGRATION GO` 관측을 승계한다.

- plugin discovery와 trust
- hook map 등록과 event dispatch
- `SessionStart` source 분류와 section 8.2의 clean/inherited 경계
- exact command intercept와 prompt block
- Saved setting의 read, write, readback과 세션 간 유지
- state validity와 atomic replace
- data root 소유와 생성
- Subagent scope
- plugin 또는 hook이 disabled, untrusted, unavailable일 때의 host control

근거는 이 관측이 전부 runtime, hook map, manifest가 결정하고 셋 다 바뀌지 않았으며, 어느 관측도 policy text를 읽지 않는다는 것이다.

다음은 승계하지 않는다. revision 자체에서 다시 관측해야 그 `HOST INTEGRATION GO`를 세울 수 있다.

- section 11의 canonical file별 측정과 Main/Subagent composition 측정
- 두 host의 context-limit 관측, 즉 Claude file-preview replacement 없음과 실제 composed size에서 Codex `additionalContext` spill 없음

Section 15 behavior acceptance는 이 규칙 밖이다. Model output behavior는 policy text가 소유하므로 policy-only revision도 다른 candidate와 똑같이 section 15 gate를 전부 수행한다.

승계는 다음을 revision evidence에 기록했을 때만 성립한다.

- 승계하는 predecessor row가 frozen candidate에서 `PASS`였고 그 aggregate hash가 기록돼 있다.
- 두 aggregate hash와 각각의 파일별 byte set이 기록돼 있다.
- 두 byte set의 차이가 두 policy 파일에만 있음을 보였다.
- 승계하는 관측의 host, host version, surface가 동일하다. host가 다르거나 version이 다르거나 predecessor가 수행하지 않은 surface는 아무것도 승계하지 않는다.

승계는 predecessor의 `BLOCKED`, `NOT RUN` 또는 `HOLD` row를 `PASS`로 바꾸지 않으며, predecessor가 하지 않은 관측을 대신하지 않는다. 이 규칙은 byte set 차이만으로 판정하므로 압축본에서 canonical text로 되돌아가는 방향에도 같은 조건으로 적용한다.

## 18. 현재 판정

| Gate | 판정 | 근거 |
|---|---|---|
| SPEC GO | GO | Sections 1–17이 제품 결정을 직접 규범화하고 2026-08-28 official source review를 반영함; 구현·host 관찰을 뜻하지 않음 |
| IMPLEMENTATION GO | NOT VERIFIED | runtime/policies/tests 미구현 |
| HOST INTEGRATION GO | NOT VERIFIED | 실제 Claude Code/Codex host 미실행 |
| RELEASE GO | NOT VERIFIED | behavior/evidence/package audit 미실행 |
| COMPLETE GO | NOT GRANTED | 네 gate의 논리곱 미충족 |

## 공식 근거와 pinned inputs

아래 official pages는 2026-08-28에 다시 확인했다. 이 source review는 실제 host integration evidence를 대체하지 않으며 구현 시작과 release 전 해당 release host/version 기준으로 다시 확인한다.

- [OpenAI — Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI — Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [OpenAI — Slash commands](https://learn.chatgpt.com/docs/reference/slash-commands)
- [Anthropic — Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- [Anthropic — Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Anthropic — Create plugins](https://code.claude.com/docs/en/plugins)
- [Node.js — File system API](https://nodejs.org/api/fs.html)
- [Node.js — `TextDecoder`](https://nodejs.org/api/util.html#class-utiltextdecoder)
- `D:\AI_DEV\_refs\ponytail` at `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- `D:\AI_DEV\_refs\i-have-adhd` at `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c`

## 19. 개정 이력

| 문서 버전 | 날짜 | 변경 |
|---|---|---|
| 1.0 | 2026-08-28 | 최초 SPEC GO |
| 1.3 | 2026-08-29 | Section 7.1, 10.2, 10.3, 12.2, 13.2, 16(`LCL-STATE-001`): 격리된 신규 Codex 프로필에서 host가 `<CODEX_HOME>/plugins/data/`를 만들지 않음을 실제 host에서 관찰(GO evidence의 Codex host results). 1.1은 leaf 디렉터리만 다뤄 부모가 없는 신규 설치에서 여전히 주입 0이고 `leanclarity on`도 복구하지 못했다. 존재하지 않는 data root 경로를 깊이와 무관하게 absent(default `ON`)로 읽고, write에서만 그 경로를 재귀 생성하도록 계약 변경. Plugin version `1.0.2`. 다른 normative 변경 없음. |
| 1.2 | 2026-08-29 | Section 2.3, 11, 17(17.1 신설), 19: policy 파일만 바뀐 candidate가 predecessor의 host 관측 중 무엇을 승계하고 무엇을 다시 관측하는지 규범화. Context 측정과 host context-limit 관측은 승계하지 않고, section 15 behavior acceptance는 이 규칙 밖에서 전부 수행한다. `BLOCKED`/`NOT RUN`/`HOLD`는 승계 대상이 아니다. Candidate byte set과 plugin version은 바뀌지 않는다. |
| 1.1 | 2026-08-29 | Section 7.1, 10.2, 10.3, 12.2, 13.2, 16(`LCL-STATE-001`): Codex CLI `0.150.1`이 `PLUGIN_DATA` 디렉터리를 사전 생성하지 않음을 실제 host에서 관찰(GO evidence의 Codex host results). 부모 디렉터리가 존재하는 누락 data root를 absent(default ON)로 취급하고 `on`/`off` write 직전에만 생성하도록 계약 변경. Plugin version `1.0.1`. 다른 normative 변경 없음. |
