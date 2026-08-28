# LeanCue v1.1 Normative Specification

> **Status: Superseded by [LeanClarity v1.0](LeanClarity_v1.0_SPEC.md).**  
> 이 문서는 이전 LeanCue 설계 계보의 판단 근거를 보존하는 historical record다. LeanClarity 구현 계약으로 사용하지 않는다.

## 0. 문서 상태

| 항목 | 상태 |
|---|---|
| 문서 종류 | Normative Specification |
| 문서 버전 | 1.1 |
| 설계 상태 | SPEC GO |
| 구현 상태 | NOT VERIFIED |
| Host 통합 상태 | NOT VERIFIED |
| Release 상태 | NOT VERIFIED |
| 최종 판정 | COMPLETE GO NOT GRANTED |

이 문서는 LeanCue v1의 구현 적합성을 판정하는 유일한 규범 문서다.
구현 순서와 검증 절차는 [LeanCue_v1.1_PLAN.md](../plans/LeanCue_v1.1_PLAN.md)가 소유한다.
기존 [v1.0 설계 브리프](../gpts/LeanCue_통합_플러그인_최종_판정_설계_브리프_v1.0.md)는 배경 자료이며 이 문서와 충돌할 때 규범적 효력이 없다.

이 문서에는 열린 설계 결정이 없다. 구현이나 host 검증에서 이 계약을 만족할 수 없는 항목이 발견되면 기능 또는 지원 범위를 줄이고 이 문서를 새 버전으로 변경한다. 문서화되지 않은 fallback, host 설정 변경, 추가 runtime 또는 외부 서비스를 도입하지 않는다.

---

## 1. COMPLETE GO 정의

LeanCue의 최종 판정은 다음 네 게이트의 논리곱이다.

```text
COMPLETE GO
= SPEC GO
+ IMPLEMENTATION GO
+ HOST INTEGRATION GO
+ RELEASE GO
```

### 1.1 SPEC GO

- 모든 제품 동작과 실패 의미가 이 문서에 고정되어 있다.
- 모든 규범 요구사항에 `LC-*` ID가 있다.
- 모든 `LC-*` 요구사항이 PLAN의 테스트와 증거에 연결되어 있다.
- 지원 host, OS, runtime과 제외 범위가 명시되어 있다.
- 현재 공식 문서가 필요한 API를 실제로 지원한다.

### 1.2 IMPLEMENTATION GO

- 구현이 모든 `LC-*` 요구사항을 만족한다.
- 결정론적 로컬 테스트가 전부 통과한다.
- runtime dependency가 Node 표준 라이브러리뿐이다.
- network, telemetry, database, registry 또는 plugin-root 상태 쓰기가 없다.

### 1.3 HOST INTEGRATION GO

- 지원 범위의 Claude Code와 Codex surface에서 실제 플러그인을 실행했다.
- lifecycle, trust, mode command, main/subagent 주입과 실패 동작을 관찰했다.
- 관찰한 host와 버전이 `docs/GO_EVIDENCE.md`에 기록되어 있다.

### 1.4 RELEASE GO

- manifest, README, license, attribution, migration 안내와 이름 재검색이 완료됐다.
- 요구사항 추적표에 실패 또는 미검증 행이 없다.
- 최종 배포물과 검증한 배포물이 동일하다.

어떤 게이트에도 `NOT VERIFIED`가 남아 있으면 `COMPLETE GO`를 선언하지 않는다.

---

## 2. 용어

| 용어 | 의미 |
|---|---|
| Build | 구현 선택을 단순화하는 정책 |
| Focus | 답변을 실행 가능하고 추적 가능하게 만드는 표현 정책 |
| Current | 현재 host session에 적용되는 mode |
| Defaults | 새로운 session이 시작할 때 복사하는 persistent mode |
| Main | root conversation의 모델 context |
| Subagent | `SubagentStart`로 시작되는 child agent context |
| Lifecycle Event | `SessionStart`의 startup, resume, clear, compact 또는 fork |
| Active | hook이 실행됐고 선택된 policy가 정상 주입된 상태 |
| Off | 사용자가 policy를 명시적으로 비활성화한 상태 |
| Unavailable Host | plugin 또는 hook이 disabled, untrusted 또는 managed-only 정책으로 실행되지 않는 상태 |
| Unavailable Runtime | Node, input, state 또는 policy 오류로 runtime 결과를 만들지 못한 상태 |
| Canonical Policy | `policies/build.md` 또는 `policies/focus.md`의 유일한 전문 |

Build와 Focus는 model-interpreted guidance다. security control, permission boundary, deterministic enforcement 또는 결과 보증이 아니다.

---

## 3. 지원 환경

### 3.1 v1 지원 범위

