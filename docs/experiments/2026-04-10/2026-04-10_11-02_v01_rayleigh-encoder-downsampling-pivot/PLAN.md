# 실험 계획

## 메타데이터

- 실험 id: `2026-04-10_11-02_v01_rayleigh-encoder-downsampling-pivot`
- 시작 일시: `2026-04-10 11:02 KST`
- 상태: `planned`
- 담당자: `Codex`

## 배경

지금까지 `Rayleigh` 강건성 개선을 위해 시도한 개입은 다음 두 축이었다.

- 전송 직전 개입:
  - `semantic spreading`
  - `semantic power`
- 표현 보조 개입:
  - `latent mixing`
  - `semi-dense support balancing`

하지만 `n_clients=8`, `Rayleigh` 기준 재실행에서는 `CA-SSFL Orig`를 확실히 이기는 개선안이 아직 나오지 않았다. 특히 `latent mixing`과 `semi-dense`는 현재 구현 기준으로 baseline 대비 강한 개선 신호를 만들지 못하고 있다.

이번에는 문제를 transmission head가 아니라 **encoder representation 구조 자체**에서 다시 본다. 현재 `FiLMChannelAwareEncoder`는 stride를 모두 `1`로 유지해 `8x8` spatial map을 거의 그대로 latent `4096 = 64 x 8 x 8`에 펼친다. 이 구조는 semantic feature를 지나치게 spatially disentangled, axis-aligned하게 만들 수 있고, 그 결과 `Rayleigh` deep fade에서 일부 좌표 손상에 취약할 수 있다.

## 핵심 가설

인코더가 DeepJSCC / SC-USFL 쪽처럼 **중간 단계에서 downsampling을 수행하도록** 바뀌면, feature mixing이 구조적으로 강제된다. 그러면 semantic information이 더 distributed하게 표현되어, 현재와 같은 low-redundancy / brittle latent보다 `Rayleigh`에서 더 강건한 표현을 만들 수 있다.

## 질문

1. `8x8` spatial map을 그대로 유지하는 현재 encoder 대신, 일부 stride를 복원해 `4x4` 또는 그에 준하는 bottleneck mixing을 유도하면 `Rayleigh` final accuracy와 `-6 dB` 정확도가 개선되는가?
2. 같은 `compressed_dim=4096`을 유지하더라도, encoder 내부 downsampling만으로 robustness 이득이 생기는가?
3. 이득이 있다면 그 원인은
   - 더 distributed한 latent
   - low-SNR 좌표 손상 민감도 감소
   - active support 안정화
   중 어느 쪽에 가까운가?

## 문제 재정의

현재 `CA-SSFL`의 핵심 문제를 다음과 같이 본다.

- semantic selection 이전에 만들어지는 latent representation이 너무 spatially disentangled하다
- stride를 모두 제거한 encoder 구조가 좌표별 독립성을 키운다
- 그 결과 `Rayleigh`에서 일부 좌표 손상이 semantic failure로 바로 이어진다

즉, 이번 실험의 초점은

`전송 직전 보정이 아니라, 인코더가 처음부터 더 섞인 latent를 만들게 하는 구조적 개입`

이다.

## 제안하는 개입

### 1차 후보: Encoder Downsampling Variant

- `FiLMChannelAwareEncoder`의 일부 conv stride를 `1 -> 2`로 복원
- spatial resolution을 `8x8 -> 4x4`로 줄이는 mixing path 도입
- 이후 projection head로 다시 `compressed_dim=4096` latent로 매핑
- 나머지 학습/마스킹/통신 로직은 최대한 baseline 유지

핵심 의도:

- spatial mixing은 늘리되
- `CA-SSFL`의 masking / VIB / FiLM 프레임은 유지
- 비교 기준을 흐리지 않는 최소 구조 변경으로 시작

### 2차 후보: More Aggressive Bottleneck

1차가 의미 있는 신호를 주면 다음 단계에서 검토한다.

- 더 작은 spatial bottleneck
- projection head depth 조정
- decoder와의 구조 정합 조정

이번 계획에서는 여기까지는 가지 않는다.

## 실행 범위

- 채널:
  - `rayleigh`
- 알고리즘:
  - `SSFLv6` (`CA-SSFL Orig` 기반)
- 우선 비교:
  - `CA-SSFL Orig`
  - `CA-SSFL + encoder downsampling variant`
- exploratory seed set:
  - `1,2`

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

## 비교 원칙

- baseline은 기존 `Rayleigh n_clients=8`의 `CA-SSFL Orig`
- 다른 하이퍼파라미터는 고정
- encoder 구조만 바꾼다
- 결과 해석은 accuracy와 communication cost를 같이 본다

## 성공 기준

1차 exploratory 기준:

- seed `1,2` 평균에서 baseline 대비
  - final accuracy 개선 또는 열세가 `0.5%p` 이내
  - `-6 dB` accuracy 개선
  - 통신량 증가가 제한적

이 신호가 보이면 claim용 seed `1,2,3,4` 확장 검토

## 실패 기준

다음 중 하나면 1차 후보를 실패로 본다.

- final accuracy와 `-6 dB`가 모두 baseline보다 낮음
- 통신량만 늘고 robustness 이득이 없음
- 구조 변경으로 학습 안정성이 악화됨

## 검증 포인트

- active feature count 분포가 baseline 대비 달라지는지
- low-SNR 구간에서 `-6 dB`, `-4 dB`가 먼저 반응하는지
- encoder downsampling이 decoder와 정합 문제를 일으키지 않는지

## 다음 단계

- 이 계획 승인 후 `SPEC.md`에서
  - 정확히 어떤 stride를 복원할지
  - projection head를 어떻게 둘지
  - smoke 조건과 exploratory 실행 매트릭스를
  고정한다.
