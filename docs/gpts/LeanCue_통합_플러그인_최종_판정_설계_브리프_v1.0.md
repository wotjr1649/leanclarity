# LeanCue 통합 플러그인 최종 판정 및 설계 브리프 v1.0

**기준일:** 2026-08-28  
**대상 원본:** Ponytail v4.9.0 / i-have-adhd v0.2.0  
**1차 대상 호스트:** Claude Code, OpenAI Codex  
**목적:** 로컬 Codex가 두 upstream을 재검증한 뒤, 새로운 통합 플러그인을 과잉 설계 없이 구현·검증할 수 있도록 최종 설계 방향과 Freeze 승인조건을 고정한다.

---

## 1. 최종 판정

**GO.** Ponytail과 i-have-adhd를 하나의 플러그인 패키지로 통합하는 것은 타당하다.

단, 다음 두 원칙을 동시에 지킨다.

> 하나의 플러그인으로 통합하는 것은 권장한다.

> 두 SKILL.md를 하나의 거대한 SKILL.md로 합치는 것은 권장하지 않는다.

최종 권장 구조:

```text
LeanCue
├─ Build Policy
│  └─ Ponytail에서 파생
│     - YAGNI
│     - existing-code reuse
│     - stdlib/native first
│     - avoid unnecessary dependencies
│     - minimum correct diff
│     - root-cause fix
│
├─ Focus Policy
│  └─ i-have-adhd에서 파생
│     - action first
│     - bounded numbered steps
│     - tangent suppression
│     - state/progress visibility
│     - matter-of-fact errors
│     - concrete next action
│
└─ Shared Runtime
   ├─ SessionStart
   ├─ UserPromptSubmit
   ├─ SubagentStart
   ├─ config/state
   └─ instruction composition
```

즉 **1 Plugin + 2 Independent Policies + 1 Shared Runtime**이 최종 권장 구조다.

---

## 2. 원본 플러그인의 목적

### 2.1 Ponytail

Ponytail의 핵심 목적은 **AI coding agent의 과잉 엔지니어링 억제**다.

핵심 질문:

> 무엇을 만들어야 하며, 정말 이 정도 구현이 필요한가?

현재 핵심 의사결정 순서:

1. 기능 자체가 실제로 필요한가? — YAGNI
2. 이미 codebase에 존재하는가? — reuse
3. standard library가 해결하는가?
4. native platform 기능이 해결하는가?
5. 이미 설치된 dependency가 해결하는가?
6. 한 줄 또는 더 작은 구현으로 가능한가?
7. 그때만 최소한의 새 코드를 작성한다.

security, trust-boundary validation, data-loss prevention, accessibility 같은 필수 안전장치는 단순화를 이유로 제거하지 않는다.

**정의:** Ponytail은 주로 **Implementation Decision Policy**다.

주요 원본:
- `skills/ponytail/SKILL.md`
- `hooks/claude-codex-hooks.json`
- `hooks/ponytail-activate.js`
- `hooks/ponytail-subagent.js`
- `hooks/ponytail-mode-tracker.js`
- `hooks/ponytail-instructions.js`
- `hooks/ponytail-runtime.js`
- `hooks/ponytail-config.js`

### 2.2 i-have-adhd

i-have-adhd의 핵심 목적은 **AI 답변을 사용자가 즉시 실행하기 쉬운 형태로 재구성하는 것**이다.

핵심 질문:

> 그래서 사용자가 지금 무엇을 해야 하는가?

핵심 규칙:

- 다음 action을 먼저 제시
- 여러 단계는 번호 매기기
- tangent 억제
- 진행 상태를 눈에 보이게 표시
- 오류는 감정적 표현 없이 원인과 해결책을 직접 제시
- 불필요한 preamble / recap / closing 축소
- 남은 작업이 있으면 concrete next action 제시

**정의:** i-have-adhd는 주로 **Presentation / Interaction Policy**다.

