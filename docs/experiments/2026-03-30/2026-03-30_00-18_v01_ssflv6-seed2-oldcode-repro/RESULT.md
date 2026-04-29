# 결과 요약

## 결과

- 상태: `패`
- 결정: `반복`

## 무엇을 테스트했는가

사용자가 최근 변경한 `_run_clientv6`와 현재 작업트리의 `FiLMChannelAwareEncoder` 기준으로 `SSFLv6 seed=2`를 재실행해 old raw `seed_2`가 재현되는지 확인했다.

## 최종 비교

- baseline: `src/results/.../seed_2_server.log`, `docs/experiments/.../orig-threshold-rerun-seed2/.../seed_2_server.log`
- candidate: `현재 작업트리 상태의 SSFLv6 seed=2 full rerun`
- 고정 조건 일치 여부: `예`
- seeds: `2`
- 산출물 경로:
  - `docs/experiments/2026-03-30_00-18_v01_ssflv6-seed2-oldcode-repro/artifacts/full/`

## 주요 지표

- 정확도:
  - rerun round `200` acc `42.19%`
  - old raw round `200` acc `42.06%`
  - current canonical rerun round `200` acc `42.19%`
- 통신량:
  - rerun `30541.49 MB`
  - old raw `21128.55 MB`
  - current canonical rerun `30541.49 MB`
- SNR 강건성:
  - rerun `Test SNR 12dB 42.32%`
- seed 분산: `해당 없음`

## 해석

이번 rerun은 old raw `seed_2`를 재현하지 못했다. 수치가 직전 canonical rerun과 사실상 완전히 같으므로, 사용자가 기대한 “예전 코드” 효과는 현재 작업트리 기준으로 나타나지 않는다. 핵심은 `src/utils/trainer.py`의 `_run_clientv6`가 일부 sparse 경로를 사용하더라도, `src/models/model.py`의 active `FiLMChannelAwareEncoder`가 여전히 `8x8/4096` 구조라는 점이다. old raw를 설명할 수 있는 경량 `2x2 -> compressed_dim` encoder는 현재 주석 블록에만 남아 있다.

## 알려진 한계

- `seed=2` 단일 재현만 확인했다.
- current client log late-round line 매칭은 old raw와 포맷 차이가 있다.

## 다음 권장 행동

- active `FiLMChannelAwareEncoder`를 old `2x2` 경량형으로 실제 교체한 뒤 동일 조건 재실행
- `_run_clientv6`와 encoder를 분리해 어느 쪽이 통신량 차이를 만드는지 진단
