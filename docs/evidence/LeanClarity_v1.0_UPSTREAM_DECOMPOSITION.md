# Upstream 지침 분해 — ponytail · i-have-adhd → LeanClarity

SPEC section 14는 provenance를 **라이선스 수준**으로만 기록한다 — URL, pinned revision, copyright,
그리고 "파생된 policy 위치". **어느 상위 규칙이 어느 bullet이 됐고 무엇이 버려졌는지는 어디에도
기록돼 있지 않다.** 이 문서가 그 분해다.

게이트 증거가 아니다. 어떤 GO도 부여하거나 막지 않는다. SPEC 재설계의 입력이고, 견고성 연구가
대역으로 쓸 지침이 무엇을 이미 의무화하는지를 확정한다.

| 소스 | 경로 | pinned revision | bytes |
|---|---|---|---:|
| ponytail | `skills/ponytail/SKILL.md` | `2ed6c52c9d7e5e56942508591085fd45dea277d3` | 6,757 |
| i-have-adhd | `skills/i-have-adhd/SKILL.md` | `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c` | 6,953 |
| LeanClarity | `policies/engineering.md` + `policies/guidance.md` | candidate `99B19A9C…` | 2,485 (조합 2,486) |

`AGENTS.md`가 아니라 `SKILL.md`가 정본이다. `i-have-adhd/AGENTS.md`(5,166 bytes)에는 행동 규칙이
하나도 없다 — 그 repo 기여자용 지도이고, 문서 스스로 *"It does not replace the skill rules in
`skills/i-have-adhd/SKILL.md`"*라고 적는다. `ponytail/AGENTS.md`(2,625)는 축약된 행동 정책이지만
정본은 `SKILL.md`다.

---

## 1. ponytail 규범 단위 → LeanClarity

| # | ponytail 단위 | 처리 | 착지점 |
|---|---|---|---|
| P1 | 페르소나 — "lazy senior developer", 3am 호출 | **버림** | 없음. SPEC은 행동만 규범화하고 인격을 주입하지 않는다 |
| P2 | Persistence — "ACTIVE EVERY RESPONSE", `stop ponytail`로만 해제 | **기제로 대체** | 텍스트가 아니라 런타임. 매 `SessionStart` 주입 + saved state ON/OFF |
| P3 | 사다리 rung 1 — YAGNI, 존재할 필요가 있는가 | 채택 | Engineering 3 |
| P4 | 사다리 rung 2–5 — 기존 코드 → stdlib → 네이티브 → 설치된 의존성 | 채택 | Engineering 4 |
| P5 | 사다리 rung 6 — "Can it be one line?" | **버림** | 없음. SPEC 6.1.3의 사슬에 이 단계가 없다 |
| P6 | 사다리 rung 7 — 최소 구현 | 채택 | Engineering 4 (사슬 끝) |
| P7 | 사다리 규율 — 오르기 **전에** 이해하고 실제 흐름을 끝까지 추적 | 채택 | Engineering 1 |
| P8 | 버그 수정 = 근본 원인. 호출자를 grep하고 공유 함수에 가드 하나 | 채택 | Engineering 1(호출자 확인) + 6(근본 원인) |
| P9 | 요청되지 않은 추상화 금지 — 구현 1개짜리 인터페이스, 제품 1개짜리 팩토리, 상수용 config | 채택 | Engineering 5 |
| P10 | 보일러플레이트·"나중을 위한" 스캐폴딩 금지 | 채택 | Engineering 3 |
| P11 | 추가보다 삭제. 영리함보다 지루함 | **버림** | 없음 |
| P12 | 파일 최소. 가장 짧은 diff — 단 이해한 뒤에만 | 채택(분할) | Engineering 5(file split) + 6(shortest가 아니라 smallest correct) |
| P13 | 복잡한 요청 → 게으른 판을 내면서 같은 응답에서 되묻는다 | **버림** | 없음. Guidance에도 없다 |
| P14 | 같은 크기의 stdlib 두 개 → 엣지 케이스에 옳은 쪽 | **버림** | 없음 |
| P15 | `ponytail:` 주석으로 천장과 승급 경로 표기 | **버림** | 없음. 특정 마커 강제는 SPEC 6.2의 비강제 목록과 같은 성격 |
| P16 | 출력 형식 — 코드 먼저, 최대 3줄, `[code] → skipped: [X], add when [Y]` | **명시적 버림** | SPEC 6.2가 "`Code first, then three lines` 같은 Ponytail output template"을 기계적 강제 금지 목록에 넣었다 |
| P17 | 강도 레벨 lite/full/ultra + `/ponytail` 명령 | **기제로 대체** | 단일 ON/OFF. SPEC 7의 세 bare prompt |
| P18 | 게을러지면 안 되는 것 — 신뢰 경계 검증, 데이터 손실 방지 오류 처리, 보안, 접근성 기본 | 채택 | Engineering 7 |
| P19 | …**"anything explicitly requested"** | **버림** | 없음. SPEC 6.1.7이 안전 명사만 나열하고 사용자 권한 조항을 옮기지 않았다 |
| P20 | 사용자가 완전판을 고집하면 만든다, 재논쟁 없이 | **버림** | 없음 |
| P21 | 이해에 대해서는 절대 게으르지 않는다 (P7의 확장) | 채택 | Engineering 1 |
| P22 | 하드웨어 보정 — 시계가 흐르고 센서가 어긋난다, 보정 손잡이를 남겨라 | **명시적 버림** | SPEC 6.1이 "Hardware calibration 같은 domain-specific upstream 규칙은 v1 core invariant가 아니다"라고 적는다 |
| P23 | 비자명 로직은 실행 가능한 검사 하나를 남긴다 | 채택 | **Engineering 8** |
| P24 | Boundaries — "무엇을 만드는지를 지배하지 어떻게 말하는지가 아니다", Caveman과 조합 | **버림** | 없음 — 5절 참조. 이것이 우선순위 조항이다 |

