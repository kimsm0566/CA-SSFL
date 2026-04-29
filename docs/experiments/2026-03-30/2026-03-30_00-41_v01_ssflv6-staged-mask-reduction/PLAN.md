# 실험 계획

## 메타데이터

- 실험 id: `2026-03-30_00-41_v01_ssflv6-staged-mask-reduction`
- 초안 일시: `2026-03-30 00:41 KST`
- 상태: 승인
- 담당자: Codex

## 목표

`SSFLv6`의 active 차원과 누적 통신량을 단계적으로 줄이되, 정확도 손실이 과도하지 않은 지점을 찾는다.

## 지금 하는 이유

현재 active 구현은 old raw artifact보다 active ratio와 통신량이 높다. 특히 `8x8/4096` encoder와 batch-shared mask가 sparse 효과를 약화시키고 있어, 작은 변경부터 순차적으로 분리 검증할 가치가 있다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - `src/models/model.py`
- 의도한 동작 변화:
  - 1단계: batch 평균 VIB mask를 샘플별 VIB mask로 되돌리되, 현재 서버/decoder를 유지하기 위해 배치 내 union indices로 전송
  - 2단계: FiLM encoder를 더 작은 gate 구조로 변경해 `data comm`와 `model comm`를 동시에 줄임
  - 3단계: 필요 시 `beta`를 올려 KL 압축 강도를 더 높임
- 유지할 조건:
  - `SSFLv6`, `cifar10`, `class`
  - `n_clients=9`, `n_client_data=3000`, `batch_size=100`
  - `n_epochs=1`
  - 단계 비교는 모두 `n_rounds=200` full run으로 수행
  - `model_type=resnetv2`, `channel_type=rayleigh`
  - `snr_db=12`, `compressed_dim=4096`
  - `pruning_threshold=1.0`, `seed=2`
  - Docker GPU 경로 사용

## 후보 접근법

- 접근 A: 샘플별 mask 복귀 -> `200`라운드 full 비교 -> 다음 단계 진행
- 접근 B: encoder와 beta를 같이 바꾸고 한 번에 sweep
- 우선 접근법과 그 이유: 접근 A. 원인 분리를 유지하면서 각 단계 효과를 사용자에게 바로 보고할 수 있다.

## 계획된 검증

- 스모크 체크:
  - 각 단계 후 `python -m py_compile`
- 비교 대상:
  - 현재 작업트리 baseline round `200`
  - old raw `seed_2`
- 예상 산출물 경로:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/`

## 리스크와 열린 질문

- 기술적 리스크:
  - 샘플별 mask는 현재 wire format과 완전히 호환되지 않으므로 union indices 방식이 필요함
  - encoder 변경은 decoder shape와 맞물려 영향 범위가 큼
- 평가상 리스크:
  - 짧은 초기 round 경향과 full `200` 결과가 다를 수 있으므로 full run만 비교 근거로 사용해야 함
- 검토가 필요한 질문:
  - 1단계만으로도 active ratio가 충분히 내려가는지
  - encoder를 `64` channel gate로 줄일지, old `2x2` 경량형으로 되돌릴지

## 사용자 검토 메모

- 피드백: 단계별로 진행하고 각 단계 후 보고
- 합의된 결정: 1단계부터 순서대로 적용 후 보고하되, 각 단계 비교는 `200`라운드 full run으로 판단
- 남은 쟁점: 2단계 encoder 형태 선택은 1단계 결과 후 재확정

## 실행 게이트

- 구현 시작 가능?: 예
- 아니라면 먼저 명확히 할 점:
