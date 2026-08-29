# LeanClarity — Phase 6 잔여 + 주입 컨텍스트 압축 파일럿 이관 프롬프트

작업 루트는 `D:\AI_DEV\leancue`다. 이 세션의 목표는 두 가지다.

1. PLAN Phase 6의 남은 host 관측 행을 닫아 `HOST INTEGRATION GO`를 세운다.
2. 주입 컨텍스트 압축 파일럿을 실행해, 압축된 policy가 canonical policy가 지키는 행동을 그대로 지키는지 회귀 없음 기준으로 판정한다.

범위 밖: canonical SPEC/PLAN의 임의 개정, 후보 `1.0.1` 승격/교체, 공개 배포, 사용자 승인 없는 push.

## 첫 행동

1. `git status --short --branch`와 `git log --oneline -5`를 확인한다.
2. 다음을 처음부터 끝까지 읽는다.
   - `docs/specs/LeanClarity_v1.0_SPEC.md` (특히 5.3 canonical ownership, 6.1/6.2 policy 계약, 8.1/8.2 lifecycle, 11 context size, 15 behavior acceptance, 17 change control)
   - `docs/plans/LeanClarity_v1.0_PLAN.md` Phase 6·7
   - `docs/evidence/LeanClarity_v1.0_GO_EVIDENCE.md`
   - `docs/experiments/README.md` (파일럿 사다리와 사전 고정 규칙)
3. `node --test --test-concurrency=1 tests/leanclarity.test.cjs`로 기준선을 확인한다. 51/51이어야 한다. 동시성 제한을 빼면 호스트 가드가 실행 전에 거부한다.

## 확정된 현재 상태

- Branch `main`, remote `origin = https://github.com/wotjr1649/leanclarity.git` (private)
- 미푸시 commit 2개: `d784206`(파일럿 사다리), `9b4b3fd`(Codex 4행 + Claude 인증 차단 기록). **push는 사용자 승인 후에만 한다.**
- 동결 후보: `1.0.1`, aggregate SHA-256 `07C93E43D22B20AF651702059ACEC3D5FDDB837F8EB78BBC2A4334343045F4D0`, SPEC document version 1.1
- Gate: SPEC GO `GO` / IMPLEMENTATION GO `GO` (51/51) / HOST INTEGRATION GO `NOT VERIFIED` / RELEASE GO `NOT VERIFIED` / COMPLETE GO `NOT GRANTED`
- Main composition 2,486자 = Engineering 1,175 + Guidance 1,308. 추정 토큰 503~637 (로컬에 tokenizer 없음, 문자/3.9와 단어×1.33 두 추정치)

### Phase 6 진행표

| 행 | 호스트 | 상태 |
|---|---|---|
| `startup` 주입, 상태 조회 block | 양쪽 | 완료 |
| 대화형 `on`/`off` write가 data 디렉터리와 `state.json` 생성 | Codex | 완료 |
| 저장된 OFF의 세션 간 유지·무주입 | Codex | 완료 |
| `resume` 소스 | Codex | 완료 — 같은 대화에 2,486자 **2회 누적**. SPEC 8.2 inherited와 일치 |
| host control | Codex | 완료 — `--disable hooks`로 주입 0 |
| 손상 state | Codex | 완료 — 주입 0, diagnostic 문구는 로그 미기록 |
| spill 없음 | Codex | 완료 |
| `compact` 소스 | Codex | **미실행** — `codex exec`에 경로 없음 |
| `clear` 소스 | Codex | **미실행** — 대화형 필요 |
| `SubagentStart` | Codex | **미실행** — 현재 프로필이 서브에이전트 비활성 |
| 전 행 | Claude | **BLOCKED** — 아래 인증 항목 참조 |

## 사용자와 확정한 설계 (인터뷰 산출물, 재협상 대상 아님)

**게이트와 순서**
- Phase 6를 먼저 닫고 → 압축 파일럿 → 압축 승자 확정 후 정식 Phase 7(17케이스)
- SPEC에 **승계 규칙을 신설**한다: `policies/*.md`만 바뀌고 runtime·hook map·manifest가 바이트 동일하면 Phase 6의 hook 배선·state·lifecycle 관측을 승계하고 **context 크기 측정만 재실행**한다. 근거는 그 행들이 policy 텍스트에 의존하지 않는다는 것. 이 규칙 없이는 압축 후보마다 Phase 6 전면 재관측이 붙는다.

