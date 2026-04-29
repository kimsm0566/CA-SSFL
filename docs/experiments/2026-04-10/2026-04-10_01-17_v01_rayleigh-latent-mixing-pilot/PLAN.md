# 실험 계획

## 메타데이터

- 실험 id: `2026-04-10_01-17_v01_rayleigh-latent-mixing-pilot`
- 시작 일시: `2026-04-10 01:17 KST`
- 상태: `planned`
- 담당자: `Codex`

## 배경

`CA-SSFL New`로 시도했던 `semantic spreading + SNR-adaptive beta`는 `Rayleigh`, `n_clients=8` 재실행에서 `CA-SSFL Orig` 대비 정확도 이득을 재현하지 못했고, 통신량만 증가했다. 따라서 다음 개입은 전송 직전 spreading이 아니라, 인코더가 더 분산된 latent를 직접 학습하도록 유도하는 쪽으로 전환한다.

## 핵심 가설

인코더 내부에 약한 `latent mixing`을 넣으면, 동일한 전송 예산 안에서도 semantic information이 특정 좌표에 과도하게 몰리지 않고 여러 좌표에 분산된다. 그러면 `Rayleigh` deep fade에서 일부 좌표가 흔들려도 전체 semantic 정보가 완전히 붕괴하지 않아 `CA-SSFL Orig` 대비 강건성이 개선될 수 있다.

## 질문

1. `CA-SSFL Orig` 위에 작은 `latent mixing`을 추가하면 `Rayleigh`에서 final accuracy와 저 SNR 정확도가 올라가는가?
2. 같은 `compressed_dim=4096`과 동일한 masking 정책에서 통신량 증가는 제한적인가?
3. mixing strength가 약할 때와 강할 때 중 어느 구간이 안정적인가?

## 실행 범위

- 채널:
  - `rayleigh`
- 알고리즘:
  - `SSFLv6` (`CA-SSFL Orig` 기반)
- exploratory seed set:
  - `1,2`
- latent mixing strength:
  - `0.1`
  - `0.25`
  - `0.5`
- latent mixing groups:
  - `8`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- compressed_dim: `4096`
- beta: `0.01`
- pruning_threshold: `1.0`
- film_max_t: `0.7`
- film_min_t: `0.4`
- `semantic_spreading_enable=0`
- `snr_adaptive_beta_enable=0`
- `semantic_power_enable=0`
- Docker GPU runtime 사용

## 비교 기준

- baseline:
  - `2026-04-09_20-05_v01_rayleigh-cross-benchmark-nclients8`의 `CA-SSFL Orig`
- candidate:
  - baseline + `latent_mixing_enable=1`

## 성공 기준

- seed `1,2` 기준으로 최소 1개 mixing strength가 baseline 대비
  - final accuracy 열세가 `0.5%p` 이내이고
  - `-6 dB` 정확도가 개선되거나 유지되고
  - 통신량 증분이 과도하지 않음
- 위 조건을 만족하는 strength가 있으면 다음 단계로 claim용 seed `1,2,3,4` 확장 검토

## 실패 시 다음 방향

- 이번 pilot에서 이득이 없으면 다음 후보는 `semi-dense bottleneck`으로 전환한다.