| 구분 | 지원 |
|---|---|
| OS | Windows 11 x64 |
| Claude | Claude Code CLI 2.1.214 이상 중 Release GO에서 실제 검증한 버전 |
| Codex | Codex desktop app 및 Codex CLI 중 Release GO에서 실제 검증한 버전 |
| Node | Node.js 22 LTS 또는 24 LTS |
| Runtime 위치 | local plugin process |
| State 위치 | host가 제공한 plugin data directory |

Release 문서는 `GO_EVIDENCE.md`에 기록된 정확한 host 버전보다 넓은 호환성을 주장하지 않는다.

### 3.2 v1 비지원 범위

- Codex IDE extension
- macOS, Linux, WSL
- Claude Code와 Codex 이외의 AI host
- 원격 실행 또는 cloud sync
- network 요청, telemetry, analytics
- database, registry, host 내부 SQLite 사용
- Python, shell script 또는 bundled Node fallback
- MCP, connector, app
- statusline 또는 별도 UI
- 자동 설치, 자동 제거, 자동 host 설정 변경
- public marketplace submission

다른 OS 또는 surface는 해당 환경의 결정론적 테스트와 실제 host 검증을 추가한 새 SPEC 버전에서만 지원한다.

---

## 4. 제품 범위와 불변식

LeanCue는 다음 네 요소로 구성된다.

1. 하나의 source distribution
2. 독립적인 Build와 Focus policy
3. 하나의 Node.js CommonJS runtime
4. Claude Code와 Codex용 manifest

다음 불변식은 모든 mode와 host에 적용된다.

- Build와 Focus는 독립적으로 켜고 끌 수 있다.
- Main은 활성 Build와 Focus를 받는다.
- Subagent는 활성 Build만 받으며 Focus를 받지 않는다.
- 정상 `UserPromptSubmit`은 전체 policy를 재주입하지 않는다.
- Canonical Policy 전문은 `skills/`에 노출하지 않는다.
- plugin root에는 mutable state를 쓰지 않는다.
- runtime은 prompt, cwd, session ID 또는 state 내용을 로그에 남기지 않는다.
- runtime은 host-wide 설정, trust 또는 hook enablement를 변경하지 않는다.
- runtime은 upstream repository를 읽거나 fetch하지 않는다.

---

## 5. Repository와 배포 구조

`LC-ARCH-001`에 따른 repository 구조는 다음과 같다.

```text
leancue/
├─ .claude-plugin/
│  └─ plugin.json
├─ .codex-plugin/
│  └─ plugin.json
├─ hooks/
│  ├─ hooks.json
│  └─ leancue.cjs
├─ policies/
│  ├─ build.md
│  └─ focus.md
├─ tests/
│  ├─ policy.test.cjs
│  ├─ runtime.test.cjs
│  ├─ state.test.cjs
│  └─ packaging.test.cjs
├─ docs/
│  └─ GO_EVIDENCE.md
├─ README.md
├─ LICENSE
└─ THIRD_PARTY_NOTICES.md
```

다음 파일과 기능은 v1 배포물에 포함하지 않는다.

- `package.json`
- `node_modules/`
- discoverable policy skill
- command skill
- host별 복제 runtime
- full-policy fallback 사본
- marketplace metadata
- benchmark harness
- installer 또는 uninstaller

테스트는 Node 내장 `node:test`와 `node:child_process`를 사용하며 runtime dependency가 아니다.

---

## 6. Policy 원본과 조합

### 6.1 Canonical source

- `policies/build.md`는 Build의 유일한 전문이다.
- `policies/focus.md`는 Focus의 유일한 전문이다.
- runtime source, README, manifest 또는 test fixture에 전문을 복제하지 않는다.
- policy 파일이 없거나 유효하지 않으면 해당 policy만 생략하고 다른 정상 policy는 계속 사용할 수 있다.
- runtime은 누락된 policy를 embedded text로 대체하지 않는다.

### 6.2 Build file format

`build.md`는 다음 sentinel block을 정확히 한 번씩 가진다.

```markdown
<!-- LEANCUE:BUILD:LITE:START -->
...
<!-- LEANCUE:BUILD:LITE:END -->

<!-- LEANCUE:BUILD:FULL:START -->
...
<!-- LEANCUE:BUILD:FULL:END -->

<!-- LEANCUE:BUILD:ULTRA:START -->
...
<!-- LEANCUE:BUILD:ULTRA:END -->
```

runtime은 sentinel 자체를 주입하지 않는다.

| Mode | 주입할 block |
|---|---|
| `off` | 없음 |
| `lite` | LITE |
| `full` | LITE + FULL |
| `ultra` | LITE + FULL + ULTRA |

sentinel이 없거나 중복되거나 순서가 잘못되면 Build policy 전체를 유효하지 않은 것으로 처리한다. 일부 block만 추정하여 주입하지 않는다.

### 6.3 Focus file format

`focus.md` 전체 body가 Focus policy다. `focus=off`이면 주입하지 않고 `focus=on`이면 전체를 한 번 주입한다.

### 6.4 Model-visible marker

생성된 context는 활성 policy 앞에 다음 marker를 정확히 한 번 포함한다.

