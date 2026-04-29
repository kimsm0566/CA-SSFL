# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_13-03_v01_comm-reduction-followup-rayleigh-awgn`
- 시작 일시: `2026-04-09 13:03 KST`
- 상태: `진행중`
- 담당자: `Codex`

## 목적

`Rayleigh`에서 `SC-USFL` 대비 우위를 확인한 현재 `SSFLv6 candidate`의 통신량을 줄이면서 정확도와 저 SNR 강건성을 최대한 유지하는 설정을 찾고, 선별된 설정을 `AWGN`에서도 재검증한다.

## 배경

- 완료된 `cross-benchmark` 기준으로 `SSFLv6 candidate`는 `SC-USFL`보다:
  - final accuracy mean 우세
  - `-6 dB` mean 우세
  - total comm mean도 소폭 우세
- 그러나 저장소의 1차 목표는 `communication-performance trade-off` 개선이므로, 현재 후보의 comm를 더 낮출 여지가 있는지 확인할 필요가 있다.

## 질문

1. `beta`, `film_max_t`, `film_min_t`를 보수적으로 조정해 `Rayleigh`에서 current candidate보다 통신량을 낮추면서 성능 저하를 제한할 수 있는가?
2. 그렇게 선별된 설정이 `AWGN`에서도 최소한 `SC-USFL` 대비 경쟁력을 유지하는가?

## 실행 범위

### Stage A: Rayleigh 통신량 절감 sweep

- 알고리즘: `SSFLv6`
- 고정:
  - `semantic_spreading_enable=1`
  - `snr_adaptive_beta_enable=1`
  - `semantic_power_enable=0`
- seeds:
  - `1,2`
- sweep 구성 원칙:
  - `beta`는 논문 표기상 해석 가능한 decade 단위만 사용
    - `0.1`, `0.01`, `0.001`, `0.0001`
  - `film_max_t`, `film_min_t`는 `0.1` 단위 쌍만 사용
    - `0.7/0.4`
    - `0.8/0.5`
    - `0.9/0.6`
- 클라이언트 수:
  - `8`
  - 즉 서버 `1`개를 포함한 MPI world size는 `9`

### Stage B: AWGN 재검증

- 대상:
  - Stage A에서 선택된 best config 1개
- 채널:
  - `awgn`
- seeds:
  - `1,2`

## 선택 규칙

Stage A 종료 후 다음 기준으로 best config를 고른다.

1. Rayleigh `seed 1,2` 평균 기준으로
   - final accuracy가 current candidate reference 대비 `1.0%p` 이내
   - `-6 dB` 정확도가 current candidate reference 대비 `1.0%p` 이내
2. 위 조건을 만족하는 후보 중 total comm mean이 가장 작은 설정 채택
3. 조건을 만족하는 후보가 없으면:
   - `final_acc_mean + m6_mean - 0.0002 * comm_mean` 점수가 최대인 설정을 임시 best로 채택
   - 이 경우 결과는 `exploratory`로 표시

## 산출물

- Stage A/B 실행 로그
- 선택 요약
- 결과 파일
- 최종 `RESULT.md`
