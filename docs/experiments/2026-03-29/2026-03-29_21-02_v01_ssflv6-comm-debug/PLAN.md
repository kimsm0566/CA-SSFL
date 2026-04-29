# 실험 계획

## 메타데이터

- 실험 id: `2026-03-29_21-02_v01_ssflv6-comm-debug`
- 초안 일시: `2026-03-29 21:02 KST`
- 상태: `1차 진단 완료`
- 담당자: `Codex + 사용자`

## 목표

현재 `SSFLv6` full run에서 200라운드 누적 통신량이 약 `28386.97 MB`로 관측되는 원인을 찾아, matched 조건에서 누적 통신량을 `21000 MB 미만`으로 다시 낮출 수 있는 수정 방향을 식별하고 검증한다.

성공 기준은 다음과 같다.

- 현재 통신량 상승이 `측정 로직 변화`인지, `실제 활성 차원 증가`인지, `모델 파라미터 전송량 증가`인지 분해해서 설명할 수 있다.
- 원인 가설별로 가장 작은 재현 실험과 검증 포인트가 정의된다.
- 후속 코드 수정이 들어간다면 smoke 및 matched 비교에서 `Total comm < 21000 MB`를 다시 확인할 수 있는 실행 계획이 준비된다.

## 지금 하는 이유

- 현재 baseline `SSFLv6` 로그는 200라운드에서 `Total comm: 28386.97 MB`, `Total data comm: 18992.34 MB`, `Total model comm: 9394.63 MB`로 끝난다.
- 사용자가 기억하는 기존 값은 `21000 MB 미만`이며, 최소한 현재 결과보다 유의하게 낮았다고 보고 있다.
- 현재 로그만 봐도 데이터 통신량과 모델 통신량이 둘 다 올라가 있어, 단일 원인보다 “모델 크기 변화 + 마스크/활성 차원 변화 + 비교 기준 혼선”을 함께 점검해야 한다.

현재까지 확인된 사실:

- 현재 기준 로그:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full/.../seed_1_server.log`
  - 200라운드 수치: `Total comm 28386.97 MB`, `Total data comm 18992.34 MB`, `Total model comm 9394.63 MB`
- 참고용 과거 로그:
  - `src/output.log`
  - 200라운드 수치 중 하나는 `Total comm 24613.84 MB`, `Total data comm 16263.06 MB`, `Total model comm 8350.78 MB`
- 다만 `src/output.log`의 확인 가능한 run 시작점은 `SSFLv6_w_o_vib`이며, 현재 비교 대상이 정말 baseline `SSFLv6`와 matched인지 먼저 검증이 필요하다.
- 현재 코드상 서버 통신량은 두 덩어리로 계산된다.
  - 모델 통신량:
    - 클라이언트에서 서버로 보내는 local weights
    - 서버에서 클라이언트로 다시 보내는 avg weights
  - 데이터 통신량:
    - forward 활성 요소 수
    - index overhead
    - backward compressed gradient 요소 수
- 현재 로그의 per-round model comm은 약 `46.97 MB`, 과거 참고 로그는 약 `41.75 MB` 수준이라 모델 전송량도 증가했다.
- 현재 로그의 per-round data comm은 대략 `77~80 MB`, 과거 참고 로그는 대략 `68~74 MB` 수준이라 데이터 전송량도 증가했다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - 필요 시 `src/models/model.py`
  - 필요 시 진단용 문서/스크립트:
    - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/`
- 의도한 동작 변화:
  - 먼저 통신량 상승의 원인을 정확히 진단한다.
  - 원인 확인 후, 통신량을 낮추는 최소 수정만 적용한다.
  - 최종적으로 canonical `SSFLv6` 경로에서 누적 통신량을 다시 낮춘다.
- 유지할 조건:
  - dataset, partition, client 수, batch size, rounds, algorithm, channel, compressed dim, beta, threshold, seeds는 비교 시 고정한다.
  - historical raw artifact는 덮어쓰지 않는다.
  - 통신량을 낮추기 위해 정확도나 측정 정의를 몰래 바꾸지 않는다.

## 후보 접근법