```text
[LEANCUE_BUILD:<off|lite|full|ultra>]
[LEANCUE_FOCUS:on]
```

`off` policy marker는 model context에 넣지 않는다.

---

## 7. Build Policy 계약

Build는 code-changing task의 구현 판단에 강하게 적용되고, 설명·보고만 요청된 task에서는 구현을 강제하지 않는다.

### 7.1 Lite

- 먼저 이미 존재하는 코드와 pattern을 찾는다.
- Node 또는 언어 표준 라이브러리와 native platform 기능을 새 dependency보다 우선한다.
- 요구사항을 충족하는 가장 작은 올바른 변경을 선택한다.
- 요청되지 않은 확장 지점과 boilerplate를 만들지 않는다.

### 7.2 Full

Lite에 다음을 추가한다.

- symptom이 아니라 shared root cause를 수정한다.
- shared contract를 변경하기 전에 관련 caller를 확인한다.
- speculative abstraction, factory, interface와 config를 만들지 않는다.
- validation, data-loss protection, security, accessibility와 failure handling을 단순화 명목으로 제거하지 않는다.
- 비자명한 로직에는 가장 작은 실행 가능한 regression check를 남긴다.
- 기존 dependency가 해결하지 못하는 것이 확인된 경우에만 새 dependency를 검토한다.

### 7.3 Ultra

Full에 다음을 추가한다.

- 요청된 artifact 자체가 필요한지 먼저 검토한다.
- 같은 결과를 삭제, 표준 기능 또는 기존 코드로 얻을 수 있으면 추가 구현을 하지 않는다.
- 새 dependency 또는 abstraction에는 현재 요구사항으로 입증되는 이유를 요구한다.
- 동작과 안전을 보존하는 범위에서 추가보다 삭제를 우선한다.

Ultra도 validation, 보안, 접근성, 데이터 보호 또는 명시적 요구사항을 제거할 권한을 부여하지 않는다.

---

## 8. Focus Policy 계약

Focus는 모든 응답의 기본 표현 guidance다.

- 첫 유용한 줄은 결과 또는 실행 가능한 다음 행동이다.
- 여러 행동은 가장 짧은 번호 목록으로 쓰며 항목마다 하나의 bounded action을 둔다.
- 현재 요청을 먼저 끝내고 독립적인 두 번째 문제는 분리한다.
- 세 단계 이상이거나 여러 turn에 걸친 작업에서 현재 진행 상태를 다시 표시한다.
- 완료한 작업은 관찰 가능한 결과로 표시한다.
- 검증이 필요한 주장은 `Verified`, `Not verified`, `Blocked by`로 구분한다.
- 일이 남아 있을 때만 마지막에 하나의 다음 행동을 둔다.
- 시간 추정은 근거와 가정을 함께 제시할 수 있을 때만 한다.
- 일반적인 option과 recommendation은 우선순위를 제한하되 오류, 위험, 요구사항, 감사 finding과 검증 결과는 누락하거나 개수로 자르지 않는다.
- 불필요한 preamble, recap, closing pleasantry를 사용하지 않는다.

다음 요청은 brevity보다 우선한다.

- 상세 설명 또는 walkthrough
- exhaustive review, audit 또는 risk report
- 사용자가 지정한 출력 형식
- 파괴적 작업 전 확인
- 반복 실패 후 진단
- 실제 ambiguity 해소

Focus는 사용자의 의료 상태를 추론하거나 ADHD, dopamine, 진단 또는 치료 효과를 주장하지 않는다.

---

## 9. Policy precedence

Build와 Focus는 default behavioral guidance다.

- system, host, developer, workspace와 현재 user instruction의 실제 precedence를 따른다.
- 자신이 다른 instruction보다 우선한다고 주장하지 않는다.
- 사용자의 detail, exhaustive reporting 또는 특정 format 요청과 양립할 수 있으면 그 요청을 따른다.
- 안전 규칙, host guard, sandbox, permission 또는 approval을 우회하지 않는다.
- deterministic enforcement나 compliance guarantee로 표현하지 않는다.

---

## 10. Mode와 Defaults

### 10.1 유효값

```text
Build: off | lite | full | ultra
Focus: off | on
```

### 10.2 초기값

```text
defaults.build = full
defaults.focus = on
```

### 10.3 독립성

- Build 변경은 Focus를 변경하지 않는다.
- Focus 변경은 Build를 변경하지 않는다.
- `on` alias만 두 mode를 `full/on`으로 설정한다.
- `off` alias만 두 mode를 `off/off`으로 설정한다.
- Defaults 변경은 이미 materialize된 Current session을 변경하지 않는다.
- 새로운 session은 그 시점의 Defaults를 Current snapshot으로 복사한다.

---

## 11. Canonical command grammar

명령은 slash command나 skill invocation이 아니라 단독 user prompt다.

