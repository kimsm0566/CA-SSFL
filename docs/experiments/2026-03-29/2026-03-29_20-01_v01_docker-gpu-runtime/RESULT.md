# 결과 요약

## 결과

- 상태: `승`
- 결정: `승격`

## 무엇을 테스트했는가

GPU 전용 Docker runtime으로 `run_exp_main.py`의 최소 smoke run을 통과시키는 하네스 정비를 테스트했다.

## 최종 비교

- baseline: 기존 CPU-only Docker runtime 및 미검증 GPU 경로
- candidate: GPU-enabled Docker runtime
- 고정 조건 일치 여부: `예`
- seeds: `0`
- 산출물 경로: `tmp/docker-gpu-smoke-results/mnist/n_clients_2/n_client_data_10/batch_size_10/data_partition_type_iid/model_type_resnet/major_percent_0.8/n_epochs_1/beta_0.1/pruning_threshold_0.1/SSFLv6/snr_10/compress_4096/channel_type_awgn/seed_0.npz`

## 주요 지표

- 정확도: `10.26%` at the end of the smoke run
- 통신량: `11.03 MB` cumulative communication in the smoke run
- SNR 강건성: multi-SNR evaluation completed and artifact saved
- seed 분산: 이번 범위에서는 측정하지 않음

## 해석

Docker 기반 실행 경로는 이제 실제 GPU를 사용한다. 이 결과는 알고리즘 개선의 증거가 아니라, GPU research harness가 최소 end-to-end 경로에서 동작함을 확인한 것이다.

## 알려진 한계

- 단일 GPU에서 모든 MPI rank가 `cuda:0`를 공유한다
- 다중 seed나 Rayleigh smoke는 아직 수행하지 않았다
- 성능 비교 실험이 아니라 실행 인프라 검증만 수행했다

## 다음 권장 행동

- baseline reproduction 단계에서 이 GPU runtime을 기본 경로로 사용
- 필요하면 rank별 device policy를 별도 실험으로 분리
