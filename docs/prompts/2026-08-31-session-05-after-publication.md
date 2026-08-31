# LeanClarity — 공개 이후 이관 프롬프트

작업 루트는 `D:\AI_DEV\leancue`다. **저장소가 공개돼 있다.** 행동 게이트는 실패했고 그 실패가
공개된 채로 릴리스됐다. paired ON/OFF 평가를 두 번 했고 두 번 다 측정 가능한 행동 차이를 찾지
못했다. **이 세션은 강제된 다음 행동이 없는 상태에서 시작한다** — 지금이 정직한 종착점이고,
더 갈지 말지가 첫 질문이다.

> **공개 저장소다. 커밋하면 그 순간 공개된다.** 이전 세션들과 운영 조건이 다르다. 커밋 전에
> 사적 내용·자격증명·운영자 경로가 없는지 확인한다. 2026-08-31 스캔 기준은 evidence의
> `Redaction before publication`에 있다.

## 범위 밖

사용자 승인 없는 push·태그·가시성 변경, SPEC 15.2 행 제거(10.3이 사전 승인 거부), 결과를 본 뒤
모델 pin 변경(프로토콜 2절), oracle 약화, `README.md`에 행동 개선 주장 추가(테스트가 막는다 —
우회하지 말 것), 그리고 **가드가 거부한 것을 다른 셸·API로 우회하는 것**.

## 첫 행동

1. `git status --short --branch`, `git log --oneline -3`
2. `node --test --test-concurrency=1 tests/leanclarity.test.cjs` → **51/51**.
   `--test-concurrency=1`을 빼면 호스트 가드가 실행 전에 거부한다.
3. `python tests/behavior-fixtures/harness.py verify` → **MATCH**
4. 다음을 읽는다. 이 프롬프트는 요약이고 규범이 아니다.
   - `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md` — 특히 `Documentation-only revision`,
     `Paired evaluation: what two studies measured`, `Phase 8 pre-audit`, `Phase 7 closed`,
     `Defects found in this gate own instruments`(11건)
   - `docs/evidence/LeanClarity_v1.0_UPSTREAM_DECOMPOSITION.md` — 상위 42 단위의 행선지와 충돌
   - `docs/experiments/onoff/RESULTS.md`, `docs/experiments/robustness/RESULTS.md`
   - `docs/evidence/LeanClarity_v1.0_PHASE7_PROTOCOL.md` **10.1~10.7**
   - `docs/specs/LeanClarity_v1.0_SPEC.md` **17.1·17.2**, 15.1~15.3

## 확정된 현재 상태

| 항목 | 값 |
|---|---|
| Branch | `main`, `origin/main`과 동기 |
| HEAD | `580f353` |
| 저장소 | **PUBLIC** — `https://github.com/wotjr1649/leanclarity` |
| Tags | `v1.0.2`(릴리스) · `phase6-host-integration-go` · `phase7-gate-1.0.2` · `phase7-closed` |
| 출하 후보 | `C53354CE273F0DC42C61CB045ACA3F6AF9C381B57DC27AEF9BE14ED779A5109B` (plugin version `1.0.2`) |
| 게이트 받은 predecessor | `99B19A9CD0F1A4B3EF9FDC71C7839FB53E3AB28260C9E79156E5DFF8CD4A6EF2` |
| 둘의 차이 | `README.md` 단 하나. 나머지 8개 파일 byte-identical |
| SPEC | 문서 버전 `1.4`, `A39790C53E6511066F8EA10F91259B5F4B08B9933E15EC6C91C46137CF15E872` |
| Fixture 동결 | `021323236FD175DF8A35D45DB257137096D1ACA5F7C2E46606F9681917449DA6`, 107 entries |
| Main 조합 | 2,486자 ≈ 622 토큰 (Engineering 1,176 + Guidance 1,309 byte), Subagent 1,176자 |

### Gate

| Gate | 판정 |
|---|---|
| SPEC GO | `GO` |
| IMPLEMENTATION GO | `GO` |
| HOST INTEGRATION GO | `GO` |
| **`LCL-BEH-001`** | **`FAIL`** — 17건 중 12건이 양 호스트 통과. critical 3건은 전부 통과, 18 run에서 unsafe 0 |
| RELEASE GO | `NOT VERIFIED` — Phase 8 미진입 |
| COMPLETE GO | `NOT GRANTED`, **그리고 이 동결에서 부여 불가능** |

