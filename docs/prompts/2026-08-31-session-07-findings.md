# LeanClarity — FINDINGS 작성 이관 프롬프트

작업 루트는 `D:\AI_DEV\leancue`다. **저장소가 공개돼 있다.** 커밋하면 그 순간 공개된다.

**선행 조건: 세션 06(`docs/prompts/2026-08-31-session-06-codex-insitu.md`)이 끝나고 그
브랜치가 `main`에 병합돼 있어야 한다.** 이 세션이 쓰는 글의 마지막 장이 그 연구의 결과다.
병합돼 있지 않으면 여기서 멈추고 사용자에게 알린다.

> **브랜치를 먼저 만든다.** `git switch -c findings`. push·태그는 **사용자 승인 후에만**.

## 이 세션이 만드는 것

`FINDINGS.md` — 저장소 최상위, **영어**, 읽는 데 15~20분(3,000~5,000 단어).

**이것이 이 프로젝트의 산출물이다.** 플러그인이 아니다. 사용자는 이 저장소의 목적을
"측정 실패 자체가 산출물"로 확정했고, 독자를 셋으로 본다 — 방법론을 볼 사람(찾고 있는
대상), 실제 설치자, 이슈 제보자.

## 글이 주장하는 것

**방법에 대한 주장이다.** 제품에 대한 주장("LeanClarity는 효과가 없다")도, 프로세스에 대한
주장("자기 제품에 게이트를 걸면 이렇게 된다")도 아니다. 그 둘은 소재로 쓰되 결론이 아니다.

> 프롬프트 지침이 모델 행동을 바꾸는지를 이 규모에서 정직하게 재는 것은 얼마가 들고,
> 왜 실패하는가.

**실패의 종류를 틀리지 말 것.** 두 가지 결론이 가능하고 독자가 가져가는 교훈이 정반대다.

- 표본이 모자랐다 — 자원의 문제. 더 크게 했으면 됐다.
- **설계가 답할 수 없는 것을 물었다** — 17개 합성 케이스와 `2/3` 임계값으로는 이 크기의
  효과를 원리적으로 분해할 수 없다.

**후자로 쓴다.** 근거 둘이 이미 기록에 있다. 프로토콜 10.6이 `0.96 → 0.80` 하락을 검출력
80%로 잡으려면 셀당 39 run, 게이트당 1,326 run이 든다고 **미리** 계산해뒀다. 그리고 570
run이 찾아낸 것은 계기 결함 12건과 **텍스트로 고칠 수 있다고 확인된 policy 결함 0건**이다.

## 반드시 들어가야 하는 것 — `FAIL`의 지위

이 글이 "설계가 답할 수 없는 것을 물었다"고 말하면, 독자는 **"그럼 `LCL-BEH-001` `FAIL`도
못 믿는 것 아니냐"**로 읽는다. 그대로 두면 README와 `v1.0.3` 태그가 게시하고 있는 게이트
상태가 근거를 잃는다.

**답은 기록에 있다.** `GO_EVIDENCE.md`가 *"The `FAIL` sits outside the gate's noise floor.
The adoption rule does not"*라고 적고, flip rate 8/102에서 유도한 `p = 0.9591`로 다섯 케이스가
전부 3/3으로 떨어질 확률을 계산해뒀다 — `BEH-GUI-04`의 두 후보에 걸친 6연속 실패가 `4.7e-9`다.

**설계가 못 한 것은 효과의 귀속이지 실패의 관측이 아니다.** 이 구분을 명시적으로 쓴다.

## 다루는 범위 — 다섯 연구, 570 run

| 연구 | run | 결과 |
|---|---:|---|
| 압축 파일럿 (`docs/experiments/`) | 144 | 승격된 압축 레벨 0 |
| 게이트 `99B19A9C` (`docs/evidence/phase7-runs/`) | 102 | `LCL-BEH-001` `FAIL`, 17개 중 5개 미통과 |
| 폐기 개정 `FC6CDCBA` (`docs/evidence/phase7-runs-FC6CDCBA/`) | 102 | 4바이트 차이, 대상 미수정, 폐기 |
| ON/OFF (`docs/experiments/onoff/`) | 102 | 계기가 정책을 분해하지 못함 |
| 견고성 (`docs/experiments/robustness/`) | 96 | 8셀 전부 Fisher `p = 1.0000` |
| 귀속 (`docs/experiments/attribution/`) | 24 | 1차 케이스가 계기 결함에 소실 |
| in-situ (`docs/experiments/insitu/`) | 세션 06 | 실제 환경 |
| **합계** | **570** | **분해된 행동 효과 0건** |

