# 실험 계획

## 메타데이터

- 실험 id: `2026-04-10_01-28_v01_rayleigh-semidense-pilot`
- 시작 일시: `2026-04-10 01:28 KST`
- 상태: `planned`
- 담당자: `Codex`

## 배경

`latent mixing`은 같은 전송 예산에서 표현을 덜 brittle하게 만들기 위한 1순위 개입이다. 만약 이 개입이 `Rayleigh`에서 baseline 대비 이득을 만들지 못하면, 다음 후보는 전송량 `K`는 유지하되 selected support를 그룹 단위로 더 고르게 퍼뜨리는 `semi-dense bottleneck`이다.

## 핵심 가설

현재 `CA-SSFL Orig`는 active support가 일부 좌표/영역에 과도하게 몰려 deep fade에 취약할 수 있다. 같은 active budget `K`를 유지하면서도 support를 그룹 단위로 분산시키면, 좌표 단위 failure에 대한 민감도가 낮아져 `Rayleigh`에서 강건성이 개선될 수 있다.

## 질문

1. 같은 `K`를 유지한 group-balanced support selection이 baseline 대비 `-6 dB` 성능을 올리는가?
2. group granularity와 per-group top-k 중 어느 설정이 가장 안정적인가?
3. 통신량을 사실상 유지한 상태에서 final accuracy 손실 없이 robustness를 얻을 수 있는가?

## 실행 범위

- 채널:
  - `rayleigh`
- 알고리즘:
  - `SSFLv6` (`CA-SSFL Orig` 기반)
- exploratory seed set:
  - `1,2`
- semi-dense configs:
  - `group_size=16`, `group_topk=4`
  - `group_size=16`, `group_topk=8`
  - `group_size=32`, `group_topk=8`

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
- `latent_mixing_enable=0`
- Docker GPU runtime 사용

## 실행 조건

- 기본 규칙:
  - `latent mixing pilot`에서 baseline 대비 명확한 이득이 없을 때만 실행
- 자동 후속:
  - latent pilot 완료 후 자동 판정
  - 이득 없음 판정 시 즉시 본 pilot 시작

## 성공 기준

- seed `1,2` 기준으로 최소 1개 semi-dense config가 baseline 대비
  - final accuracy 열세가 `0.5%p` 이내이고
  - `-6 dB` 정확도가 개선되거나 유지되고
  - 통신량 증분이 미미함

## 실패 시 다음 방향

- semi-dense도 이득이 없으면 다시 representation-level 개입 또는 channel-aware objective 자체를 재설계한다.
