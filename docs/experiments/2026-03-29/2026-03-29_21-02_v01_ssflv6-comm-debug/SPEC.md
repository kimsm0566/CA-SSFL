# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-29_21-02_v01_ssflv6-comm-debug`
- 시작 일시: `2026-03-29 21:04 KST`
- 상태: `진단 완료, 수정 미채택`
- 담당자: `Codex + 사용자`

## 요약

현재 `SSFLv6` baseline의 200라운드 누적 통신량이 `28386.97 MB`까지 올라간 원인을 디버깅했다. 비교 기준 검증, 통신량 항목 분해, 최소 수정 후보 진단까지 마쳤고, 현재 관찰상 모델 통신량과 데이터 통신량이 동시에 증가했다. client state_dict 크기 자체도 round당 `46.97 MB` accounting과 정확히 일치한다.

## 질문

현재 `SSFLv6`의 높은 누적 통신량은 무엇 때문에 발생했으며, 어떤 최소 수정으로 matched 조건에서 `21000 MB 미만`까지 다시 낮출 수 있는가?

## 가설

현재 상승분은 단순 로그 오차가 아니라, `SSFLv6` client model 크기 증가와 활성 차원 증가가 함께 누적된 결과일 가능성이 높다.

## 기준선

- 기준선 알고리즘: 현재 Docker baseline `SSFLv6`
- 기준선 설정:
  - `dataset=cifar10`
  - `partition_type=class`
  - `n_clients=9`
  - `n_client_data=3000`
  - `batch_size=100`
  - `n_epochs=1`
  - `n_rounds=200`
  - `model_type=resnetv2`
  - `channel_type=rayleigh`
  - `snr_db=12`
  - `compressed_dim=4096`
  - `beta=0.0005`
  - `pruning_threshold=1.0`
  - `use_private_SGD=0`
  - `seed=1`
- 기준선 산출물 경로:
  - `docs/experiments/2026-03-29_20-32_v01_ssflv6-ablations/artifacts/ssflv6/full/.../seed_1_server.log`
- 이 비교가 적절한 이유:
  - 현재 문제 제기는 동일 baseline 계열 내 통신량 회귀(regression) 여부를 다루기 때문이다.

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200` for matched rerun, `1~5` for diagnosis smoke
- channel_type: `rayleigh`
- seed_set: `1`
- evaluation_path:
  - Docker GPU 경로만 사용
  - 현재 baseline 로그와 진단 재실행 비교

## 변경 변수

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - 필요 시 `src/models/model.py`
  - 문서:
    - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/`
- 바꾸는 변수:
  - 1차는 코드 변경 없이 진단
  - 2차부터 최소 수정 후보를 하나씩 적용
- 탐색 범위:
  - model comm 분해
  - data comm 분해
  - baseline artifact 정합성 확인

## 지표

### 주요 지표

- `Total comm`
- `Total data comm`
- `Total model comm`

### 보조 지표

- round당 `Data` MB
- round당 `Model` MB
- client active ratio
- state_dict one-copy MB

## 검증 계획

### 스모크 체크

- 명령어:
  - 현재 코드에서 model `state_dict()` 총 크기 계산
  - top parameter 항목 크기 출력
  - 짧은 Docker run에서 round별 active ratio와 per-round comm 확인
- 성공 신호:
  - 현재 `46.97 MB/round model comm`의 근거를 코드/모델 크기로 설명 가능
  - `data comm` 증가 원인을 active ratio 쪽으로 좁힐 수 있음

### 매칭 비교

- 명령어:
  - 비교 가능한 과거 baseline artifact가 있으면 같은 조건으로 대조
  - 수정 후보 적용 후 seed `1` matched rerun
- 예상 산출물 경로:
  - `docs/experiments/2026-03-29_21-02_v01_ssflv6-comm-debug/artifacts/`

### 강건성 후속 검증

- 추가 seed:
  - 회귀 수정이 유효해 보이면 `1,2,3,4`
- 추가 SNR:
  - 이번 범위 밖
- 추가 channel 설정:
  - 이번 범위 밖

## 승격 기준

다음이 모두 충족되면 통신량 회귀 수정 후보를 승격한다.

- matched 조건에서 `Total comm < 21000 MB`
- accounting 정의가 바뀐 것이 아니라 실제 항목 감소가 확인됨
- 정확도 저하가 설명 가능하거나 허용 범위 내

## 중단 기준

- 과거 비교 기준이 baseline `SSFLv6`가 아닌 것으로 확인됨
- 수정이 통신량만 낮추고 정확도를 과도하게 해침
- accounting 로직 변경만으로 숫자만 낮추는 상태가 됨

## 리스크와 교란 요인

- 가능한 교란 요인:
  - 과거 로그가 다른 알고리즘일 가능성
  - Docker/current code와 과거 host run의 코드 버전 차이
  - `class` partition warning이 active ratio에 간접 영향
- 예상 실패 모드:
  - model comm와 data comm 상승 원인이 서로 독립이어서 단일 수정으로 해결되지 않음
  - 비교 가능한 과거 baseline artifact 부재
- 결과를 무효화할 수 있는 요소:
  - 다른 알고리즘 또는 다른 state_dict 구조를 baseline처럼 비교하는 경우
