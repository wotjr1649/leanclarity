# 견고성 연구 — 설계

Not release evidence. 어떤 GO도 부여하거나 막지 않는다. `LCL-BEH-001`은 `FAIL`,
`RELEASE GO`는 `NOT VERIFIED`, `COMPLETE GO`는 `NOT GRANTED`로 그대로다.

**공개 전 가장 먼저 받을 질문에 답한다: 원본 둘을 이미 쓰는 사용자에게 LeanClarity
2,486자를 더 실으면 무엇이 달라지는가.**

ON/OFF 연구는 *빈 맥락*에서 정책의 효과를 물었고 "이 계기로는 분해되지 않는다"로
끝났다. 이 연구는 *다른 지침이 이미 실린 맥락*에서 같은 것을 묻는다. SPEC 9절이
"운영자 자신의 전역 지시 파일이 함께 실릴 때의 합성 효과는 측정하지 않는다"고 적어둔
축이고, 지금까지 한 번도 측정된 적이 없다.

## 설계

| 항목 | 값 |
|---|---|
| 케이스 | `BEH-ENG-05`, `BEH-GUI-07`, `BEH-SAFE-02`, `BEH-ENG-06` |
| 셀당 run | **6** |
| 호스트 | Claude Code `2.1.251`, Codex CLI `0.150.1` |
| arm | LeanClarity **ON / OFF**, 대역 지침은 **양 arm 모두** 적재 |
| 총 run | 4 × 6 × 2 × 2 = **96** |
| 모델 | `claude-haiku-4-5-20251001`, `gpt-5.6-luna` — 게이트와 동일 |
| effort | **high** 양쪽 (`--effort high`, `-c model_reasoning_effort="high"`) |
| fixture | 동결본 `021323236FD…` 그대로. `harness.py verify`가 이후에도 MATCH여야 한다 |
| 후보 | `99B19A9C…`, 바이트 무변경 |

**arm은 교차 실행한다.** 각 케이스×run 안에서 ON 직후 OFF를 돌린다. ON/OFF 연구가
제거하지 못한 유일한 교란이 창간 드리프트였고(두 arm이 13시간 떨어져 있었다), 여기서는
상태 파일 쓰기 한 번이면 된다.

## 케이스 선정 기준 — 결과를 보기 전에 고정

**(i) 기계로 판정되는 신호를 가질 것.** ON/OFF 연구에서 분해된 신호는 전부 diff가
정하는 사실이었고, predicate 묶음은 전부 드리프트했다. **(ii) 네 축을 덮을 것.**

| 케이스 | 축 | 결정 신호 |
|---|---|---|
| `BEH-ENG-05` | ON/OFF 연구에서 유일하게 분해된 신호 | `test_lines_added` (diff) |
| `BEH-GUI-07` | 30전 0승, 모든 인코딩에서 실패 | `impl_markers`·`assumption_substrings` (diff) |
| `BEH-SAFE-02` | critical이자 최다 드리프트 셀 | 실행 oracle |
| `BEH-ENG-06` | 계측 결함으로 재분류, 재설계 대상 | `require_empty_diff` (diff) |

## effort 상향은 게이트 행위가 아니다

프로토콜 2절은 **게이트**에 대해 결과를 본 뒤 모델·설정을 올리는 것을 금지한다. 이
연구는 게이트가 아니고 어떤 GO도 건드리지 않는다. effort `none`/기본값은 하한 구성으로
선택된 것이었고, 여기서 묻는 것은 "실제로 쓰는 구성에서 어떤가"다. 두 제어는 실측으로
확인했다 — Claude `--effort high`는 haiku에서 thinking token을 발생시키고, Codex
`-c model_reasoning_effort="high"`는 배너에 `reasoning effort: high`를 찍는다.

**이 연구의 어떤 결과도 `LCL-BEH-001`에 반영되지 않는다.**

## 대역 지침

| | |
|---|---|
| 내용 | `ponytail/skills/ponytail/SKILL.md` 본문 + `i-have-adhd/skills/i-have-adhd/SKILL.md` 본문 |
| pinned | `2ed6c52c9d7e5e56942508591085fd45dea277d3` · `cbe69fb83c08a37cf54d5ec9ec6bb88c8bc9973c` |
| 크기 | **12,072자** (frontmatter 제거 후. 원본 파일은 13,710 bytes / 13,429자이고 frontmatter는 모델에 도달하지 않는다). 각 upstream의 자기 hook이 실제로 주입하는 양은 11,584자로 더 작다 — ponytail이 mode 필터로 5,193자, i-have-adhd가 6,391자 |
| SHA-256 | `9F41ABF3D76A46690C2D8D0CE968480238EE3573D3DD7E9A40D716EEF0158E86` |
| 생성 | `build_standin.py` — 각 upstream 자신의 hook이 쓰는 것과 같은 frontmatter 정규식 |

`AGENTS.md`가 아니라 `SKILL.md`가 정본이다. `i-have-adhd/AGENTS.md`에는 행동 규칙이
하나도 없다(분해 문서 참조).

**중복이 크다. 그게 요점이다.** ponytail은 LeanClarity Engineering 8을 거의 축자로
이미 의무화한다. 이 연구는 "임의의 사용자 지침 아래 견고한가"가 아니라 **"원본을 이미
쓰는 사용자에게 순증 가치가 있는가"**에 답한다. 가장 혹독한 쪽이다.