```text
leancue
leancue on
leancue off
leancue build off
leancue build lite
leancue build full
leancue build ultra
leancue focus off
leancue focus on
leancue defaults
leancue defaults on
leancue defaults off
leancue defaults build off
leancue defaults build lite
leancue defaults build full
leancue defaults build ultra
leancue defaults focus off
leancue defaults focus on
```

### 11.1 Parsing

- 입력 앞뒤 Unicode whitespace를 제거한다.
- ASCII `leancue`와 mode token은 대소문자를 구분하지 않는다.
- 명령은 한 줄 전체가 위 grammar와 일치할 때만 유효하다.
- trailing punctuation, 추가 설명 또는 여러 줄 입력은 명령이 아니다.
- 두 번째 token이 `on`, `off`, `build`, `focus` 또는 `defaults`이지만 전체 grammar가 유효하지 않으면 reserved invalid command다.
- 그 밖의 LeanCue 언급은 정상 user prompt로 통과한다.

### 11.2 의미

| 명령 | 상태 변경 | 표시 |
|---|---|---|
| `leancue` | 없음 | Current와 Defaults |
| `leancue on` | Current = full/on | 변경된 Current와 Defaults |
| `leancue off` | Current = off/off | 변경된 Current와 Defaults |
| `leancue build X` | Current Build만 X | 변경된 Current와 Defaults |
| `leancue focus X` | Current Focus만 X | 변경된 Current와 Defaults |
| `leancue defaults` | 없음 | Defaults |
| `leancue defaults on` | Defaults = full/on | Current와 변경된 Defaults |
| `leancue defaults off` | Defaults = off/off | Current와 변경된 Defaults |
| `leancue defaults build X` | Defaults Build만 X | Current와 변경된 Defaults |
| `leancue defaults focus X` | Defaults Focus만 X | Current와 변경된 Defaults |
| reserved invalid command | 없음 | 한 줄 usage |

### 11.3 처리 순서

인식된 command는 다음 순서를 지킨다.

1. input과 session scope를 검증한다.
2. 필요한 state를 atomic replace로 저장한다.
3. 저장된 state를 다시 읽어 결과를 확인한다.
4. `decision: "block"`과 200자 이하의 `reason`을 출력한다.
5. command prompt를 model task로 전달하지 않는다.

state write 또는 검증이 실패하면 성공했다고 표시하지 않는다. command는 model에 전달하지 않고 짧은 실패 reason으로 block한다.

정상 user prompt에서는 `UserPromptSubmit`이 state를 변경하거나 policy 전문을 출력하지 않는다.

---

## 12. Lifecycle과 agent scope

### 12.1 Event matrix

| Event | Main output | State |
|---|---|---|
| Claude `startup` | 활성 Build + Focus | session snapshot 생성 또는 기존 snapshot |
| Claude `resume` | 활성 Build + Focus | 같은 session ID snapshot |
| Claude `clear` | 활성 Build + Focus | 같은 ID면 유지, 새 ID면 Defaults snapshot |
| Claude `compact` | 활성 Build + Focus | 같은 session ID snapshot |
| Claude `fork` | 활성 Build + Focus | 같은 ID면 유지, 새 ID면 Defaults snapshot |
| Codex `startup` | 활성 Build + Focus | session snapshot 생성 또는 기존 snapshot |
| Codex `resume` | 활성 Build + Focus | 같은 session ID snapshot |
| Codex `clear` | 활성 Build + Focus | 같은 ID면 유지, 새 ID면 Defaults snapshot |
| Codex `compact` | 활성 Build + Focus | 같은 session ID snapshot |
| `SubagentStart` | 활성 Build만 | parent session state |

`SessionStart` 주입은 session당 한 번이 아니라 lifecycle event당 한 번이다.

### 12.2 Subagent

- `SubagentStart` output은 Build만 포함한다.
- Focus marker와 Focus 전문을 포함하지 않는다.
- Codex가 parent session ID를 제공하면 parent Current를 사용한다.
- session state를 확인할 수 없으면 Defaults를 임의로 materialize하지 않고 context를 생략한다.
- mode 변경은 이후 생성되는 subagent에만 적용한다.
- 이미 실행 중인 subagent의 context를 소급 변경한다고 주장하지 않는다.
- `SubagentStart` 실패로 subagent 생성을 block하려 하지 않는다.

Main/Subagent 분리는 injection scope이며 capability 또는 security boundary가 아니다.

---

## 13. Hook discovery와 invocation

두 host는 plugin root의 `hooks/hooks.json` 기본 discovery를 사용한다. 두 manifest에는 `hooks` 경로를 선언하지 않는다.

`hooks/hooks.json`의 규범 형태는 다음과 같다.

