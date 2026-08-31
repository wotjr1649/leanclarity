# LeanClarity — Codex in-situ 측정 이관 프롬프트

작업 루트는 `D:\AI_DEV\leancue`다. **저장소가 공개돼 있고 `v1.0.3`까지 태그돼 있다.** 커밋하면
그 순간 공개된다. 커밋 전에 사적 내용·자격증명·운영자 홈 경로가 없는지 확인한다.

**이 세션은 다섯 번째 연구다.** 앞의 네 연구와 게이트는 전부 격리 프로필에서 `codex exec`로
돌았다. 이번에는 **운영자의 실제 Codex 환경에서 직접** 측정한다. 그것이 이 연구의 유일한
새로움이고, 동시에 유일한 약점이다.

> **브랜치를 먼저 만든다.** `git switch -c insitu-measurement`. 이 세션은 `main`에 직접
> 커밋하지 않는다. push·병합·태그는 **사용자 승인 후에만**.

## 이 세션이 하는 두 가지

1. **측정** — 실제 Codex에서 LeanClarity의 주입·제어·생명주기가 살아남는지.
2. **정리 작업** — 아래 목록. 이것은 그 자체로 필요한 일이면서, **동시에 compact를 자연
   발생시키는 누적 수단이다.** 작업을 하다 보면 컨텍스트가 쌓이고, 거기서 compact가 난다.

두 번째가 첫 번째의 도구라는 점이 이 설계의 핵심이다. 합성 부하로 창을 밀어 올리는 것은
이미 해봤고(`.pilot/codex_compact.py`가 `model_context_window=24000`으로 강제했다), 그것은
실제 창에서의 실제 누적이 아니다.

## 범위 밖

사용자 승인 없는 push·병합·태그·저장소 가시성 변경, **플러그인 재설치나 `~/.codex` 상태
변경**, fixture 동결 변경, oracle 수정, SPEC 15.2 행 제거, `README.md`에 행동 개선 주장 추가,
그리고 **가드가 거부한 것을 다른 셸·API로 우회하는 것**.

이 연구는 **어떤 게이트도 부여·차단·수정하지 않는다.** `LCL-BEH-001`은 `FAIL`, `RELEASE GO`는
`NOT VERIFIED`, `COMPLETE GO`는 `NOT GRANTED`이고 그대로 둔다.

## 첫 행동

1. `git status --short --branch`, `git log --oneline -3` → `3012f67`, `main`과 동기
2. `git switch -c insitu-measurement`
3. `node --test --test-concurrency=1 tests/leanclarity.test.cjs` → **51/51**.
   `--test-concurrency=1`을 빼면 호스트 가드가 실행 전에 거부한다.
4. `python tests/behavior-fixtures/harness.py verify` → **MATCH**.
   `harness.py manifest`는 **절대 실행하지 말 것** — 동결 기록을 다시 쓴다.
5. 아래 *확정된 환경 사실*을 재확인한다. 이 프롬프트는 요약이고 규범이 아니다.

## 확정된 환경 사실 — 2026-08-31 실측

전부 이 세션 직전에 확인했다. 바뀌었을 수 있으니 재확인하되, 재발견 비용이 크므로 여기 적는다.