- 접근 A:
  - 먼저 “비교 기준이 정말 같은가”를 검증한다.
  - 과거의 `21000 MB 미만` 근거가 baseline `SSFLv6`인지, 다른 알고리즘/코드 버전인지, 다른 하이퍼파라미터인지 먼저 분리한다.
  - 장점: 잘못된 baseline 착각으로 헛디버깅하는 일을 막을 수 있다.
  - 단점: 바로 코드 수정은 못 한다.

- 접근 B:
  - 모델 통신량과 데이터 통신량을 별도 가설로 쪼개서 계측한다.
  - 예:
    - 모델 파라미터 수 증가 여부
    - aggregation에 포함되는 state_dict 항목 변화 여부
    - active index 개수 평균 증가 여부
    - `torch.count_nonzero` 기반 forward accounting이 예전과 다르게 커졌는지
  - 장점: 어느 항목이 얼마나 올랐는지 바로 보인다.
  - 단점: 추가 로그나 진단 코드가 필요할 수 있다.

- 접근 C:
  - 예전 값에 맞추려는 수정 후보를 바로 좁힌다.
  - 우선 후보:
    - aggregation 통신량 계산 기준 재검토
    - `state_dict()` 전체 대신 실제 학습 파라미터만 집계하는지 점검
    - `SSFLv6`의 mask/active index 경로가 예전보다 덜 sparse해진 원인 점검
  - 장점: 목표값 회복에 직접적이다.
  - 단점: 원인 확정 전에 손대면 잘못된 수정이 될 수 있다.

- 우선 접근법과 그 이유:
  - `A -> B -> C` 순서로 간다.
  - 이유: 현재 상승분은 모델 comm과 data comm이 동시에 올라간 상태라, baseline 정의와 accounting drift를 먼저 고정하지 않으면 수정 효과를 해석할 수 없다.

## 계획된 검증

- 스모크 체크:
  - 현재 `SSFLv6` 경로에서 짧은 run으로 진단 로그가 정상적으로 찍히는지 확인
  - 모델 파라미터 총량, round별 평균 active 차원, index overhead, backward gradient 크기를 별도 로그로 남기는 최소 실험
- 비교 대상:
  - 현재 Docker baseline `SSFLv6` 로그
  - 비교 가능하면 과거 baseline `SSFLv6` 로그 또는 artifact
  - 비교 불가능하면 현재 코드에서 계측된 세부 통신 항목끼리 분해 비교
- 예상 산출물 경로:
  - 문서:
    - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/PLAN.md`
    - 후속 `SPEC.md`, `WORKLOG.md`, `RESULT.md`
  - 진단 artifact:
    - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/`

## 리스크와 열린 질문

- 기술적 리스크:
  - 과거 `21000 MB 미만` 기준의 정확한 matched artifact가 없으면 원인 규명이 늦어질 수 있다.
  - 현재 full run은 시간이 길어서 작은 계측 실험으로 먼저 좁혀야 한다.
  - 통신량 감소 수정이 정확도 저하를 유발할 수 있다.

- 평가상 리스크:
  - 비교 대상이 실제로 다른 알고리즘이었는데 baseline처럼 해석하면 잘못된 결론이 나온다.
  - accounting 로직 변경만으로 통신량이 낮아졌는데 실제 wire cost가 줄어든 것처럼 오해할 수 있다.

- 검토가 필요한 질문:
  - 사용자가 기억하는 “21000 MB 미만”의 근거 artifact가 저장소 안에 더 있는가?
  - 목표는 “예전 accounting 재현”인가, 아니면 “현재 코드 기준 실제 전송량 감소”인가?
  - `21000 MB 미만`은 seed `1` 기준인지, 평균 기준인지?

## 사용자 검토 메모

- 피드백:
  - 현재 `SSFLv6` 로그의 200라운드 통신량이 과거보다 높다.
  - 이 값을 `21000 MB 미만`으로 다시 낮출 수 있도록 디버깅 plan이 필요하다.
- 합의된 결정:
  - 아직 없음. 이 `PLAN.md` 검토 후 `SPEC.md`로 고정 예정.
- 남은 쟁점:
  - 과거 비교 기준의 정확한 artifact 식별
  - accounting 수정과 알고리즘 수정 중 우선순위

## 실행 게이트

- 구현 시작 가능?: `아니오`
- 아니라면 먼저 명확히 할 점:
  - 과거 baseline 근거를 확인하고, 진단용 계측 범위를 `SPEC.md`에 고정해야 한다.