## 적재 경로 — 실측으로 정했다

| 호스트 | 경로 | 근거 |
|---|---|---|
| Claude | `--append-system-prompt-file` | additionalContext 채널이 이 크기를 못 나른다 |
| Codex | workspace `AGENTS.md`, baseline 커밋에 포함 | 프로브가 두 꼬리 문장을 축자 인용 |

세 가지를 실측했다 (2026-08-30, Claude Code `2.1.251`).

1. **`--setting-sources project,local`은 운영자 자신의 `~/.claude/CLAUDE.md`를 함께
   싣는다.** 그 파일에만 있는 정확한 구절로 프로브했을 때 `project,local`
   에서 HIT, `local` 단독에서 NONE. **게이트가 쓴 `local` 구성은 깨끗하다** — Phase 7이
   운영자 지침에 오염되지 않았다는 첫 직접 확인이다.
2. **additionalContext 채널은 12,072자를 못 나른다.** 대역을 SessionStart 훅으로 주입한
   플러그인을 만들어 붙였더니 호스트는 `provided additionalContext (12072 chars)`를
   기록했지만 모델은 *"only a 2KB preview is visible and the full text is truncated"*라고
   답했다. SPEC 11이 문서화한 "Claude 10,000-character 이후 file-preview replacement"의
   경계 위쪽을 처음으로 관측한 것이다. 후보의 2,486자는 아래쪽에서 온전히 전달된다.
3. `--add-dir`로는 적재되지 않는다.

**한계, 미리 적는다.** Claude에서 대역은 system prompt에 놓이고 Codex에서는 프로젝트
맥락에 놓인다. 실제 사용자의 `CLAUDE.md`는 맥락이지 system prompt가 아니므로, Claude
쪽 대역은 현실보다 **권한이 높다.** 따라서 Claude에서 LeanClarity 효과가 사라지면
"중복이라 불필요"와 "대역에 눌렸다"를 구별할 수 없다. Codex 쪽이 더 깨끗하다. 이 경로를
고른 것은 다른 경로가 오염되거나(1) 물리적으로 불가능하기(2) 때문이다.

## arm 증명

Claude는 매 turn 자기 증명한다 — `--debug-file`이 `provided additionalContext (N chars)`를
LeanClarity가 주입했을 때만 쓴다. 대역은 system prompt로 가므로 이 계수기에 섞이지 않는다.
**ON arm은 모든 turn이 `[2486]`, OFF arm은 모든 turn이 `[]`여야 한다.** Codex는 turn별
계수기가 없으므로 배치 전후 프로브 로그로 덮는다.

## 분석

쌍 단위는 **셀**(케이스 × 호스트), `n = 8`. 각 셀에서 ON 6 run vs OFF 6 run.

- **1차: machine verdict.** 셀마다 Fisher 정확검정 2×2. 6대6에서 완전 분리
  (6/6 vs 0/6)의 양측 p는 `2/C(12,6) = 0.0022`. **5대1 분리는 p ≈ 0.08로 유의하지 않다.**
  즉 이 설계는 거의 완전한 분리만 잡는다. 그것이 6 run을 산 이유다.
- **2차: 응답 문자수, diff churn.** 셀마다 순열검정 (라벨 뒤섞기 12개, 전수 924가지).
- 8 셀 × 2 계열에 Holm 보정. `alpha = 0.05`.
- REVIEW는 판정이 아니다. 스크리너는 verdict가 갈린 셀에서만, 갈린 run에만 돌린다.

## 사전 등록 예측 (분해 문서에서 도출, 반증 가능)

| # | 예측 | 근거 |
|---|---|---|
| 1 | `BEH-ENG-05`는 **분리되지 않는다** | ponytail이 Engineering 8을 거의 축자로 이미 말한다 |
| 2 | `BEH-GUI-07`은 **양 arm 모두 실패** | i-have-adhd A13이 대역에 그대로 있는데도 실패한다면 텍스트 문제가 아니다 |
| 3 | `BEH-SAFE-02`는 **분리되지 않는다** | ponytail P18이 대역에 있다. 분리되지 않으면 Engineering 7의 한계 기여는 0 |
| 4 | `BEH-ENG-06`은 **분리될 수 있다** | `E2`는 대역 어디에도 없는 LeanClarity 신규 조항이다 |

1·3이 맞으면 LeanClarity의 순가치는 압축과 기제이지 행동이 아니다. 4가 맞으면 신규
조항이 그 순가치다.

## 공개 (disclosure)

이 문서는 96 run 중 **2건이 이미 존재하는 상태**에서 쓰였다 — `BEH-GUI-07` Claude r1의
두 arm으로, 실제 소요를 재는 파일럿이었다. 그 두 건의 verdict를 봤다(ON `PASS`,
OFF `REVIEW`). 나머지 94건과 모든 연속 지표는 이 문서 이후다. 설계·기준·예측은
파일럿 이전에 결정된 것이며, 그 사실을 주장하는 대신 이렇게 적어 둔다.

## 이 연구가 말하지 못하는 것

- 대역은 두 개의 특정 upstream이다. 임의의 사용자 지침을 대표하지 않는다.
- pin된 두 모델의 effort `high` 밖으로 일반화되지 않는다.
- 네 케이스는 SPEC 15.2를 겨냥해 만든 합성 fixture다. 실제 작업의 표본이 아니다.
- 어떤 게이트도 부여·차단·수정하지 않는다.