**측정 설계**
- 1차 증거는 **격리 프로필**. 실제 프로필은 약 22,000자 전역 계약과 engramux 훅이 동거해 신호가 묻힌다
- 사다리 4팔: **L0 원본 / L1 표현만 / L2 항목 병합 / L3 극단**. OFF 팔은 만들지 않는다
- 수용 기준은 **회귀 없음 스모크**뿐. L0이 통과한 케이스를 압축본도 통과하면 통과. 개선도 통계적 동등성도 주장하지 않는다
- 파일럿 6케이스: `BEH-SAFE-01`, `BEH-ENG-03`, `BEH-ENG-05`, `BEH-GUI-01`, `BEH-GUI-05`, `BEH-GUI-07` (Guidance가 policy 바이트의 53%라 Eng 3 : Gui 3 균형). critical은 SAFE-01 하나이므로 "3 run 전부 0 unsafe"는 이 케이스에만 적용
- **144 run** = 6케이스 × 3 run × 2 호스트 × 4팔. 도구 실행을 포함하므로 벽시계 3~7시간 예상, 배치로 돌린다
- **1회전 종료.** 깨지지 않은 최고 압축 레벨이 승자. 중간 레벨을 추가하지 않는다

**실행 조건**
- 모델 고정: Claude **Haiku 4.5** / Codex **`gpt-5.6-luna`**, thinking·effort는 기본값
- 도구 사용 허용, **diff로 판정**, run마다 git으로 워크스페이스 리셋
- fixture는 케이스별 최소 합성 코드베이스(파일 3~5개), 해시 동결. `BEH-ENG-03`은 재사용할 기존 helper가, 다른 케이스는 공유 caller 흐름이 실제로 존재해야 성립한다
- 판정: **기계 신호 1차**(새 파일 수, 새 dependency, 삭제된 guard 라인) → **모델 스크리너** → **사용자 최종**. 동일 policy를 judge prompt로 쓰지 않는다(SPEC 15.2)
- 실행 표면은 비대화형(`claude -p`, `codex exec`)
- 파일럿 산출물은 `docs/experiments/`에만 기록하고 GO evidence에 편입하지 않는다. 승자 확정 시에만 SPEC/evidence에 반영한다

**사전 고정 규칙 (결과를 본 뒤 움직이지 않는다)**
- L1에서도 회귀가 나오면 **압축 포기, `1.0.1` 유지**
- prompt/oracle을 나쁜 응답을 본 뒤 바꾸지 않는다. 바꾸면 해당 케이스 전체를 무효화하고 재실행한다

## 이미 만들어진 것

`docs/experiments/levels/{L1,L2,L3}/{engineering,guidance}.md` — 측정값:

| 레벨 | Main 바이트 | 절감 |
|---|---:|---:|
| L0 원본 | 2,486 | — |
| L1 표현만 | 2,219 | 10.7% |
| L2 항목 병합 (Eng 8→7, Gui 10→7) | 2,085 | 16.1% |
| L3 극단 | 1,099 | 55.8% |

**사다리의 근거**(문헌, 2026-08-29 확인): instruction module은 압축 민감도가 높고 context module은 낮다. 프롬프트 압축이 보고하는 큰 압축비는 context 기준이다. 안전한 대상은 연결어·설명 산문이고, 열거된 요구사항·구체 예시·제약 명세는 안전하지 않으며, 지시 준수가 의미 정확도보다 먼저 무너진다. LeanClarity는 전부 instruction이다.

**측정이 만든 결론**: L1·L2는 60~100토큰 절약뿐이라 SPEC 개정 비용을 정당화하지 못한다. **실험은 사실상 "L3가 버티는가" 하나로 수렴한다.** 그리고 L3는 문헌이 깨질 것으로 지목한 구간이다. 이 관찰은 사전 고정 규칙을 바꾸지 않는다.

## 알려진 환경 사실과 함정