```json
{
  "description": "LeanCue lifecycle hooks",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "^(startup|resume|clear|compact|fork)$",
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/leancue.cjs\"",
            "timeout": 5
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/leancue.cjs\"",
            "timeout": 5
          }
        ]
      }
    ],
    "SubagentStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/leancue.cjs\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

규칙:

- `UserPromptSubmit`에는 matcher를 넣지 않는다.
- `SubagentStart`는 matcher를 생략하여 모든 subagent type에 적용한다.
- `commandWindows`를 넣지 않는다.
- prompt, cwd, session ID 또는 event 값을 command 문자열에 삽입하지 않는다.
- `async`를 사용하지 않는다.
- 두 manifest가 같은 default hook file을 중복 선언하지 않는다.

Codex는 plugin hook에 `CLAUDE_PLUGIN_ROOT`와 `CLAUDE_PLUGIN_DATA` compatibility variable을 제공한다.

---

## 14. Runtime module과 허용 API

`hooks/leancue.cjs`는 CommonJS 단일 entrypoint다.

runtime에서 허용하는 Node module:

- `node:fs`
- `node:path`
- `node:crypto`
- `node:process`

테스트에서만 추가로 허용:

- `node:test`
- `node:assert/strict`
- `node:child_process`
- `node:os`

runtime은 다음을 사용하지 않는다.

- third-party package
- dynamic import
- `eval` 또는 `Function`
- child process
- shell invocation
- network API
- environment 전체 dump
- transcript 파일 parsing

plugin root는 `PLUGIN_ROOT`가 있으면 우선 사용하고 없으면 `CLAUDE_PLUGIN_ROOT`를 사용한다.
state root는 `PLUGIN_DATA`가 있으면 우선 사용하고 없으면 `CLAUDE_PLUGIN_DATA`를 사용한다.

---

## 15. Hook input protocol

runtime은 stdin에서 하나의 JSON object를 읽는다.

| 항목 | 제한 |
|---|---|
| 전체 stdin | 최대 1 MiB |
| read deadline | process 시작 후 최대 1초 |
| root JSON | non-null object |
| `hook_event_name` | 정확한 지원 event string |
| `session_id` | 1–512 Unicode code points의 string |
| `prompt` | `UserPromptSubmit`에서만 string |
| `source` | `SessionStart`에서 지원하는 source |
| `agent_id` / `agent_type` | `SubagentStart`에서 host가 제공한 bounded string |

규칙:

- UTF-8 BOM은 제거한 뒤 parsing한다.
- 빈 stdin, malformed JSON, scalar, array와 null은 fail-open input error다.
- 1 MiB를 초과하면 더 읽거나 parsing하지 않는다.
- EOF가 도착하지 않아도 deadline 후 종료한다.
- prompt, cwd, transcript path와 session ID 원문을 persist하거나 echo하지 않는다.
- transcript format을 API로 사용하지 않는다.

---

## 16. Hook output protocol

### 16.1 Context output

Main과 Subagent context는 다음 공통 structured output을 사용한다.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "..."
  }
}
```

`hookEventName`은 실제 event와 정확히 같아야 한다.

### 16.2 Command output

```json
{
  "decision": "block",
  "reason": "LeanCue: current build=full focus=on; defaults build=full focus=on."
}
```

### 16.3 Diagnostic output

runtime이 structured output을 만들 수 있는 오류는 model context 대신 다음 공통 field로 알린다.

```json
{
  "systemMessage": "LeanCue unavailable: state error."
}
```

허용하는 diagnostic category는 `input error`, `state error`, `storage error`, `policy error`와 `context limit`이다. 다른 내부 예외도 가장 가까운 category 하나로 일반화한다. diagnostic은 200자 이하이며 prompt, path, session ID, state content, stack trace 또는 secret을 포함하지 않는다.

정상인 다른 policy를 함께 주입할 수 있으면 `systemMessage`와 `hookSpecificOutput`을 같은 JSON object에 넣는다. `systemMessage`는 user-visible host status이며 model guidance로 사용하지 않는다. hook 자체가 실행되지 않는 Unavailable Host와 Node 미설치는 runtime이 diagnostic할 수 없으므로 host hook UI가 소유한다.

### 16.4 일반 규칙

- stdout은 비어 있거나 정확히 하나의 valid JSON object다.
- stdout에 log, banner, debug text 또는 JSON 앞뒤 문자를 넣지 않는다.
- 정상 처리와 fail-open runtime error는 exit code 0이다.
- `decision:block`은 인식된 mode/status command에만 사용한다.
- `SessionStart`와 `SubagentStart`를 block하려 하지 않는다.
- stderr 진단은 200자 이하이며 prompt, path, session ID, state value 또는 secret을 포함하지 않는다.
- stdout flush 전에 무조건 `process.exit()`를 호출하지 않는다.

---

## 17. State

### 17.1 위치

```text
<plugin-data>/v1/defaults.json
<plugin-data>/v1/sessions/<sha256(session_id)>.json
```

session ID 원문은 파일명과 file body에 쓰지 않는다.

### 17.2 Schema

```json
{
  "schema": 1,
  "build": "full",
  "focus": "on"
}
```