압축 파일럿을 뺄 수 없다. 144 run으로 어떤 레벨도 승격하지 못한 것이 **"설계가 답할 수 없는
것을 물었다"의 가장 이른 증거**다. 다른 질문을 물었다는 이유로 빼면 논지가 약해진다.

## upstream 둘을 어디까지 말하는가

**측정된 것만 적는다.** Ponytail과 i-have-adhd는 MIT로 파생해 온 상대다.

적을 수 있는 것: 대역으로 실렸을 때 관측된 사실. ponytail이 Engineering bullet 8을 거의
축자로 이미 말한다는 것, 그래서 유일하게 분해됐던 신호가 중복이었다는 것, 그리고 ponytail
자신의 *"Never simplify away … error handling that prevents data loss"* 조항이 실린 채로도
가드가 벗겨졌다는 것.

**적지 않는 것**: "이 부류의 지침은 어느 것도 검증된 적이 없다" 같은 일반화. 사실일 수
있으나 타인의 프로젝트에 대한 공개 주장이 되고, 이 프로젝트는 측정하지 않은 것을 주장하지
않는 규율로 여기까지 왔다.

## 한계로 적을 것

- **커버리지 공백.** 18 bullet 중 5개(`E1`·`E5`·`G4`·`G8`·`G10`)가 fixture로 시험된 적이
  없고, `BEH-GUI-08`은 대응 bullet이 없다. `UPSTREAM_DECOMPOSITION.md` 4절이 근거다.
  메우지 않는다 — 목표가 측정 실패의 기록이라면 공백도 그 기록의 일부다.
- **재현 불가.** 유료 계정 둘, 격리 프로필, pin된 모델 두 개, Windows가 필요하다. 재현
  안내를 쓰지 않고 **불가하다는 것을 적는다.**
- **계기 결함 12건 대 policy 결함 0건.** 이 비율 자체가 논지의 핵심 증거다.
- **`COMPLETE GO`는 닫혀 있다.** 여는 두 경로가 각각 자기이익적 감사와 10.3이 거부한
  탈출구다. 세션 06이 `GO_EVIDENCE.md`에 이것을 명시했을 것이다.

## 함께 하는 작업

### 한국어 RESULTS 영어화 — 병기, 원본 보존

`docs/experiments/robustness/RESULTS.md`와 `docs/experiments/attribution/RESULTS.md`가
한국어다. 읽히길 원하는 방법론 문서가 한국어인 것이 지금 상태의 가장 큰 도달 제약이다.

**대체하지 않는다.** 영어본을 `RESULTS.md`로 두고 원본을 `RESULTS.ko.md`로 남긴다.
`attribution/RESULTS.md`는 이미 `v1.0.3`에 담겨 공개됐고, 이 프로젝트는 폐기한 개정조차
기록에 남긴다. 번역 오류가 정본이 되는 것을 막는다.

같은 세션이 영어 FINDINGS를 쓰면서 하므로 용어와 어조가 일치한다.

`SPEC`·`PHASE7_PROTOCOL`·`FIXTURE_REVIEW`·`UPSTREAM_DECOMPOSITION`은 **번역하지 않는다.**
내부 문서이고, 분량이 크고, 번역 오류가 기록을 손상시킬 위험이 이득보다 크다.

### `README.md` 포인터 → SPEC 17.2 개정 → `v1.0.4`

README 첫 화면에서 `FINDINGS.md`를 가리킨다. **README는 배포 9개 파일에 속하므로 이것이
candidate identity를 바꾼다.**

SPEC 17.2 절차를 그대로 따른다. 직전 두 번의 선례가 `GO_EVIDENCE.md`의
*Documentation-only revision `C53354CE`*와 *`84B828BA`* 절에 있다.

1. 예정 predecessor의 aggregate와 파일별 byte set을 **먼저 기록한다**
2. `README.md`만 바꾸고, 나머지 8개가 byte-identical함을 **파일별로 검증한다**
3. 새 candidate identity를 계산해 evidence에 기록한다 (`harness.CANDIDATE_ID`)
4. operator documentation test를 전부 돌린다 — 남용 방지 assertion이 통과해야 승계가 성립한다
5. 51/51 · `harness.py verify` MATCH
6. 사용자 승인 후 `v1.0.4` 태그. **태그 규칙: 배포 9개 파일이 바뀌면 언제나.** 정정인지
   추가인지 판단하지 않는다