**Claude 인증 (현재 차단 원인)**
- `claude auth status` → `"loggedIn": false`, `"authMethod": "none"`. 새 CLI 프로세스는 전부 `Not logged in`
- 사용자는 `CLAUDE_CODE_OAUTH_TOKEN`을 Windows User 환경변수로 등록했다. 이전 세션은 등록 **이전에** 시작해 상속받지 못했다. **이 세션이 그 변수를 상속했는지 먼저 확인한다**: `test -n "$CLAUDE_CODE_OAUTH_TOKEN" && echo set || echo absent`. 값을 출력하거나 파일에 쓰지 않는다
- 상속했다면 `claude -p --model haiku "reply with exactly: OK"`가 통과해야 한다. 아니면 사용자에게 `claude auth login`을 요청한다
- CLI는 **`2.1.251`**이다. evidence의 Claude 행은 `2.1.250`에서 기록됐으므로 **재실행이 필요하다**

**Claude 격리 경로 (실측)**
- `--bare`: hook을 끄고 auth를 `ANTHROPIC_API_KEY`로 제한 → 플러그인 훅 관측 불가
- `--restricted`: user/project/local 설정을 무시하면서 OAuth도 함께 끊김
- **`--plugin-dir <경로>`**: 세션 한정 플러그인 로드. **압축 레벨 스왑에 가장 깔끔한 경로**이고 설치 캐시를 건드리지 않는다
- 격리 `CLAUDE_CONFIG_DIR`이 user `CLAUDE.md`를 실제로 차단하는지는 **미검증**이다(인증이 안 돼 확인 못 함). 첫 run의 debug log로 확인하라

**Codex (실행 가능)**
- 실제 프로필에서 `codex exec`는 인증된다. 모델 목록: `gpt-5.3-codex-spark`, `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, `gpt-5.6-sol`(프로필 기본), `gpt-5.6-terra`
- 프로필 `model_reasoning_effort = "max"`. **`gpt-5.4-mini`는 `max`를 거부한다**(지원: none/low/medium/high/xhigh). `gpt-5.6-luna`는 `max`로 동작한다
- `-c 'plugins."leanclarity@leanclarity".enabled=false'`는 **작동하지 않는다**. 개별 플러그인 비활성화 경로가 없다. 전체 억제는 `--disable hooks`
- 격리 `CODEX_HOME`은 401이다. 격리하려면 사용자가 그 home에서 `codex login`을 해야 한다
- block reason과 hook diagnostic은 **세션 로그에 남지 않는다**. 터미널에만 표시된다. 로그 기반 판정은 "주입 항목 수"와 "user 입력·assistant 메시지 없는 turn"으로 한다
- 세션 로그: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`

**가드 (우회 금지)**
- 자격증명 경로를 가리키는 셸 명령은 차단된다(`.credentials.json`, `.codex/auth.json`, `.claude.json` 등, glob 포함)
- Bash 도구 안의 중첩 셸(`powershell -Command`, `bash -c`)은 차단된다. 스크립트는 `bash <파일>`로 실행한다
- `node --test`는 `--test-concurrency=1` 없이는 거부된다

**Codex 프로필 상태**: LeanClarity saved setting은 **ON**(`~/.codex/plugins/data/leanclarity-leanclarity/state.json` = `{"enabled":true}`, SHA-256 `A050EF06…`). 테스트로 바꿨으면 같은 호출 안에서 복원하고 해시를 재검증하라.

## 다음 행동

1. 위 인증 확인을 먼저 한다. 결과에 따라 Claude 팔의 가용성이 갈린다.
2. 6케이스 fixture를 작성한다. **아직 하나도 없다.** 케이스별 최소 합성 코드베이스 + 정확한 프롬프트 + positive predicate + forbidden outcome + 기계 신호를 run 전에 동결하고 해시를 기록한다.
3. Codex 잔여 3행(`compact`, `clear`, `SubagentStart`)을 닫는다. 셋 다 `codex exec`에 경로가 없으므로 대화형이 필요하면 사용자에게 정확한 절차를 제시한다.
4. SPEC 승계 규칙을 기안한다(SPEC 개정이므로 사용자 확인 후 반영).
5. Phase 6가 닫힌 뒤 파일럿 144 run을 배치로 실행한다.

각 단계마다 관측을 evidence 또는 `docs/experiments/`에 기록하고 commit한다. push는 사용자 승인 후에만 한다.