**24개 단위: 채택 11 · 버림 11 · 기제로 대체 2.**

## 2. i-have-adhd 규범 단위 → LeanClarity

| # | i-have-adhd 단위 | 처리 | 착지점 |
|---|---|---|---|
| A0 | 전제 — "The reader has ADHD" + 다섯 가지 사실(작업기억, 앎≠함, 시작이 어려움, 시간감각, 도파민) | **명시적 버림** | SPEC 6.2.12가 "ADHD, 진단, 치료, dopamine 또는 의료적 효능을 전제하거나 주장하지 않는다"로 금지. 동사가 "**전제하거나**"인 것이 핵심 — upstream의 ADHD 내용은 주장이 아니라 정확히 전제다 |
| A1 | 다음 행동을 먼저 | 채택 | Guidance 1 |
| A2 | 다단계 작업은 번호로, 최소 단계 | 채택(조건화) | Guidance 2 — "**genuinely** multi-step work만" |
| A3 | 열린 게 있으면 2분 내 구체적 next action 하나로 끝낸다 | 채택 + **부정 추가** | Guidance 5 — "…**do not invent one after completion**" |
| A4 | 탈선 억제 — 첫 번째를 끝내고 두 번째는 분리 | 채택 | Guidance 3 |
| A5 | 매 turn 상태 재진술 | 채택(완화) | Guidance 4 — "every turn"이 "**as needed**"로 |
| A6 | 항상 구체적 시간 추정 | 채택(대폭 축소) | Guidance 10 — "**의사결정에 도움이 되고 근거가 있을 때만**". SPEC 6.2가 "모든 답변의 time estimate"를 비강제 목록에 넣었다 |
| A7 | 완료된 작업을 보이게 | 흡수 | Guidance 4 |
| A8 | 오류에 담담한 어조 — "Uh oh" 금지 | **버림** | 어조 규칙은 옮기지 않았다. Guidance 7은 다른 것(검증 정직성)을 말한다 |
| A9 | **목록은 5개로 제한** | **명시적 부정** | Guidance 6이 "without an arbitrary brevity or **list limit**"으로 뒤집는다. SPEC 6.2 비강제 목록의 "list 최대 개수" |
| A10 | preamble·recap·맺음 인사 금지 + 금지 문구 목록 | 채택(정신만) | Guidance 1. 금지 문구 블랙리스트는 버림 — SPEC 6.2 "모든 preamble/closing의 절대 금지" 비강제 |
| A11 | 예외 1 — "설명해줘"면 충분히 설명 | 채택 | Guidance 6 |
| A12 | 예외 2 — 파괴적 행위 전 확인 | 채택 | Guidance 8 |
| A13 | 예외 3 — 디버그 나선. 세 turn 막히면 의심 가정을 대고 진단 질문 하나 | 채택 | **Guidance 9** |
| A14 | 예외 4 — 진짜 모호함이면 짧은 질문 하나 | 채택 | Guidance 8 |
| A15 | 예외 5 — 규칙이 과제와 싸우면 과제가 이긴다 | **버림** | 없음 |
| A16 | 예외 6 — **규칙이 하네스와 싸우면 시스템 프롬프트가 이 스킬을 이긴다** | **버림** | 없음 — 5절 참조 |
| A17 | 발송 전 점검 5항 (첫 문장·마지막 문장·사이드바·헤지 부사·관용구 삭제) | **버림** | 없음. 기계적 형식 강제라 SPEC 6.2 비강제 목록의 성격 |