object는 위 세 field만 가진다. unknown field, 잘못된 schema 또는 invalid mode가 있으면 corrupt state다.

### 17.3 Defaults와 Current

- `defaults.json`이 처음부터 없으면 compiled scalar defaults `full/on`을 사용한다.
- 새 valid session ID를 처음 보면 현재 Defaults snapshot을 session file로 materialize한다.
- materialize된 session은 이후 Defaults 변경의 영향을 받지 않는다.
- 같은 session ID의 resume, clear, compact는 같은 snapshot을 사용한다.
- 새 session ID는 그 시점의 Defaults를 snapshot으로 사용한다.
- session ID가 없거나 유효하지 않으면 state를 persist하지 않고 policy context를 생략한다.

### 17.4 Atomic replace

state write는 다음 순서를 따른다.

1. target directory를 plugin-data 아래에 생성한다.
2. 같은 directory에 unique temporary file을 생성한다.
3. 완전한 JSON과 끝 newline을 쓴다.
4. file을 닫는다.
5. target으로 rename한다.
6. target을 다시 읽고 schema와 intended state를 검증한다.
7. 실패 시 temporary file만 제거하고 기존 target은 보존한다.

같은 session에 대한 동시 command는 last successful commit wins다. 서로 다른 command를 merge한다고 보장하지 않는다. state가 깨지지 않는 것은 보장한다. 실제 multi-client lost update가 관찰되면 새 SPEC에서 per-session lock을 추가한다.

### 17.5 Bounded retention

- session state는 최대 64개다.
- successful session state 생성 또는 갱신 후에만 prune한다.
- `sessions/` 바로 아래의 `^[0-9a-f]{64}\.json$` 파일만 대상이다.
- 64개를 초과하면 mtime이 가장 오래된 LeanCue-owned session file부터 제거한다.
- `defaults.json`, 다른 directory 또는 pattern이 다른 파일은 제거하지 않는다.
- prune 실패는 current write 성공을 되돌리지 않으며 bounded diagnostic만 남긴다.

### 17.6 Durability boundary

Current와 Defaults의 persistence는 host가 같은 plugin-data directory를 제공하는 동안에만 보장한다. plugin uninstall/reinstall, host migration, account 변경 또는 Codex cache replacement 뒤의 state 보존을 주장하지 않는다. LeanCue는 host 내부 database 또는 다른 global path에 복사본을 만들지 않는다.

---

## 18. Failure semantics

| 상태 | Model context | User-visible 상태 | 일반 prompt |
|---|---|---|---|
| Active | 선택된 policy | 필요할 때만 | 계속 |
| Off | 해당 policy 없음 | status command에서 표시 | 계속 |
| Unavailable Host | 없음 | host의 plugin/hook UI | 계속 |
| Missing one policy | 정상인 다른 policy만 | 한 줄 diagnostic | 계속 |
| Missing both policies | 없음 | 한 줄 diagnostic | 계속 |
| Invalid/corrupt state | 없음 | 한 줄 diagnostic | 계속 |
| Missing/unwritable data root | 없음 | 한 줄 diagnostic | 계속 |
| Invalid/oversized input | 없음 | 한 줄 diagnostic 또는 host hook error | 계속 |
| Timeout/no EOF | 없음 | host timeout 또는 한 줄 diagnostic | 계속 |
| Missing Node | 없음 | host hook failure | 계속 |

runtime error는 ordinary user prompt를 block하지 않는다.

인식된 LeanCue command에서 state read/write가 실패하면 command만 block하고 성공을 주장하지 않는다. 이 block은 잘못된 command를 일반 model task로 보내지 않기 위한 command protocol의 일부다.

full policy fallback은 없다. 명시적 Off와 Unavailable을 같은 상태로 표현하지 않는다.

---

## 19. Context budget

### 19.1 Hard limit

| Context | Unicode code points | UTF-8 bytes |
|---|---:|---:|
| Main Build + Focus | 8,000 이하 | 8,000 이하 |
| Subagent Build | 5,000 이하 | 5,000 이하 |

### 19.2 Authoring target

| Context | UTF-8 target |
|---|---:|
| Main Build + Focus | 7,000 bytes 이하 |
| Subagent Build | 4,000 bytes 이하 |

### 19.3 초과 동작

- runtime은 policy를 중간에서 truncate하지 않는다.
- 하나의 policy를 추가했을 때 hard limit을 넘으면 그 policy 전체를 생략하고 diagnostic을 출력한다.
- Build와 Focus가 모두 활성이고 Focus 추가가 limit을 넘으면 Build는 유지하고 Focus를 생략한다.
- Build 자체가 limit을 넘으면 Build를 생략한다.
- marker와 wrapper를 포함한 최종 string을 측정한다.
- UTF-8 bytes 또는 code points를 token 수로 부르지 않는다.
- Release GO에서는 Codex spill과 Claude large-output spill이 실제로 발생하지 않았음을 확인한다.

---

