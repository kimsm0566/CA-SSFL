# 실험 스펙

## 메타데이터

- 실험 id: `2026-03-29_23-50_v01_ssflv6-stronger-channel-mask`
- 시작 일시: `2026-03-29 23:50 KST`
- 상태: `진행중`
- 담당자: `Codex + 사용자`

## 요약

현재 canonical `SSFLv6`의 channel mask threshold를 현재보다 소폭 강화한다. 기존 식 `0.5 - (snr_normalized * 0.3)` 대신 더 강한 식을 적용하고, `seed=1`, `n_rounds=5` 진단으로 data comm, model comm, active ratio를 비교한다.

## 질문

현재 threshold를 조금 더 공격적으로 바꾸면 `SSFLv6`의 data comm를 줄이면서도 초기 성능과 model comm를 크게 해치지 않을 수 있는가?

## 가설

threshold를 소폭 상향하면 active ratio가 내려가고 data comm가 줄어든다. 변화 폭이 크지 않다면 초기 정확도 손상도 제한적일 수 있다.

## 기준선

- 기준선 알고리즘: `SSFLv6`
- 기준선 설정:
  - `dataset=cifar10`
  - `partition_type=class`
  - `n_clients=9`
  - `n_client_data=3000`
  - `batch_size=100`
  - `n_epochs=1`
  - `n_rounds=5`
  - `model_type=resnetv2`
  - `channel_type=rayleigh`
  - `snr_db=12`
  - `compressed_dim=4096`
  - `beta=0.0005`
  - `pruning_threshold=1.0`
  - `use_private_SGD=0`
  - `seed=1`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `9`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `5`
- channel_type: `rayleigh`
- snr_db: `12`
- compressed_dim: `4096`
- beta: `0.0005`
- pruning_threshold: `1.0`
- use_private_SGD: `0`
- seed_set: `1`

## 변경 변수

- 대상 코드 경로:
  - `src/utils/trainer.py`
- 바꾸는 변수:
  - `dynamic_threshold`
- 적용 식:
  - current canonical: `0.5 - (snr_normalized * 0.3)`
  - stronger candidate: `max(0.25, min(0.60, 0.60 - (snr_normalized * 0.35)))`

## 지표

- `Total comm`
- `Total data comm`
- `Total model comm`
- `avg_active_indices`
- round `5` acc

## 검증 계획

- 명령어:
  - `python -m py_compile src/utils/trainer.py`
  - `docker compose run --rm sfl-semantic run-exp --dataset=cifar10 --algorithm=SSFLv6 --channel_type=rayleigh --partition_type=class --n_clients=9 --n_client_data=3000 --batch_size=100 --n_epochs=1 --n_rounds=5 --model_type=resnetv2 --snr_db=12 --use_private_SGD=0 --optimizer=adam --lr=0.001 --compressed_dim=4096 --beta=0.0005 --pruning_threshold=1.0 --major_percent=0.7 --seed=1 --verbose=1 --result_path=/workspace/docs/experiments/2026-03-29_23-50_v01_ssflv6-stronger-channel-mask/artifacts/diag_ssflv6_5r`
- 성공 신호:
  - current canonical보다 `avg_active_indices`와 `data comm`가 내려감
  - `model comm`는 유지됨