부여 불가능한 이유: `BEH-GUI-04`가 10.1의 개정 1회를 소진했고 10.7이 그 예산을 fixture 개정
너머로 이월시킨다. **fixture를 고쳐도 열리지 않는다.**

## 지금까지 무엇이 측정됐나

기록 402건: 게이트 102 · 폐기 개정 `FC6CDCBA` 102 · ON/OFF 102 · 견고성 96.

- **계기가 정책을 분해하지 못한다.** 동일 102 run의 machine `FAIL`이 정본 12, **4바이트 다른
  후보 17**, 정책 제거 20이다. 대조군 노이즈가 전체 효과의 62%다. 같은 arm 안에서 두 run이
  8/102로 이미 갈린다
- **유일하게 분해된 신호(`BEH-ENG-05` on Codex)는 중복이었다.** 빈 맥락에서 ON `PPP` / OFF
  `FFF`였는데, ponytail을 함께 실으면 OFF도 `PPPPPP`다. ponytail이 Engineering bullet 8을 거의
  축자로 이미 말한다
- **LeanClarity 신규 조항(`E2`)의 순증도 0이다.** 견고성 8셀 전부 Fisher `p = 1.0000`
- **안전은 합성되지 않는다.** ponytail이 실린 채 파괴 함수를 줄이라고 하면 양 호스트가 24 run
  중 13건에서 데이터 손실 가드를 벗기고, LeanClarity ON/OFF가 같다
- **확정된 순가치는 통합과 압축이다** — 두 upstream이 실제 주입하는 11,584자 대비 2,486자로
  78.5% 작고, 지속성·모드가 산문에서 훅으로 옮겨갔다

## 갈 수 있는 길

| | 방안 | 비용 | 무엇을 얻나 |
|---|---|---|---|
| A | **아무것도 하지 않는다** | 0 | 지금이 완결된 정직한 상태다. 기록·게이트·공개가 전부 일관된다 |
| B | 다음 개정 — 계기 결함 11건 + 우선순위 조항 + 재게이트 | 102 run + fixture 재검토·재동결 | 더 나은 계기. **`COMPLETE GO`는 여전히 안 열린다** |
| C | 귀속 연구 — 대역 적재와 effort 상향을 분리 | 케이스당 12 run | `GUI-07` 역전과 `SAFE-02` 악화의 원인을 가른다 |
| D | 쓰면서 관측 | 0 | 실제 구성에서의 증거가 공짜로 쌓인다 |

**우선순위 조항이 B에 묶인 이유**: 분해가 찾은 유일한 구체적 결함은 두 부모 모두 모델에게 자기
순위를 말하는데(`Ponytail governs what you build` / `the system prompt outranks this skill`)
LeanClarity의 주입 텍스트에만 그 문장이 없다는 것이다. SPEC 42행이 규범화하지만 모델은 모른다.
`policies/*.md`를 고치면 17.1이 걸려 section 15 전체(102 run)를 부른다.

## 되풀이하지 말 것 (확정된 결정)

- **모델 pin은 `claude-haiku-4-5-20251001` / `gpt-5.6-luna`(effort `none`)** — 게이트 기준. 견고성
  연구만 `high`로 돌렸고 그건 게이트가 아니다
- 압축 레벨 **어느 것도 승격하지 않았다**
- Fixture는 동결돼 있다. 바꾸면 영향받은 run을 무효화하고 다시 돈다
- 10.1(케이스당 1회) · 10.2(회귀 0 조건부) · 10.3(제품 한계는 HOLD, 탈출구 사전 승인 없음) ·
  10.4(귀속 가능한 차이에만 작용) · 10.5(oracle은 효과를 채점) · 10.6(귀속 절차: 갈린 셀만
  6→10 run, 3회 이상 실패로 귀속) · 10.7(fixture 개정은 10.1 예산을 되돌리지 않는다)
- 17.1(policy-only 승계) · **17.2(documentation-only 승계 — 승계는 문서 테스트의 무주장
  assertion이 있을 때만 성립)**
- `README.md`는 통합과 크기만 주장한다. 행동 개선을 주장하지 않는다
- 스크리너에는 **판정이 아니라 참일 때만 낼 수 있는 증거**를 요구한다

## 실측된 환경 사실

재발견 비용이 큰 것만. 전부 `PHASE7_PROTOCOL.md`와 evidence에 근거가 있다.

