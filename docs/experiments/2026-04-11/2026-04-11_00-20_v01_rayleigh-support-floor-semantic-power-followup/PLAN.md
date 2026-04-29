# 실험 계획

## 메타데이터

- 실험 id: `2026-04-11_00-20_v01_rayleigh-support-floor-semantic-power-followup`
- 초안 일시: `2026-04-11 00:20 KST`
- 상태: 승인
- 담당자: Codex

## 목표

`1~4` suite 이후 살아남은 두 방향, 즉 `3번 support floor`와 `4번 semantic power`를 더 보수적인 설정으로 다시 실행해서, 정확도 손실 없이 통신량을 줄일 수 있는지 확인한다.

## 지금 하는 이유

직전 suite에서 `1,2`는 사실상 실패했다. 반면 `3`은 방향성은 괜찮지만 floor가 과했고, `4`는 alpha가 너무 커서 과집중으로 보이는 붕괴가 뚜렷했다. 따라서 다음 우선순위는 representation 개입이 아니라 보호 메커니즘의 보수적 재설계다.

## 제안 변경사항

- 대상 코드 경로:
  - `scripts/`
  - `docs/experiments/`
- 의도한 동작 변화:
  - 새 코드 변경 없이 기존 옵션만 더 보수적으로 sweep한다.
- 유지할 조건:
  - `cifar10`, `class`, `rayleigh`, `n_clients=8`, `seed 1,2`

## 후보 접근법

- 접근 A:
  - `support floor`를 더 낮은 floor와 더 낮은 trigger SNR에만 적용
- 접근 B:
  - `semantic power`를 low-alpha로 재실행
- 우선 접근법과 그 이유:
  - 둘 다 같은 follow-up queue로 묶어 실행

## 계획된 검증

- 스모크 체크:
  - 없음. 기존 코드 경로와 옵션만 재사용
- 비교 대상:
  - `CA-SSFL Orig`
  - 직전 suite의 `support floor 256@0dB`, `semantic power alpha=2.0`
- 예상 산출물 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-rayleigh-support-floor-semantic-power-followup`

## 리스크와 열린 질문

- 기술적 리스크:
  - 너무 약하게 조정하면 baseline과 차이가 거의 없어질 수 있음
- 평가상 리스크:
  - `seed 1,2`만으로는 아직 exploratory
- 검토가 필요한 질문:
  - 없음

## 사용자 검토 메모

- 피드백:
  - 사용자가 결과 정리와 함께 다음 두 방향도 바로 진행하길 요청함
- 합의된 결정:
  - `3`, `4` 두 방향을 동시에 후속 실행
- 남은 쟁점:
  - 없음

## 실행 게이트

- 구현 시작 가능?: 예
- 아니라면 먼저 명확히 할 점:
  - 없음
