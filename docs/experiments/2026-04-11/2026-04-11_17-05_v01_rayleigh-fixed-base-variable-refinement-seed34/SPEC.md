# SPEC

## 문서 및 로그 경로

- 문서 폴더:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_17-05_v01_rayleigh-fixed-base-variable-refinement-seed34`
- 실행 로그:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_17-05_v01_rayleigh-fixed-base-variable-refinement-seed34/RUNLOG.md`
- launcher 로그:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_17-05_v01_rayleigh-fixed-base-variable-refinement-seed34/launcher.log`

## 결과 저장 경로

이번 실행은 기존 후보 아티팩트 루트에 `seed=3,4`를 추가한다.

- 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-fixed-base-variable-refinement`

## 후보 설정

- `algorithm=SSFLv6`
- `base_refinement_enable=1`
- `base_refinement_variable_enable=1`
- `base_support_k=128`
- `refinement_support_k=128`

## 고정 조건

- dataset: `cifar10`
- partition: `class`
- channel: `rayleigh`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`
- `semantic_spreading_enable=0`
- `snr_adaptive_beta_enable=0`
- `semantic_power_enable=0`
- `latent_mixing_enable=0`
- `encoder_downsample_enable=0`
- `semidense_enable=0`
- `support_floor_enable=0`
- `importance_repetition_enable=0`
- `csi_source_mask_enable=0`
- `server_feature_impute_enable=0`

## 실행 seed

- `3`
- `4`

## 검증

코드 변경이 없으므로 새 smoke는 생략한다.

확인 항목:

- `seed_3.npz`, `seed_4.npz` 생성 여부
- 컨테이너 정상 종료 여부
- 이후 baseline / `SC-USFL`와 `seed=3,4` matched summary 산출 가능 여부

## 평가 지표

- final train acc
- total comm
- test `-6 dB`
- test `12 dB`
- best acc

## 성공 기준

이번 단계는 새 개선 주장 단계가 아니다.

성공 조건은 다음 둘뿐이다.

- `seed=3,4` 실행 완료
- matched seed-set 비교가 가능한 상태가 되는 것