| 항목 | 값 |
|---|---|
| 실제 Codex 홈 | `~/.codex` (격리 프로필 `.pilot/codex-home`이 **아니다**) |
| 설치 위치 | `~/.codex/plugins/cache/leanclarity/leanclarity/1.0.2/` |
| 저장된 상태 | `~/.codex/plugins/data/leanclarity-leanclarity/state.json` = `{"enabled":true}` |
| 함께 설치된 것 | `ponytail`, `adhd-mode`, `claude-mem-local`, `openai-curated-remote` |
| 운영자 지침 | `~/.codex/AGENTS.md` **11,426 bytes** |
| 등록된 훅 | `~/.codex/hooks.json`에 `engramux`(SessionStart·UserPromptSubmit·Pre/PostToolUse·Stop·SessionEnd)와 `guard.mjs`(PreToolUse Bash) |
| 세션 로그 | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`, 731개 |

### 뒤처진 설치본은 측정에 영향이 없다 — 확인됨

설치본의 `README.md`는 **4,903 bytes**다. 그것은 `99B19A9C`, 즉 *"steers the model toward the
smallest correct engineering solution"*이라는 주장이 든 판이고, 두 paired ON/OFF 연구가
반증해서 삭제한 문장이다. 공개된 정정이 운영자 자신의 설치본에 도달하지 않았다.

**그러나 측정에는 무관하다.** 설치본과 저장소를 바이트 비교한 결과:

| 파일 | 설치본 | 저장소 | |
|---|---:|---:|---|
| `policies/engineering.md` | 1176 | 1176 | **동일** |
| `policies/guidance.md` | 1309 | 1309 | **동일** |
| `hooks/leanclarity.cjs` | 12189 | 12189 | **동일** |
| `hooks/hooks.json` | 724 | 724 | **동일** |

주입되는 것은 `policies/*.md`이고 `README.md`는 어떤 모델 컨텍스트에도 들어가지 않는다.
그것이 SPEC 17.2의 근거이고, 여기서 실제 설치본에 대해 확인됐다. **그러므로 재설치 없이
측정한다.** 설치본이 뒤처졌다는 것은 별개의 기록 사항으로 적는다.

### `~/.codex/hooks.json`에 LeanClarity가 없다

SessionStart에 등록된 것은 `engramux`뿐이다. Codex가 플러그인 캐시의 자체 `hooks/hooks.json`을
발견해서 실행하는지, 아니면 사용자 레벨 등록이 필요한지는 **미확인**이다. 즉 **지금 실제
Codex에서 주입이 되고 있는지조차 확인된 바 없다.**

이것을 확인하는 것이 이 세션의 첫 측정이다. 되고 있지 않다면 그것이 이 연구의 결과다.

## 무엇을 "살아남는다"로 세는가

**주입·제어·생명주기만 잰다. 행동은 재지 않는다.**

행동은 네 연구가 전부 실패한 층이다. 570 run으로 분해되지 않은 것이 비고정 환경의 소수
관측으로 분해될 리 없고, 시도하면 이 연구가 앞의 실패를 반복하는 다섯 번째가 된다.

| 축 | 관측 대상 |
|---|---|
| **주입** | `policies/*.md` 조합 2,486자가 실제로 컨텍스트에 도달하는가 |
| **제어** | `leanclarity` · `leanclarity on` · `leanclarity off`가 인식·차단되는가 |
| **생명주기** | `startup` · `clear` · `resume` · `compact`에서 유지되는가 |

`hooks/leanclarity.cjs:13`이 Codex에 대해 `['startup','clear','resume','compact']`를 받는다.
`fork`는 Codex v1에서 주장하지 않으므로 범위 밖이다.

## 증거 규칙 — 자기보고는 증거가 아니다

**모델에게 "네 컨텍스트에 LeanClarity가 있느냐"고 묻지 않는다.** 모델은 동의해 버린다. 이
프로젝트는 스크리너에게도 판정이 아니라 *참일 때만 낼 수 있는 증거*를 요구했고, 게이트가 그
probe를 설계한 이유가 evidence 429행에 적혀 있다.

**1차 채널 — 축자 인용 probe.** ON/OFF 연구가 양 호스트에서 검증한 방법이다.

- ON이면 Engineering Policy의 **첫 bullet을 축자로** 낼 수 있다.
- OFF면 `NONE`을 낸다.
- 잘림·preview 대체·유실을 잡으려면 **꼬리도 함께** 요구한다 — Guidance Policy의 마지막
  bullet. 잘린 주입은 꼬리를 만들지 못한다.

정본은 `policies/engineering.md`와 `policies/guidance.md`다. 프롬프트에 정답을 싣지 말 것 —
싣는 순간 probe가 아니라 받아쓰기가 된다.

**2차 채널 — rollout 로그 교차검증.** `~/.codex/sessions/.../rollout-*.jsonl`은 세션당
`leanclarity`를 정확히 1회 언급한다. 그것이 주입 텍스트인지 단순 경로 참조인지는 **미확인**이다.
값 필드로 국소화하는 것이 이 세션의 과제 하나다. 성립하면 기계적 증거가 되고, 성립하지
않으면 probe만으로 간다. **로그 채널에만 의존하지 말 것** — 없으면 세션이 막힌다.

> **로그는 전체 대화를 담는다.** 저장소에는 관측에 필요한 **발췌만** 넣는다. 원본 jsonl은
> 커밋하지 않는다. 발췌에도 사적 내용이 없는지 확인한다.

## 측정 설계

### 상태 복구가 먼저다

제어 프롬프트 테스트는 `state.json`을 실제로 바꾼다. **이것은 운영자가 매일 쓰는 환경이다.**

- 측정 시작 전에 현재 값을 기록한다 (지금 `{"enabled":true}`).
- `off`를 시험했으면 **반드시 `on`으로 복구하고 복구를 확인한다.**
- 세션 종료 시 상태가 시작 값과 같은지 마지막으로 검증한다.

### 긴 세션 1개 + 짧은 세션 몇 개

각각이 재는 것이 다르다.

**긴 세션** — 정리 작업을 진행하며 자연 누적. 목표는 실제 창에서의 `compact` 관측.
작업 중간중간 probe를 넣어 주입이 유지되는지 본다. compact가 발생하면 **그 직후 probe가
핵심 관측이다.**

**짧은 세션들** — `startup`(새 세션), `clear`, `resume`, 그리고 제어 프롬프트 3종.
각각 깨끗한 경계에서 본다. 긴 세션에 몰아넣으면 제어 테스트가 이후 상태를 오염시킨다.

**반복은 설계하지 않는다.** 이 관측들은 결정적이다 — 주입은 되거나 안 되거나다. 결과가
갈리면 그때 반복이 필요한 관측이고, 그 자체가 발견이다.

### compact — 축소 먼저, 누적 나중

1. **창 축소로 코드 경로 확인.** `.pilot/codex_compact.py`를 참고하되 실제 홈에 대고 돌리지
   말 것. 축소는 `-c model_context_window=<작은 값>`으로 준다. 여기서 실패하면 자연 누적도
   실패하므로 순서가 이렇다.
2. **자연 누적.** 정리 작업을 진행한다. 실제 창 크기에서 실제 작업으로 compact까지 간다.
   여기가 지금까지 **한 번도 관측된 적 없는 지점**이다.

두 경로의 결과가 다르면 그것이 이 연구의 가장 중요한 관측이다 — 축소로 얻은 기존 compact
관측이 실제를 대표하지 않는다는 뜻이 된다.

## 정리 작업 — 누적 수단이자 그 자체로 필요한 일

**`README.md`는 건드리지 않는다.** README 포인터와 `v1.0.4`는 다음 세션(FINDINGS)의 몫이다.
README를 바꾸면 candidate identity가 바뀌고 SPEC 17.2 개정 절차가 이 세션에 딸려 온다.

| 작업 | 내용 |
|---|---|
| 이슈 템플릿 | `.github/ISSUE_TEMPLATE/`. LeanClarity의 실패는 호스트별이다 — host·버전·`state.json`·훅 신뢰 여부·`plugins/data` 존재를 묻지 않으면 재현이 안 된다 |
| `SECURITY.md` | 보고 경로. CONTRIBUTING·CODE_OF_CONDUCT는 기여자가 없는 단계에서 보일러플레이트다 |
| 증거 정정 | `GO_EVIDENCE.md`의 `COMPLETE GO` 애매함. 아래 절 참조 |
| description·topics | 지금 **둘 다 비어 있다**. `gh repo edit`. 문구는 "방법에 대한 주장"이라는 포지셔닝을 따른다 |
| `docs/experiments` 인덱스 | 지금 `docs/experiments/README.md`는 인덱스가 아니라 **압축 파일럿 자체의 글**이다. 진입한 독자가 오독한다. 테스트가 로컬 링크를 검사하므로 옮기면 링크를 함께 고친다 |
| LeanCue 표시 | `docs/specs/LeanCue_v1.1_SPEC.md`(36KB) · `docs/plans/LeanCue_v1.1_PLAN.md`(38KB) · `docs/gpts/…브리프…`(21KB). **종료된 선행 작업**임을 각 문서 머리에 적는다. LeanClarity SPEC이 참조하므로 지우지 않는다 |

### `COMPLETE GO` 애매함 — 두 조건을 적고 닫는다

`GO_EVIDENCE.md`가 *"Reaching it requires a fixture revision under 10.5 and 10.7"*라고만 적어
경로가 열려 있는 것처럼 읽힌다. 프로토콜 10.7과 합치면 **필요조건이지 충분조건이 아니다.**

10.7은 fixture 개정 후에도 10.1 예산이 이월된다고 정하고, `BEH-GUI-04`를 "계기 결함이 기록된
바 없다"는 이유로 **spent로 이월**한다. 그래서 여는 경로는 둘뿐이다.

1. `BEH-GUI-04`의 계기 결함을 개정 **전에** 기록한다 — 그러나 게이트를 막는 그 케이스를
   골라서 뒤지는 것은 프로토콜 8절이 금지하는 자기이익적 행위이고, `BEH-ENG-06`의 P2를 고치지
   않은 이유가 정확히 그것이다.
2. SPEC 15.2 행을 뺀다 — 10.3이 사전 승인을 거부한 탈출구다.

**둘 다 현재 없다는 것을 적고 닫는다.** 경로를 숨기지 않되 문을 정직하게 닫는 것이다.

## 산출물

`docs/experiments/insitu/`

| 파일 | 내용 |
|---|---|
| `PROTOCOL.md` | **첫 관측 전에 커밋한다.** 앞의 세 연구가 그렇게 했다. 설계를 결과 뒤에 쓰면 결과에 맞춘 설계가 된다 |
| `RESULTS.md` | 관측, 그리고 무엇을 주장할 수 없는지 |
| `observations/` | probe 응답과 로그 발췌. 원본 jsonl은 넣지 않는다 |

`PROTOCOL.md`가 **먼저** 고정해야 할 것: 무엇을 ON/OFF의 증거로 받아들이는가, 무엇을 관측
실패로 보고하는가, 상태 복구를 어떻게 검증하는가, 그리고 **결과를 무엇으로 세지 않는가**.

## 되풀이하지 말 것

- **자기보고를 증거로 쓰지 않는다.** 축자 probe 아니면 로그다.
- **환경을 통제하려 들지 않는다.** ponytail·adhd-mode·engramux·guard·`AGENTS.md` 전부 실린
  채로 잰다. 통제하는 순간 앞의 세 연구의 반복이 되고, 귀속은 어차피 포기했다. **대신 무엇이
  실렸는지를 바이트 단위로 전수 기록한다.**
- **행동을 재지 않는다.** 570 run이 분해하지 못한 것을 소수 관측으로 분해하려 들지 않는다.
- **제품 버그가 나오면 기록하고 멈춘다.** 수정은 별도 세션이다. 특히 주입이 아예 안 되고
  있다면 그것은 큰 발견이고, 같은 세션에서 고치면 관측과 수정이 섞인다. 이 프로젝트는
  나쁜 응답을 본 뒤 oracle을 고치는 것을 금지하는 규율로 여기까지 왔다.
- **fixture·oracle·후보 바이트를 건드리지 않는다.** 세션 끝에 `harness.py verify`가 MATCH여야
  한다.

## 실측된 환경 사실 — 재발견 비용이 큰 것

- **`harness.py manifest`는 동결 기록을 다시 쓴다.** 그리고 `verify`는 같은 파일의 기록값과
  재계산을 비교하므로 fixture 변경 + 재생성이면 MATCH라고 답한다. git이 유일한 위변조 증거다.
- **백그라운드 bash 작업이 약 35~40분에 SIGKILL(137)된다.** 긴 작업은 쪼갠다.
- **Bash heredoc이 `\\`를 `\`로 접는다.** 긴 스크립트나 정규식은 Write 도구로 파일에 쓰고 실행.
- **호스트 가드가 자격증명 경로 이름을 담은 명령을 거부한다** — 스크립트 안의 정규식 문자열도
  포함이다. 우회하지 말고 패턴을 바꾼다.
- **`gh`는 인증돼 있다.** `gh repo view`·`gh repo edit`가 동작한다.
- `codex exec resume`는 read-only로 복귀한다. 쓰기가 필요한 turn은
  `--dangerously-bypass-approvals-and-sandbox`가 필요하다.
- Codex는 git 저장소 밖에서 거부한다.
- **`.pilot/`은 gitignore돼 있고 이 머신에만 있다.** 격리 프로필 둘, 전달 디렉터리
  `candidate-1.0.2`가 여기 있다. **이 세션은 `.pilot/`을 쓰지 않는다** — 실제 홈에서 잰다.

## 이 세션이 끝난 상태

1. `docs/experiments/insitu/PROTOCOL.md`가 **첫 관측 전에** 커밋됐다
2. 주입·제어·생명주기 관측이 축자 probe로 기록됐고, 로그 채널의 성립 여부가 확정됐다
3. compact가 **창 축소와 자연 누적 양쪽에서** 관측됐거나, 관측되지 않은 이유가 기록됐다
4. `state.json`이 시작 값(`{"enabled":true}`)으로 복구됐고 복구가 검증됐다
5. 정리 작업 목록이 처리됐다 (`README.md` 제외)
6. `node --test --test-concurrency=1 tests/leanclarity.test.cjs`가 51/51
7. `python tests/behavior-fixtures/harness.py verify`가 MATCH
8. `insitu-measurement` 브랜치에 커밋됐다. **push·병합·태그는 사용자 승인 후에만**

각 단계마다 관측을 기록하고 commit한다. 다음 세션은 FINDINGS이며, 이 연구의 결과를 마지막
장으로 담는다. 그러므로 **이 브랜치가 `main`에 병합된 뒤에** 시작한다.