주요 원본:
- `skills/i-have-adhd/SKILL.md`
- `hooks/hooks.json`
- `hooks/always-on.mjs`
- `.claude-plugin/plugin.json`
- `.codex-plugin/plugin.json`

---

## 3. 왜 통합이 과하지 않은가

두 플러그인은 핵심 책임은 다르지만 runtime에서는 같은 종류의 일을 상당 부분 반복한다.

```text
instruction source
→ lifecycle hook
→ host adapter
→ model context injection
```

별도 설치를 유지하면 다음이 중복될 수 있다.

- plugin manifest
- activation lifecycle
- config/state
- instruction loading
- host detection
- Claude/Codex output format adaptation
- context injection
- path/BOM/error handling

따라서 runtime을 하나로 합치고 policy만 분리하면 오히려 구조가 단순해질 수 있다.

---

## 4. 통합 시 금지할 것

### 4.1 하나의 거대한 SKILL.md

Implementation 정책과 Presentation 정책을 한 파일에 뒤섞지 않는다.

문제:
- 책임 경계 상실
- 이상 동작 원인 추적 어려움
- 한쪽만 비활성화하기 어려움
- mode 조합 폭발
- 중복되는 “짧게 답하라” 규칙 누적
- upstream 반영 시 diff 추적성 저하

### 4.2 Generic Policy Framework

v1에서 registry/factory/provider/middleware 형태의 범용 policy engine을 만들지 않는다.

현재 필요한 것은 Build와 Focus 두 축뿐이다.

**Ponytail의 YAGNI를 플러그인 자체에도 적용한다.**

---

## 5. 최종 네이밍

# LeanCue

- **Repository/plugin slug:** `leancue`
- **Display name:** `LeanCue`
- **Tagline:** `Minimal code. Clear next action.`

의미:
- **Lean** = 필요한 최소 구현, 불필요한 code/dependency/abstraction 제거
- **Cue** = 사용자가 지금 실행할 명확한 다음 action

장점:
- 짧고 발음이 쉬움
- 원본 이름에 종속되지 않음
- Build + Focus 두 책임을 동시에 암시
- Claude/Codex namespace로 쓰기 자연스러움

### 5.1 2026-08-28 충돌 조사

현재 확인:
- GitHub exact repository-name 검색에서 `leancue` 동일 저장소명은 확인되지 않음
- `leancue` exact npm package 또는 Claude/Codex plugin으로 식별되는 검색 결과는 확인되지 않음
- 유사 문자열 저장소는 있으나 exact-name 충돌은 아님

단, 이름 가용성은 변한다. 실제 repository/package 생성 직전에 다시 확인한다.

확인 대상:
1. GitHub exact repository name
2. npm exact package name
3. Claude Code plugin/marketplace name
4. Codex plugin name
5. 일반 웹 검색

### 5.2 제외 이름

이미 프로젝트·제품·패키지명이 확인되어 비추천:
- LeanFlow
- CodeCue
- SharpFocus
- LeanSignal
- LeanAction
- LeanPrompt
- CodeLean
- BuildCue
- CrispPath
- FocusDiff
- BuildFocus

2순위 후보: `MinimalCue`  
다만 일반 웹에서 같은 표현이 이미 사용되어 브랜드 독창성은 LeanCue보다 낮다.

**최종 추천: LeanCue**

---

## 6. v1 범위

### 포함
- Claude Code
- Codex
- Node.js hook runtime
- Build Policy
- Focus Policy
- 독립 on/off 및 build intensity
- SessionStart
- UserPromptSubmit
- SubagentStart
- config/state
- automated tests
- Windows/macOS/Linux 경로 안정성

### 제외
- Hermes adapter
- Python runtime
- OpenCode/Qoder/Gemini/Copilot/Pi adapter
- statusline
- web UI
- telemetry
- dashboard
- generic policy registry
- MCP server
- remote service
- network call
- database
- auto-update service

필요성이 증명되면 이후 phase로 추가한다.

---

## 7. 권장 파일 구조

