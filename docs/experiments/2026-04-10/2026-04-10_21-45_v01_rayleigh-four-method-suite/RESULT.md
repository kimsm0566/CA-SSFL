# 실험 결과

## 메타데이터

- 실험 id: `2026-04-10_21-45_v01_rayleigh-four-method-suite`
- 종료 일시: `2026-04-10 22:54 KST`
- 상태: 완료
- 담당자: Codex

## 요약

`Rayleigh`, `n_clients=8`, `seed 1,2` 조건에서 방법 `1,2,3,4`를 같은 suite로 재실행한 결과, baseline `CA-SSFL Orig`를 명확히 이긴 방법은 없었다. `1`은 baseline과 사실상 동일했고, `2`는 거의 같은 통신량에서 정확도가 소폭 하락했다. `3`은 통신량을 줄였지만 정확도도 같이 하락했고, `4`는 통신량 절감은 컸지만 정확도 붕괴가 커서 현재 설정으로는 사용하기 어렵다.

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- algorithm: `SSFLv6`
- channel_type: `rayleigh`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- beta: `0.01`
- pruning_threshold: `1.0`
- film_max_t / film_min_t: `0.7 / 0.4`
- compressed_dim: `4096`
- seed_set: `1,2`

## 결과 요약

| 방법 | 설정 | final acc mean | total comm mean (MB) | 해석 |
| --- | --- | ---: | ---: | --- |
| Baseline | `CA-SSFL Orig` | `41.91` | `19608.50` | 기준선 |
| 1 | `semi-dense g32,k8` | `41.91` | `19608.50` | baseline과 사실상 동일 |
| 2 | `latent mixing s=0.1` | `41.30` | `19582.91` | 통신량은 거의 같고 정확도 소폭 하락 |
| 3 | `support floor min_active=256, snr<=0dB` | `40.39` | `18701.54` | comm 절감은 있으나 정확도 손실 동반 |
| 4 | `semantic power alpha=2.0` | `34.78` | `10939.88` | comm 절감은 크지만 정확도 붕괴 |

## seed별 결과

### Baseline

- `seed 1`: final acc `41.85`, comm `18826.68 MB`
- `seed 2`: final acc `41.97`, comm `20390.32 MB`

### 방법 1: Semi-dense

- `seed 1`: final acc `41.85`, comm `18826.68 MB`
- `seed 2`: final acc `41.97`, comm `20390.32 MB`

### 방법 2: Latent mixing

- `seed 1`: final acc `41.33`, comm `20211.46 MB`
- `seed 2`: final acc `41.27`, comm `18954.36 MB`

### 방법 3: Support floor

- `seed 1`: final acc `39.55`, comm `19037.19 MB`
- `seed 2`: final acc `41.23`, comm `18365.89 MB`

### 방법 4: Semantic power

- `seed 1`: final acc `36.37`, comm `10827.93 MB`
- `seed 2`: final acc `33.19`, comm `11051.83 MB`

## 해석

1. `1번`은 현재 구현/설정으로는 baseline과 동일하다.
2. `2번`은 representation을 약하게 섞는 것만으로는 Rayleigh 강건성 개선을 만들지 못했다.
3. `3번`은 방향 자체는 유효하다. low-SNR에서 minimum support를 보장하면서도 평균 통신량을 줄이는 결과가 나왔지만, 현재 floor 설정이 너무 공격적이라 정확도 손실이 있다.
4. `4번`은 `alpha=2.0`이 너무 강했다. 중요한 좌표 보호보다 전력 집중이 과도해져 전체 분류 성능이 크게 무너졌다.

## 결정

- `1번`: 중단
- `2번`: 중단
- `3번`: 보수적 설정으로 재탐색
- `4번`: low-alpha 설정으로 재탐색

## 산출물

- 결과 루트: `/home/sunmin/SFL_Semantic/tmp/2026-04-10-rayleigh-four-method-suite`
- 실행 로그: [RUNLOG.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-10_21-45_v01_rayleigh-four-method-suite/RUNLOG.md)
- launcher 로그: [launcher.log](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-10_21-45_v01_rayleigh-four-method-suite/launcher.log)