## 20. Trust boundary와 abuse case

| 경계 | Abuse case | Mitigation |
|---|---|---|
| Hook stdin | 매우 큰 prompt로 memory 사용 증가 | 1 MiB cap과 1초 deadline |
| Prompt text | shell metacharacter command injection | prompt를 shell/child process에 전달하지 않음 |
| Session ID | path traversal | SHA-256 filename, 원문 미저장 |
| cwd/transcript path | 외부 파일 읽기 | runtime에서 사용하지 않음 |
| State file | corrupt JSON으로 mode 변경 | strict schema, atomic replace, no silent fallback |
| Policy file | plugin root 밖 path 접근 | fixed path만 사용 |
| stdout | log가 model context 또는 JSON을 오염 | zero-or-one JSON contract |
| Multiple hooks | policy 중복 주입 | unique marker와 host `/hooks` 검증 |
| Existing plugins | Ponytail/ADHD policy 중복 | README migration 안내, 자동 삭제 금지 |
| Host trust/config | hook을 강제로 활성화 | host control 존중, 자동 설정 변경 금지 |

LeanCue는 prompt, state 또는 local path를 network, connector, MCP, telemetry 또는 다른 recipient에게 전송하지 않는다.

---

## 21. Manifest와 packaging

### 21.1 Claude manifest

`.claude-plugin/plugin.json`은 최소한 다음 값을 가진다.

```json
{
  "name": "leancue",
  "version": "0.1.0",
  "description": "Independent Build and Focus guidance for Claude Code and Codex.",
  "author": {
    "name": "LeanCue contributors"
  }
}
```

### 21.2 Codex manifest

`.codex-plugin/plugin.json`은 최소한 다음 값을 가진다.

```json
{
  "name": "leancue",
  "version": "0.1.0",
  "description": "Independent Build and Focus guidance for Claude Code and Codex.",
  "author": {
    "name": "LeanCue contributors"
  },
  "license": "MIT"
}
```

### 21.3 공통 packaging 규칙

- 두 manifest의 name, version과 description은 일치한다.
- manifest에 `hooks` field를 넣지 않는다.
- 존재하지 않는 `skills/` path를 선언하지 않는다.
- plugin root 밖 path를 참조하지 않는다.
- archive와 marketplace 파일은 public distribution이 별도 승인될 때까지 만들지 않는다.
- Codex에서 plugin enabled와 hook trusted는 별도 activation 단계로 문서화한다.
- Codex IDE extension 지원을 주장하지 않는다.

---

## 22. Migration

README는 다음을 명시한다.

1. 기존 Ponytail 또는 i-have-adhd always-on plugin/hook이 활성인지 `/hooks` 또는 host plugin UI에서 확인한다.
2. 중복 정책을 피하려면 기존 always-on source를 사용자가 직접 disable 또는 uninstall한다.
3. LeanCue는 다른 plugin, user config, project config 또는 managed config를 자동 변경하지 않는다.
4. Codex에서는 plugin enable 후 현재 hook definition을 별도로 review/trust한다.
5. Node 22 또는 24가 non-interactive hook PATH에 있어야 한다.
6. `leancue` status command로 Current와 Defaults를 확인한다.

LeanCue가 upstream state를 import하거나 삭제하지 않는다.

---

## 23. License와 attribution

LeanCue 배포물은 MIT License를 사용하며 `LICENSE`의 copyright holder는 다음과 같다.

```text
Copyright (c) 2026 LeanCue contributors
```

`THIRD_PARTY_NOTICES.md`는 다음 source revision과 MIT notice를 포함한다.

| Source | Revision | Notice |
|---|---|---|
| Ponytail | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | Copyright (c) 2026 DietrichGebert |
| i-have-adhd | `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c` | Copyright (c) 2026 Ayoub Ghriss |

runtime은 upstream repository 또는 mutable `main`을 참조하지 않는다.

Release GO 직전에 GitHub, npm, 공개 Claude plugin catalog와 공개 Codex marketplace에서 exact `leancue` 이름을 다시 검색한다. 이 검색은 상표권 clearance를 의미하지 않는다.

---

## 24. Behavior acceptance

Behavior 평가는 exact prose가 아니라 semantic oracle을 사용한다.

| Case | 기대되는 의미 |
|---|---|
| Native first | 새 dependency 전에 native 또는 stdlib 선택을 검토 |
| Existing reuse | fixture의 기존 helper 또는 pattern을 재사용 |
| Root cause | 한 caller의 symptom 대신 shared cause를 찾음 |
| Action first | 첫 유용한 줄이 결과 또는 실행 행동 |
| Detailed explanation | 상세 설명 요청에서 충분한 causal explanation |
| Exhaustive findings | finding을 임의 개수로 자르지 않음 |
| Safety | validation/security/data-loss protection을 유지 |
| Build off / Focus on | Focus만 관찰되고 Build marker 없음 |
| Build full / Focus off | Build만 관찰되고 Focus marker 없음 |
| Build ultra / Focus on | 두 policy가 함께 작동하고 안전 예외 유지 |

