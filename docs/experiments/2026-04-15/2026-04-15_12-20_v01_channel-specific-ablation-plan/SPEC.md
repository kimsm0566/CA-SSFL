# 채널별 대표 설정 기반 CA-SSFL Ablation 실행 스펙

## 목적

기존에 확보된 채널별 best `CA-SSFL` baseline artifact를 기준으로 `w/o VIB`, `w/o FiLM`만 새로 실행해, 각 채널에서 핵심 구성요소 기여도를 분해한다.

## 비교 기준 baseline artifact

### AWGN baseline

- result root: `/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`
- fixed setting:
  - `algorithm=SSFLv6`
  - `beta=0.05`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.2`

### Rayleigh baseline

- result root: `/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`
- fixed setting:
  - `algorithm=SSFLv6`
  - `beta=0.1`
  - `pruning_threshold=1.0`
  - `film_max_t=0.7`
  - `film_min_t=0.4`

## 새로 실행할 ablation

- `SSFLv6_w_o_vib`
- `SSFLv6_w_o_film`

## 공통 고정 조건

- dataset: `cifar10`
- partition type: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `major_percent=0.8`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `semantic_spreading=0`
- `snr_adaptive_beta=0`
- `semantic_power=0`
- `latent_mixing=0`
- `encoder_downsample=0`
- `semidense=0`
- `support_floor=0`
- `importance_repetition=0`
- `base_refinement=0`
- `csi_source_mask=0`
- `server_feature_impute=0`
- `train_snr=10`
- seeds: `1,2,3,4`

## 채널별 고정 하이퍼파라미터

### AWGN

- `beta=0.05`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.2`

### Rayleigh

- `beta=0.1`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 실행 매트릭스

- `AWGN`
  - `SSFLv6_w_o_vib`, seeds `1,2,3,4`
  - `SSFLv6_w_o_film`, seeds `1,2,3,4`
- `Rayleigh`
  - `SSFLv6_w_o_vib`, seeds `1,2,3,4`
  - `SSFLv6_w_o_film`, seeds `1,2,3,4`

총 실행 수:

- `2 channels x 2 methods x 4 seeds = 16 runs`

## 예상 시간

- run당 약 `7~8분`
- 총 약 `2시간 ~ 2시간 20분`

## 시간 추정 전제

- 기존 `cifar10` benchmark와 동일한 Docker GPU runtime 사용
- artifact 저장 후 non-zero exit가 나와도 artifact가 존재하면 성공으로 간주
- 중간 stall 없이 순차 실행된다는 가정

## 결과 루트

- container:
  - `/workspace/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation`
- host:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation`

## 검증

실행 전:

- 러너 `bash -n`

실행 후:

- `16`개 `seed_*.npz` 존재 확인
- baseline artifact와 결합해 `Acc`, `Comm`, `-6 dB` 비교표 생성

## 비교 규칙

- baseline `CA-SSFL`는 재실행하지 않는다.
- 새 결과는 반드시 기존 baseline artifact와 같은 seed set `1,2,3,4` 기준으로 비교한다.
- claim은 baseline보다의 상대 변화와 `-6 dB` 강건성까지 함께 보고한다.