**18개 단위: 채택 12 · 버림 5 · 명시적 부정 1.**

## 3. 역방향 — LeanClarity 18 bullet의 출처

| bullet | 출처 | SPEC | fixture |
|---|---|---|---|
| E1 이해·호출자·공유 계약 | P7 · P8 · P21 | 6.1.1 | **없음** |
| E2 분석·설명·보고·review만 요청하면 코드를 고치지 않는다 | **원본 없음 — LeanClarity 신규** | 6.1.9 | `BEH-ENG-06` |
| E3 불필요한 기능·스캐폴딩 생략 | P3 · P10 | 6.1.2 | `BEH-ENG-01` |
| E4 기존 코드 → stdlib → 네이티브 → 설치된 의존성 → 최소 구현 | P4 · P6 | 6.1.3 | `BEH-ENG-02` · `BEH-ENG-03` |
| E5 1회용 추상화·미래용 config·wrapper·factory·file split 금지 | P9 · P12 | 6.1.4 | **없음** |
| E6 가장 작은 공통 근본 원인. shortest가 아니라 smallest correct | P8 · P12 | 6.1.5 · 6.1.6 | `BEH-ENG-04` |
| E7 신뢰 경계·보안·정확성 가드·데이터 손실·접근성·오류 처리 보존 | P18 | 6.1.7 | `BEH-SAFE-01/02/03` |
| E8 비자명 변경에 최소 실행 가능 검사 | **P23** | 6.1.8 | `BEH-ENG-05` |
| G1 유용한 결과·결론·행동을 먼저 | A1 · A10 | 6.2.1 | `BEH-GUI-01` |
| G2 진짜 다단계만 번호 단계로 | A2 | 6.2.2 | `BEH-GUI-02` |
| G3 현재 요청을 끝낸 뒤 탈선 분리 | A4 | 6.2.3 | `BEH-GUI-03` |
| G4 turn 간 단계·완료·검증·남은 실패를 보이게 | A5 · A7 | 6.2.4 | **없음** |
| G5 남은 일이 있을 때만 next action 하나 | A3 + 부정 | 6.2.5 | `BEH-GUI-04` |
| G6 명시 형식 존중. 상세 요청에 brevity/list cap 없이 | A9 부정 · A11 | 6.2.6 · 6.2.7 | `BEH-GUI-05` |
| G7 관찰된 검사와 미실행 검사를 구분, 돌리지 않은 것을 통과라 하지 않는다 | **원본 없음 — LeanClarity 신규** | 6.2.10 | `BEH-GUI-06` |
| G8 파괴적 효과 전 확인. 진짜 blocking 모호성에만 질문 하나 | A12 · A14 | 6.2.8 | **없음** |
| G9 같은 이유로 반복 실패하면 의심 가정을 대고 진단 근거 요구 | A13 | 6.2.9 | `BEH-GUI-07` |
| G10 시간 범위는 의사결정에 도움될 때만. 미래 완료를 약속하지 않는다 | A6 축소 | 6.2.11 | **없음** |
| — | — | 6.2.12 (상속 제약) | `BEH-GUI-08` (앵커 없음) |

## 4. 커버리지 공백

**18 bullet 중 5개가 시험되지 않는다** — `E1`, `E5`, `G4`, `G8`, `G10`. 그리고 `BEH-GUI-08`은
대응 bullet이 없다.

`E1`의 부재가 특히 눈에 띈다. 그것은 사다리 전체의 전제(P7·P21, "이해가 먼저")이고 Engineering의
첫 bullet인데, `BEH-ENG-04`가 근본 원인 수정을 시험할 뿐 "고치기 전에 흐름을 추적했는가"는 아무도
채점하지 않는다.