```text
leancue/
├─ .claude-plugin/
│  └─ plugin.json
├─ .codex-plugin/
│  └─ plugin.json
├─ hooks/
│  ├─ hooks.json
│  ├─ activate.js
│  ├─ mode-tracker.js
│  ├─ subagent.js
│  ├─ instructions.js
│  ├─ config.js
│  └─ runtime.js
├─ skills/
│  ├─ leancue-build/
│  │  └─ SKILL.md
│  └─ leancue-focus/
│     └─ SKILL.md
├─ tests/
│  ├─ hooks.test.js
│  ├─ instructions.test.js
│  ├─ config.test.js
│  └─ windows-paths.test.js
├─ LICENSE
├─ THIRD_PARTY_NOTICES.md
└─ README.md
```

필요하지 않다면 파일 수를 더 줄여도 된다.

파일 구조 자체를 목표로 삼지 않는다. 최소하고 검증 가능한 구조를 선택한다.

---

## 8. Policy 책임 경계

### Build Policy 소유

Ponytail에서 다음을 가져온다.

- YAGNI
- existing implementation search/reuse
- stdlib first
- native platform first
- existing dependency before new dependency
- avoid unrequested abstraction
- avoid speculative scaffolding
- fewest files / minimum correct diff
- root-cause fix over symptom patch
- boring/correct over clever
- validation/security/data-loss handling 유지
- non-trivial logic에 최소 검증 남기기

**Build Policy는 사용자에게 어떻게 말할지 결정하지 않는다.**

### Focus Policy 소유

i-have-adhd에서 다음을 가져온다.

- answer/action first
- bounded numbered steps
- tangent suppression
- visible state/progress
- concrete errors: location → cause → fix
- unnecessary preamble 제거
- unnecessary recap/closing 제거
- concrete next action
- 긴 설명 요청 시 충분히 설명하되 구조화
- ambiguity/destructive action에서는 정확성·안전 우선

**Focus Policy는 architecture/dependency 선택을 결정하지 않는다.**

---

## 9. 중복 제거 규칙

Ponytail의 기존 Output 성격 규칙은 Build Policy에서 제거하거나 약화한다.

예:
- `Code first`
- `Then at most three short lines`
- `If the explanation is longer than the code...`

이유: 출력 형태는 Focus Policy 책임이다.

반대로 Focus Policy에는 다음을 넣지 않는다.
- stdlib 선택
- native feature 선택
- dependency 선택
- abstraction 금지
- minimum diff 판단

이유: 구현 형태는 Build Policy 책임이다.

---

## 10. i-have-adhd 정책 중립화

새 플러그인은 ADHD 진단을 전제로 하지 않는 편이 좋다.

기존 성격:
```text
The reader has ADHD.
```

권장:
```text
Optimize responses for low-friction execution:
make the next action obvious, reduce working-memory load,
suppress unrelated branches, and keep progress visible.
```

기능은 유지하되 의학적/임상적 효과를 주장하지 않는다.

---

## 11. Time Estimate 규칙 수정

원본의 “specific time estimates” 규칙은 그대로 복사하지 않는다.

권장 규칙:

> 사용자가 직접 실행할 단계의 예상 시간이 의사결정에 실제 도움이 될 때만 구체적인 시간 범위를 제공한다. Agent 자신이 현재 수행 중인 작업의 미래 완료 시간을 약속하지 않는다. Host/system instruction이 항상 우선한다.

---

## 12. 기본 Mode

권장:

```json
{
  "build": "full",
  "focus": "on"
}
```

LeanCue는 두 기능을 통합하는 plugin이므로 로컬/개인 v1에서는 둘 다 활성화하는 것을 기본으로 한다.

Public distribution에서 output-style 침범을 최소화하려면 `focus=off`를 별도 검토할 수 있다.

### Build
```text
off
lite
full
ultra
```

### Focus
```text
off
on
```

Focus에 별도 intensity를 추가하지 않는다.

---

## 13. 명령 구조

조합 mode를 만들지 않는다.

권장:

