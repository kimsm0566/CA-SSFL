# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_16-55_v01_autonomous-followup`
- 시작 일시: `2026-04-09 16:55 KST`
- 상태: `진행중`
- 담당자: `Codex`

## 목적

사용자가 자는 동안 `cross-benchmark` 결과를 자동으로 집계하고, 결과에 따라 다음 단계를 이어서 수행한다.

## 자동 의사결정 규칙

1. 현재 `cross-benchmark` 큐가 끝날 때까지 대기
2. `Rayleigh`에서 `SSFLv6 candidate`와 `SC-USFL`를 `seed 1,2,3,4` 기준으로 비교
3. 만약 `SSFLv6 candidate`가 `SC-USFL`를 종합적으로 이기지 못하면:
   - 1차: `candidate`의 통신량 절감 sweep 수행
   - 2차: 그래도 부족하면 `semantic power allocation` 아이디어를 exploratory로 추가

## 종합 비교 기준

다음 조건을 모두 만족해야 `SC-USFL` 대비 우세로 본다.

- final accuracy mean 우세
- `-6 dB` mean 우세
- total comm mean이 `SC-USFL` 이하

이 셋 중 하나라도 충족하지 못하면 후속 개선 단계로 진입한다.

## 후속 개선 단계

### Stage A: 통신량 절감 sweep

- 대상: `SSFLv6 candidate`
- 채널: `rayleigh`
- seed: `1,2`
- 튜닝 변수:
  - `beta`
  - `film_max_t`
  - `film_min_t`

### Stage B: 새 아이디어

- 아이디어: `KL` 기반 `semantic power allocation`
- 목적:
  - `spreading + snr-adaptive beta`의 정확도/강건성 이득을 유지하면서 통신량 불리함을 완화할 후보 탐색

## 산출물

- 자동 진행 로그
- 집계 요약
- Stage A/B 결과 파일