`G8`도 마찬가지다. 파괴적 효과 전 확인은 `BEH-SAFE-02`가 **Engineering 7 쪽에서** 시험하고,
Guidance 8이 말하는 "사용자에게 확인을 구한다"는 시험되지 않는다.

## 5. 충돌 — 재설계가 다뤄야 할 것

### C1 **우선순위 조항이 텍스트에서 사라졌다** (가장 중요)

두 upstream은 **모델에게** 자기 순위를 말한다.

- ponytail P24: *"Ponytail governs what you build, not how you talk."*
- i-have-adhd A16: *"Inside an agent harness, the system prompt outranks this skill."*

SPEC 42행은 같은 것을 규범화한다 — *"Host의 system/developer/workspace/user instruction hierarchy와
실제 safety control은 LeanClarity보다 우선한다."*

**그런데 `policies/*.md`에는 우선순위·충돌·override에 대한 문장이 한 줄도 없다.** SPEC은 알고
모델은 모른다. 주입되는 2,486자는 자기가 사용자의 `CLAUDE.md`·`AGENTS.md`·호스트 시스템 프롬프트와
어떤 관계인지 말하지 않는다.

이것이 "사람마다 전역 지침이 달라도 일정하게 동작한다"가 지금 성립할 수 없는 구조적 이유다.
두 상위 모두 그 조항을 갖고 있었고 통합 과정에서만 사라졌다.

SPEC 6.3이 "runtime-only wrapper나 duplicated marker를 추가하지 않는다"고 못박았으므로, 복원한다면
런타임이 아니라 **정본 policy 텍스트**여야 하고 그것은 SPEC 6.1/6.2 개정이다.

### C2 두 상위의 출력 규칙이 서로 반대다

ponytail P16은 산문을 최소화한다(코드 먼저, 최대 3줄, 설명이 코드보다 길면 삭제).
i-have-adhd A2·A5·A6·A7은 산문을 **늘린다**(번호 단계, 매 turn 상태 재진술, 시간 추정, 성과 가시화).

LeanClarity의 해결: **ponytail의 출력 템플릿을 통째로 버리고, adhd의 구조를 조건부로 채택**
(`genuinely multi-step`, `as needed`, `도움이 될 때만`). SPEC 6.2의 비강제 목록이 그 판정을 기록한다.
adhd의 형태가 이겼고 ponytail의 상한이 졌다.

### C3 i-have-adhd가 자기모순이고 LeanClarity가 편을 들었다

A9(목록 5개 제한)와 A11(설명 요청이면 충분히)은 양립하지 않는다. LeanClarity는 **A9를 부정**했다
(G6: *"without an arbitrary brevity or list limit"*). 상위 규칙을 뒤집은 유일한 지점이다.

### C4 A3에 부정을 덧붙인 것이 시험에서 실패한다

A3는 이미 조건부다 — "**If anything is left open**, name ONE thing". LeanClarity G5는 여기에
금지를 덧댔다 — *"do not invent one after completion."*

**`BEH-GUI-04`가 정확히 그 덧댄 부정을 시험하고, 양 호스트에서 6/6 실패한다.** 개정 한 번이
소진됐고(10.1) 반증됐다. 상위에 없던 조항을 추가한 것이 통하지 않는다는 직접 증거다.

### C5 사용자 권한 조항이 안전 조항에서 떨어져 나갔다

ponytail P18과 P19는 한 문장이다 — *"Never simplify away: input validation…, security measures,
accessibility basics, **anything explicitly requested**."* LeanClarity E7은 안전 명사만 가져오고
"명시적으로 요청된 것"을 남겼다. P20("사용자가 고집하면 만든다")도 어디에도 없다.

결과적으로 **사용자가 명시적으로 요청한 것을 단순화로 지우지 않는다는 보호가 정본 텍스트에 없다.**

### C6 상위가 이미 스스로 해소한 긴장은 같은 방식으로 해소됐다

- P23(검사를 남겨라) vs P3(YAGNI) → ponytail이 "trivial one-liners need no test"로 자기 제한.
  LeanClarity E8도 "non-trivial change"로 같은 게이트.