```text
/leancue
/leancue on
/leancue off

/leancue build off
/leancue build lite
/leancue build full
/leancue build ultra

/leancue focus on
/leancue focus off
```

`/leancue`는 상태만 보여준다.

```text
LeanCue: build=full, focus=on
```

---

## 14. Main Agent / Subagent

### Main Agent
```text
Build Policy + Focus Policy
```

### Subagent
```text
Build Policy only
```

Focus는 기본적으로 subagent에 넣지 않는다.

이유:
- 내부 worker에는 사용자-facing output 규칙의 가치가 낮음
- context 비용 절감
- 구현 결정에는 Build가 더 중요함

실측 후 필요성이 확인되면 option을 추가한다.

---

## 15. Hook Runtime

### SessionStart

대상:
```text
startup
resume
clear
compact
```

동작:
1. config/state 읽기
2. 활성 Build 읽기
3. 활성 Focus 읽기
4. frontmatter 제거
5. mode-specific filtering
6. 중복 없는 combined context 생성
7. host-native 형식으로 1회 출력

일반 turn마다 full ruleset을 다시 넣지 않는다.

### UserPromptSubmit

담당:
- `/leancue ...` 감지
- session state 변경
- 상태 보고

일반 prompt에서는 full policy를 재주입하지 않는다.

### SubagentStart

활성 Build Policy만 주입한다.

---

## 16. Claude / Codex Adapter

구현 전에 최신 공식 hook schema를 다시 확인한다.

### Claude
- SessionStart context output 형식 재검증
- SubagentStart `additionalContext` schema 재검증
- `CLAUDE_PLUGIN_ROOT`, `CLAUDE_CONFIG_DIR` 등 공식 env 재검증

### Codex
- manifest `hooks`, `skills` 재검증
- `PLUGIN_DATA` 기반 state 우선 검토
- `hookSpecificOutput.additionalContext` schema 재검증
- `systemMessage`와 model context를 구분

원본 Ponytail 코드를 무조건 복사하지 말고 현행 API와 대조한다.

---

## 17. Module System

runtime은 Node.js 하나만 사용한다.

CJS와 ESM을 섞지 않는다.

우선 검토:
> Ponytail의 현재 Claude/Codex runtime에서 검증된 CommonJS `.js`

최신 loader에서 ESM이 더 단순하다면 전부 `.mjs`로 통일해도 된다.

핵심은 하나의 module system을 일관되게 쓰는 것이다.

---

## 18. Python 판정

**v1 runtime에 Python은 필요 없다.**

Ponytail의 Python은 Hermes adapter/benchmark 계열이다.

Claude Code + Codex만 대상으로 하면 Node runtime으로 충분하다.

---

## 19. Context / Token 최적화

upstream 핵심 SKILL 원본 크기:

```text
Ponytail       6,637 bytes
i-have-adhd    6,813 bytes
-----------------------
raw total     13,450 bytes
```

단순 연결 금지.

통합 시:
- frontmatter 제거
- Ponytail presentation 규칙 제거
- i-have-adhd implementation 중복 제거
- persistence 설명 중복 제거
- host-specific 설명을 runtime으로 이동
- examples 최소화
- Build/Focus 책임 중복 제거

### Engineering target

```text
Main combined injected context:
<= 약 8,000 UTF-8 characters

Subagent Build-only context:
<= 약 5,000 UTF-8 characters
```

절대 숫자보다 중요한 조건:
> 두 upstream의 단순 합보다 의미적으로 작고, 중복이 없고, behavior regression이 없어야 한다.

실제 chars/tokens를 테스트에서 기록한다.

---

## 20. Config / State

개념:

```json
{
  "buildMode": "full",
  "focusMode": "on"
}
```

persistent defaults와 current session state를 분리한다.

Codex에서는 가능한 경우 plugin-local `PLUGIN_DATA`를 우선 검토한다.

credential 또는 unrelated global config는 수정하지 않는다.

---

## 21. Fail-Open / Security

productivity policy hook 오류가 host session을 멈추면 안 된다.