각 host에서 동일한 model/version을 기록하고 case당 세 번 실행한다.

- Safety case는 3/3 통과한다.
- 나머지 case는 각각 최소 2/3 통과한다.
- 비활성 policy marker 또는 명백한 orthogonality failure는 0건이어야 한다.
- model/version 변경 결과를 이전 결과와 혼합하지 않는다.

---

## 25. Normative requirements

| ID | 요구사항 | Acceptance |
|---|---|---|
| `LC-SCOPE-001` | 지원 host, OS, Node와 제외 범위를 지킨다. | 배포물·README·증거의 support matrix 일치 |
| `LC-ARCH-001` | 하나의 distribution, 두 private policies, 하나의 runtime을 사용한다. | packaging tree와 import scan |
| `LC-POL-001` | Canonical Policy 전문은 각 파일 하나뿐이다. | 중복 전문 및 discoverable policy skill 0건 |
| `LC-MODE-001` | Build 4 mode와 Focus 2 mode가 독립적이다. | 8개 조합 전체 통과 |
| `LC-CMD-001` | exact command grammar와 block/status 의미를 지킨다. | command transition 및 두 host UX 통과 |
| `LC-HOOK-001` | 세 event를 default hook file 하나로 처리한다. | hook schema와 host registration 통과 |
| `LC-LIFE-001` | Claude 5 source와 Codex 4 source를 처리한다. | synthetic 및 실제 lifecycle 통과 |
| `LC-SUB-001` | Main은 Build+Focus, Subagent는 Build만 받는다. | marker와 실제 subagent 증거 |
| `LC-RUN-001` | Node 22/24 표준 라이브러리와 단일 `.cjs` runtime만 사용한다. | import scan 및 Node version matrix |
| `LC-STATE-001` | state는 plugin-data의 hashed session file에 atomic하게 저장된다. | isolation, atomic, prune와 corrupt-state tests |
| `LC-FAIL-001` | ordinary prompt에서 모든 runtime error가 fail-open이다. | child-process failure matrix |
| `LC-SEC-001` | input을 bound하고 prompt/session/path를 노출하거나 실행하지 않는다. | oversized/no-EOF/path/log assertions |
| `LC-CTX-001` | Main/Subagent context hard limit과 no-spill을 만족한다. | byte/code-point tests와 host evidence |
| `LC-PKG-001` | 두 manifest와 default discovery가 host contract와 일치한다. | Claude strict validation과 Codex install |
| `LC-MIG-001` | 기존 plugin 충돌을 문서화하고 자동 변경하지 않는다. | README 및 filesystem/config mutation scan |
| `LC-LIC-001` | MIT license와 pinned upstream notices를 보존한다. | file-content test |
| `LC-BEH-001` | Build/Focus behavior와 독립성을 semantic oracle로 확인한다. | host별 반복 eval 기준 통과 |
| `LC-GO-001` | 모든 gate의 관찰 증거가 있어야 COMPLETE GO다. | `GO_EVIDENCE.md`에 실패·미검증 행 0개 |

---

## 26. Change control

- 규범 동작을 변경하는 구현 편의는 SPEC 변경 없이 허용하지 않는다.
- host 공식 문서가 바뀌면 먼저 `LC-HOOK-001`, `LC-LIFE-001`, `LC-PKG-001`을 재검토한다.
- 새로운 host, OS, command alias, skill, dependency 또는 remote capability는 새 SPEC 버전이 필요하다.
- 테스트가 host contract와 충돌하면 테스트를 통과시키기 위해 validation 또는 failure handling을 약화하지 않는다.
- host가 계약을 지원하지 않으면 그 surface의 지원을 제거하거나 별도 adapter를 명시적으로 설계한다.
- 구현에서 발견한 측정값과 실행 로그는 SPEC에 누적하지 않고 `GO_EVIDENCE.md`에 둔다.

---

## 27. 현재 판정

`SPEC GO`는 이 문서로 정의된다.

구현, 실제 host integration과 release evidence가 아직 없으므로 현재 판정은 다음과 같다.

```text
SPEC GO
IMPLEMENTATION NOT VERIFIED
HOST INTEGRATION NOT VERIFIED
RELEASE NOT VERIFIED
COMPLETE GO NOT GRANTED
```

---

## 공식 근거

- [Claude Code Hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code Plugins](https://code.claude.com/docs/en/plugins)
- [OpenAI Docs: Codex Hooks](https://developers.openai.com/codex/hooks)
- [OpenAI Docs: Build Plugins](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Docs: Codex Plugins](https://developers.openai.com/codex/plugins)
- [Node.js Releases](https://nodejs.org/en/about/previous-releases)
- [Node.js Packages](https://nodejs.org/api/packages.html)
- [Node.js File System](https://nodejs.org/api/fs.html)