- P12(가장 짧은 diff) vs 정확성 → ponytail이 "이해한 뒤에만"으로 자기 제한. LeanClarity E6이
  "shortest-looking이 아니라 smallest correct"로 명문화. **상위보다 명확해진 유일한 지점.**

### C7 신규 조항 둘의 출처가 없다

`E2`(review-only 요청에 코드를 고치지 않는다)와 `G7`(돌리지 않은 검사를 통과라 하지 않는다)은
어느 상위에도 대응이 없다. 둘 다 SPEC 6.1.9 / 6.2.10으로 규범화돼 있으므로 의도된 추가다.

시험 결과가 갈린다: `G7`(`BEH-GUI-06`)은 양 호스트 통과. `E2`(`BEH-ENG-06`)는 Claude에서 실패했고,
그 실패는 이후 **계측 결함으로 재분류**됐다 — P2가 이 행이 아니라 `BEH-GUI-05`의 행을 잰다.

## 6. 통합이 실제로 한 일

| | ponytail | i-have-adhd | LeanClarity |
|---|---:|---:|---:|
| 텍스트 | 6,757 | 6,953 | **2,486** |
| 규범 단위 | 24 | 18 | **18 bullet** |
| 지속 방식 | 산문 선언 | 산문 선언 + `/i-have-adhd` | **런타임 훅 주입** |
| 모드 | lite/full/ultra | 없음 | **ON/OFF 하나** |
| 우선순위 조항 | 있음 (P24) | 있음 (A16) | **없음** |

42개 상위 단위 중 **23개 채택, 16개 버림, 2개를 기제로 대체, 1개 명시적 부정**, 그리고 신규 2개.

**통합의 실질은 텍스트 압축이 아니라 기제 치환이다.** 두 상위가 산문으로 선언하던 지속성과
호출 방식(P2·P17·A16의 절반)이 훅과 saved state로 옮겨갔다. 78.5%의 바이트 감소 중 상당 부분이
거기서 나온다 — 행동 규칙을 줄인 것이 아니라 **행동 규칙을 유지하는 장치를 텍스트에서 코드로**
옮긴 것이다.

동시에 그 이전 과정에서 **우선순위 조항이 텍스트에도 코드에도 남지 않았다.** 기제로 옮겨간 것이
아니라 사라졌다.

## 7. 견고성 연구에 대한 사전 예측 (반증 가능)

대역 지침은 위 두 `SKILL.md`의 본문(frontmatter 제거 후 합 12,072자)이다. 각 upstream의
자기 hook이 실제로 주입하는 양은 11,584자로 조금 더 작다 — ponytail이 mode 필터로 기본 `full`에서
5,193자를 내고(lite 5,166 / ultra 5,230), i-have-adhd가 6,391자를 낸다. 대역은 필터를 적용하지 않아
ponytail 쪽이 485자 더 크다. 분해가 확정한 사실 위에서:

1. **`BEH-ENG-05`의 신호는 사라진다.** ponytail P23이 LeanClarity E8과 거의 축자로 같다
   (*"non-trivial logic leaves ONE runnable check behind, the smallest thing that fails if the
   logic breaks"*). 대역이 실린 상태에서는 LeanClarity ON/OFF가 이 케이스를 가르지 못해야 한다.
   갈린다면 2,486자가 12,072자보다 같은 행동을 더 잘 유도한다는 뜻이고, 그것도 발표할 값이다.
2. **`BEH-GUI-07`은 양쪽 다 계속 실패한다.** A13이 대역에 그대로 있으므로, 정책이 이 행동을
   유도하지 못하는 것이 텍스트 문제가 아니라는 기존 진단이 옳다면 대역도 못 유도한다.
3. **`BEH-SAFE-02`는 대역만으로도 가드가 보존된다.** P18이 대역에 있다. LeanClarity가 없어도
   같은 보호가 걸린다면 E7의 한계 기여는 0이다.
4. **`BEH-ENG-06`은 갈릴 수 있다.** `E2`는 대역 어디에도 없는 LeanClarity 신규 조항이다.
   대역이 실린 상태에서 LeanClarity ON만 review-only 요청에 코드를 고치지 않는다면, 그것이
   통합이 더한 유일한 순증 행동이다.

네 예측 모두 96 run으로 반증 가능하다. 1·3이 맞으면 LeanClarity의 순가치는 압축과 기제이지
행동이 아니다. 4가 맞으면 신규 조항 두 개가 그 순가치다.