- invalid config → safe default
- missing SKILL → fallback 또는 no injection
- malformed stdin → exit 0
- missing EOF → bounded fallback
- stdout failure → no session failure
- mode/config allowlist
- no network access
- no dynamic remote code
- no `eval`
- shell invocation 최소화
- user prompt를 shell로 전달하지 않음
- path normalization / quoting 검증

---

## 22. License / Attribution

두 upstream은 MIT 라이선스다.

실제 코드/문구를 파생하면:
- 원본 copyright notice 유지
- MIT 조건 준수
- `THIRD_PARTY_NOTICES.md`에 upstream 명시
- Ponytail 파생 부분 명시
- i-have-adhd 파생 부분 명시

예:

```text
Ponytail
https://github.com/DietrichGebert/ponytail
MIT License

i-have-adhd
https://github.com/ayghri/i-have-adhd
MIT License
```

배포 전 실제 upstream LICENSE를 다시 확인한다.

---

## 23. v1에 가져오지 않을 Ponytail 기능

처음부터 이식하지 않는다.

- ponytail-review
- ponytail-audit
- ponytail-debt
- ponytail-gain
- statusline
- multi-host adapters
- OpenCode/Hermes/Pi
- MCP
- benchmark publication tooling

core Freeze 후 필요성을 별도 평가한다.

---

## 24. 검증 항목

### 기능

1. Claude 새 session에서 Build + Focus가 정확히 1회 활성화
2. Codex 새 thread에서 동일
3. resume/clear/compact 후 policy 유지
4. 일반 UserPromptSubmit에서 full ruleset 반복 주입 없음
5. build 명령은 Build만 변경
6. focus 명령은 Focus만 변경
7. off는 양쪽 비활성
8. Subagent에는 Build만 주입
9. Focus off에서도 Build 유지
10. Build off에서도 Focus 유지

### 안정성

- Windows path with spaces
- Unix path
- UTF-8 BOM
- malformed JSON stdin
- missing stdin EOF
- invalid mode
- missing/corrupted config
- missing SKILL
- stdout failure
- missing plugin root
- Codex `PLUGIN_DATA`
- Claude `CLAUDE_CONFIG_DIR`

### 중복

- Build/Focus 동일 규칙 중복 없음
- SessionStart와 skill auto-discovery 이중 주입 여부 검증
- global/project instruction과 불필요한 복제 여부 검증
- subagent에 Focus 유입 없음

---

## 25. Behavior Regression Test

### Case A — Over-engineering

```text
Add a date picker to this simple HTML form.
```

기대:
- 새 dependency 설치보다 native `<input type="date">` 우선 검토

### Case B — Existing reuse

```text
Add a helper for parsing this value.
```

동일 helper가 존재하면 새 helper보다 reuse.

### Case C — Action-first

```text
The test is failing. What should I do?
```

기대:
- 긴 preamble보다 첫 action/핵심 원인이 먼저
- 여러 단계면 bounded numbered steps

### Case D — Detailed explanation

```text
Explain in detail why this race condition occurs.
```

기대:
- 설명 자체를 삭제하지 않음
- 충분히 설명하되 headers/structure 사용

### Case E — Safety

validation/security/data-loss 문제에서 최소 코드라는 이유로 필수 guard를 제거하지 않음.

---

## 26. Freeze 승인조건

### Architecture
- [ ] One plugin / two policies
- [ ] Build/Focus 책임 분리
- [ ] generic framework 없음
- [ ] Node-only runtime
- [ ] Claude/Codex 외 host adapter 없음

### Runtime
- [ ] SessionStart green
- [ ] UserPromptSubmit green
- [ ] SubagentStart green
- [ ] Windows green
- [ ] Codex green
- [ ] Claude green
- [ ] malformed input fail-open

### Context
- [ ] full ruleset turn-by-turn 재주입 없음
- [ ] subagent Focus 미주입
- [ ] raw concatenation 아님
- [ ] 중복 rules 제거
- [ ] injected chars/tokens 측정 기록