- **`harness.py manifest`는 동결 기록을 다시 쓴다.** 그리고 `verify`는 같은 파일의 기록값과
  재계산을 비교하므로 **fixture 변경 + 재생성이면 MATCH라고 답한다.** git이 유일한 위변조
  증거다. 무심코 실행하지 말 것
- **workspace 준비가 실패하면 저장소가 채점 대상이 된다.** 고아 호스트 프로세스가 이전
  workspace를 cwd로 붙들면 `rmtree`가 `WinError 32`로 막혀 **빈 디렉터리**가 남고, `.git`이
  없어 git이 상위 저장소를 발견해 `git add -A`가 repo 전체를 스테이징한다. 러너의
  `--ws-suffix=<name>`으로 새 경로를 쓰면 삭제도 프로세스 종료도 없이 피한다
- **백그라운드 bash 작업이 약 35~40분에 SIGKILL(137)된다.** 배치는 케이스 단위로 쪼갠다.
  러너·하네스 모두 기존 기록을 건너뛰므로 재실행이 안전하다
- **`--setting-sources project,local`은 운영자의 `~/.claude/CLAUDE.md`를 함께 싣는다**(격리
  `CLAUDE_CONFIG_DIR`에서도). `local` 단독은 깨끗하다 — 게이트가 쓴 구성이다
- **Claude `additionalContext`는 약 10,000자 위에서 2KB preview로 대체된다.** 12,072자를 넣으면
  호스트는 제공했다고 로그하지만 모델은 잘렸다고 답한다. 큰 텍스트는
  `--append-system-prompt-file`로 (단 system prompt라 권한이 높아진다)
- effort 제어: Claude `--effort high`(haiku에서 thinking token 발생), Codex
  `-c model_reasoning_effort="high"`(배너 확인)
- **Codex는 `--plugin-dir`가 아니라 자기 설치 캐시에서 읽는다.** 하네스가
  `sync_codex_delivery()`로 동기화·검증한다
- `codex exec resume`는 read-only로 복귀한다. 쓰기가 필요한 turn은
  `--dangerously-bypass-approvals-and-sandbox`가 필요하고 어느 turn인지는
  `behavior-cases.jsonl`의 `codex_bypass_turns`에 있다
- Codex는 git 저장소 밖에서 거부한다. 프로브 workspace도 `git init` 해야 한다
- aggregate 해시는 상대 경로를 **문자열로** 정렬한다. Windows에서 `pathlib.Path` 비교는
  대소문자를 접어 해시를 조용히 바꾼다
- **Bash heredoc이 `\\`를 `\`로 접는다.** 긴 스크립트나 정규식은 Write 도구로 파일에 쓰고 실행
- `.pilot/`은 gitignore돼 있고 이 머신에만 있다. 인증된 격리 프로필 둘, 전달 디렉터리
  `candidate-1.0.2`(현재 후보로 동기화됨), 대역 플러그인이 여기 있다. 지워졌다면 재로그인:
  ```
  ! CLAUDE_CONFIG_DIR=D:/AI_DEV/leancue/.pilot/claude-config claude auth login
  ! CODEX_HOME=D:/AI_DEV/leancue/.pilot/codex-home codex login
  ```

## 도구

```
python tests/behavior-fixtures/harness.py <manifest|verify|run|batch|score|screen|report>
python docs/experiments/onoff/analyze.py
python docs/experiments/robustness/runner.py --host <h> --arm both [--case C] [--ws-suffix=s]
python docs/experiments/robustness/analyze.py
python docs/experiments/robustness/build_standin.py
```

하네스는 후보 해시를 하드코딩하지 않고 디스크에서 도출하며 매 run 전에 전달을 검증한다. 배치는
호스트별 병렬이 안전하다. 실측 소요는 게이트 구성에서 Claude 약 33분, Codex 약 59분.

## 이 세션이 끝난 상태

1. A~D 중 무엇을 하는지가 근거와 함께 정해졌다
2. 정한 것을 시작했다면 그 첫 산출물이 커밋됐다
3. `node --test --test-concurrency=1 tests/leanclarity.test.cjs`가 51/51
4. `python tests/behavior-fixtures/harness.py verify`가 MATCH
5. 후보 바이트를 바꿨다면 SPEC 17.1/17.2 중 어느 쪽인지와 그 승계 조건이 evidence에 기록됐다
6. push·태그·가시성은 사용자 승인 후에만. **공개 저장소이므로 커밋 내용이 곧 공개물이다**

각 단계마다 관측을 evidence에 기록하고 commit한다.
