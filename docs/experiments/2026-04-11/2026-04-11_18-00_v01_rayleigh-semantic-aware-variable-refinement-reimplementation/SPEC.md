# SPEC

## 실험 이름

`Rayleigh semantic-aware variable refinement reimplementation`

## 목적

직전 variable refinement 구현에서 확인된 두 문제를 바로잡는다.

1. `base`가 `semantic_candidate_mask`를 무시하던 문제
2. `refinement`가 `channel score` 위주로 선택되던 문제

## 비교 대상

### 주 baseline

- `CA-SSFL Orig`

### 부 baseline

- 직전 `fixed base + variable refinement`
  - `base_support_k=128`
  - `refinement_support_k=128`
  - `base_refinement_variable_enable=1`

## 고정 조건

- dataset: `cifar10`
- partition: `class`
- channel: `rayleigh`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `algorithm=SSFLv6`
- `model_type=resnetv2`
- `compressed_dim=4096`
- `beta=0.01`
- `pruning_threshold=1.0`
- `film_max_t=0.7`
- `film_min_t=0.4`

## 구현 규칙

### semantic score

- `semantic_scores = kl_mean_batch`

### semantic candidate mask

- `semantic_candidate_mask = vib_mask > 0`

### channel score

- `channel_scores = film_mask[0]`

### channel candidate mask

- `channel_candidate_mask = chan_mask > 0`

## base selection

### rule

- base는 `semantic_candidate_mask` 내부에서만 선택한다
- 점수는 `semantic_scores`
- `K_base = 128`

### fallback

- `semantic_candidate_mask` 내부 유효 차원이 `128`보다 적으면
- 부족분은 남은 전체 차원 중 `semantic_scores` 상위로 보충한다

## refinement selection

### candidate set

- 기본 candidate는 다음을 모두 만족하는 차원
  - base에 포함되지 않음
  - `semantic_candidate_mask = 1`
  - `channel_candidate_mask = 1`

### score

- refinement mixed score:
  - `semantic_scores_norm * 0.5 + channel_scores_norm * 0.5`

정규화는 각각 현재 벡터에서 min-max normalization으로 한다.

### fallback

- 위 candidate set이 비면
- base 제외 차원 중 `semantic_candidate_mask` 내부에서 mixed score 상위로 선택
- 그것도 비면 base 제외 전체 차원에서 mixed score 상위로 선택

## refinement budget

- `K_ref_max = 128`
- `K_ref = round(K_ref_max * snr_normalized)`
- `snr_normalized = (current_snr_db - (-5)) / (15 - (-5))`
- 최종 `K_ref`는 candidate 유효 개수와의 `min`

## 최종 mask

- `final_support = base_support U refinement_support`

## 로깅

기존 로그를 유지하되 다음을 반드시 출력한다.

- `Active`
- `Base`
- `Refinement`

필요 시 추가:

- `BaseFallback`
- `RefineFallback`

## 결과 경로

새 slug를 사용한다.

- 문서 경로:
  - `/home/sunmin/SFL_Semantic/docs/experiments/2026-04-11/2026-04-11_18-00_v01_rayleigh-semantic-aware-variable-refinement-reimplementation`
- 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-semantic-aware-variable-refinement-reimplementation`
- smoke 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-semantic-aware-variable-refinement-reimplementation-smoke`

## 검증 단계

### static

- `python -m py_compile` on touched python files

### smoke

- Docker GPU `1-round smoke`
- baseline과 candidate 둘 다

### exploratory

- `seed 1,2`

### extension gate

아래를 만족하면 `seed 3,4` 확장:

- 직전 variable refinement 대비 final acc 비열화
- 직전 variable refinement 대비 `-6 dB` 개선 또는 비열화
- baseline 대비 comm 절감 유지