### Behavior
- [ ] YAGNI/reuse/stdlib/native 보존
- [ ] action-first/tangent/progress 보존
- [ ] 상세 설명 요청 과축약 없음
- [ ] safety regression 없음

### Quality
- [ ] automated tests green
- [ ] no network dependency
- [ ] no runtime Python
- [ ] unnecessary package dependency 없음
- [ ] README와 구현 일치
- [ ] third-party notice/license 정리

---

## 27. Local Codex 구현 지침

Codex는 구현 전 두 upstream의 현재 main을 직접 재검증한다.

우선순위:

1. upstream source와 이 문서 사실관계 비교
2. Claude/Codex 최신 plugin/hook schema 확인
3. 현행 API에 설계가 유효한지 판정
4. 과함/누락이 있으면 근거와 수정안 제시
5. 최소 v1 구현
6. automated tests 작성
7. 실제 hook output 검증
8. injected context 크기/중복 측정
9. Freeze 승인조건 통과 시에만 Freeze 후보 판정

### 구현 원칙

> 두 repository를 통째로 합치지 마라.

> Ponytail runtime을 참고하되 Claude/Codex core만 가져와라.

> i-have-adhd에서는 presentation behavior만 추출하라.

> 하나의 거대한 prompt를 만들지 마라.

> 새 abstraction은 실제 중복이나 테스트 필요성이 증명될 때만 만든다.

> 통합 plugin 자체가 over-engineering 사례가 되지 않게 한다.

---

## 28. Codex가 구현 전에 답해야 할 질문

1. 현재 Codex와 Claude에서 SessionStart/UserPromptSubmit/SubagentStart 지원 차이는 무엇인가?
2. Codex `additionalContext` 현재 schema와 size behavior는 무엇인가?
3. Claude SessionStart stdout/SubagentStart JSON 형태는 현재도 동일한가?
4. skill auto-discovery와 hook injection이 같은 SKILL을 이중 주입할 수 있는가?
5. 두 SKILL을 `skills/`에 노출하면서 always-on hook source로도 쓰는 것이 최선인가, internal policy files가 더 안전한가?
6. config/state를 host별 어디에 저장해야 가장 native한가?
7. CommonJS/ESM 중 현재 두 host에서 더 단순하고 검증된 선택은 무엇인가?
8. 중복 제거 후 behavior regression 없이 context를 얼마나 줄일 수 있는가?
9. Subagent에 Build만 넣는 설계가 충분한가?
10. 구현 시점에도 `LeanCue` 이름이 GitHub/npm/plugin namespace에서 충돌하지 않는가?

---

# 최종 한 줄 판정

> **Ponytail과 i-have-adhd의 통합은 타당하다. 최적 구조는 `LeanCue`라는 하나의 Claude Code/Codex 플러그인 안에서 `Build Policy`와 `Focus Policy`를 독립적으로 유지하고 lifecycle/config/runtime만 공유하는 것이다. 하나의 거대한 SKILL 또는 범용 policy framework로 만드는 것은 과잉 설계이므로 피한다.**

---

## 참고 원본

### Ponytail
- https://github.com/DietrichGebert/ponytail
- https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md
- https://github.com/DietrichGebert/ponytail/blob/main/hooks/claude-codex-hooks.json
- https://github.com/DietrichGebert/ponytail/blob/main/hooks/ponytail-instructions.js
- https://github.com/DietrichGebert/ponytail/blob/main/hooks/ponytail-runtime.js
- https://github.com/DietrichGebert/ponytail/blob/main/docs/agent-portability.md

### i-have-adhd
- https://github.com/ayghri/i-have-adhd
- https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md
- https://github.com/ayghri/i-have-adhd/blob/main/hooks/hooks.json
- https://github.com/ayghri/i-have-adhd/blob/main/hooks/always-on.mjs
- https://github.com/ayghri/i-have-adhd/blob/main/.claude-plugin/plugin.json
- https://github.com/ayghri/i-have-adhd/blob/main/.codex-plugin/plugin.json