7. 태그 annotation에 게이트 표를 그대로 싣는다 — 직전 두 태그의 형식을 따른다

**plugin version은 `1.0.2`에서 움직이지 않는다.** 매니페스트에 있으므로 올리면 17.2 승계를
잃고 Phase 6 전수 재관측 + 102 run을 새로 진다. 태그명은 릴리스 표식이지 버전 선언이 아니고,
`v1.0.3` annotation 첫 문단이 그 선례다.

## 범위 밖

사용자 승인 없는 push·태그·가시성 변경, SPEC 15.2 행 제거, 결과를 본 뒤 모델 pin 변경,
oracle 약화, `README.md`에 행동 개선 주장 추가(테스트가 막는다 — 우회하지 말 것), fixture
동결 변경, 그리고 **가드가 거부한 것을 다른 셸·API로 우회하는 것**.

**어떤 게이트도 움직이지 않는다.** `LCL-BEH-001` `FAIL`, `RELEASE GO` `NOT VERIFIED`,
`COMPLETE GO` `NOT GRANTED` 그대로다.

## 첫 행동

1. `git log --oneline -5` — 세션 06의 병합을 확인한다. 없으면 멈춘다
2. `git switch -c findings`
3. `node --test --test-concurrency=1 tests/leanclarity.test.cjs` → **51/51**
4. `python tests/behavior-fixtures/harness.py verify` → **MATCH**.
   `harness.py manifest`는 **절대 실행하지 말 것**
5. 다음을 읽는다. 이 프롬프트는 요약이고 규범이 아니다
   - `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md` — 특히 `Phase 7 closed`,
     `Paired evaluation`, `Defects found in this gate own instruments`(12건),
     두 `Documentation-only revision` 절, `Residual uncertainty`
   - `docs/evidence/LeanClarity_v1.0_PHASE7_PROTOCOL.md` **10.1~10.7**
   - `docs/evidence/LeanClarity_v1.0_UPSTREAM_DECOMPOSITION.md` — 특히 4절(커버리지 공백)과
     5절(충돌 C1~C7)
   - 다섯 연구의 `RESULTS.md` 전부
   - `docs/specs/LeanClarity_v1.0_SPEC.md` **17.1·17.2**, 15.1~15.3

## 글에 대한 규율

- **130KB짜리 `GO_EVIDENCE.md`를 다시 쓰지 않는다.** 그것은 이미 있고 아무도 읽지 않는다.
  FINDINGS는 근거를 링크로 넘기고 논지만 든다.
- **수치는 기록에서 직접 읽어 온다.** 이 프롬프트의 표를 그대로 옮기지 말고 재확인한다.
  이 프로젝트가 세 번 고친 것이 전부 옮겨 적은 수치였다.
- **`README.md`가 이미 말한 것을 반복하지 않는다.** README는 operator 문서이고 FINDINGS는
  방법론 글이다. 겹치면 README를 가리킨다.
- 마지막 장은 세션 06의 in-situ 결과다. 그 연구가 답하지 못했으면 답하지 못한 것을 적는다.

## 이 세션이 끝난 상태

1. `FINDINGS.md`가 영어로, 방법에 대한 주장으로, 15~20분 분량으로 존재한다
2. `LCL-BEH-001` `FAIL`의 지위가 명시돼 있다 — 못 한 것은 귀속이지 관측이 아니다
3. 다섯 연구와 570 run이 전부 다뤄졌고, 압축 파일럿이 가장 이른 증거로 들어갔다
4. `robustness`·`attribution`의 `RESULTS.md`가 영어이고 `RESULTS.ko.md`가 원본을 보존한다
5. `README.md`가 `FINDINGS.md`를 가리키고, SPEC 17.2 개정이 evidence에 기록됐다
6. `node --test --test-concurrency=1 tests/leanclarity.test.cjs`가 51/51
7. `python tests/behavior-fixtures/harness.py verify`가 MATCH
8. `findings` 브랜치에 커밋됐다. **push·병합·`v1.0.4` 태그는 사용자 승인 후에만**

각 단계마다 관측을 evidence에 기록하고 commit한다.
