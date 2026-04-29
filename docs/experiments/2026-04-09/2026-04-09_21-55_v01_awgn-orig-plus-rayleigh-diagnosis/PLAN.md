# 실험 계획

## 메타데이터

- 실험 id: `2026-04-09_21-55_v01_awgn-orig-plus-rayleigh-diagnosis`
- 시작 일시: `2026-04-09 21:55 KST`
- 상태: `planned`
- 담당자: `Codex`

## 목적

1. `AWGN n_clients=8`에서 빠져 있던 `CA-SSFL Orig`를 추가 측정해, `Orig`와 `New`를 같은 채널/같은 client count에서 직접 비교한다.
2. `Rayleigh n_clients=8`에서 `CA-SSFL New`가 `Orig`보다 나빠진 이유를 수치적으로 진단한다.

## 질문

1. `AWGN n_clients=8`에서 `CA-SSFL Orig`와 `CA-SSFL New`의 정확도/통신량 차이는 무엇인가?
2. `Rayleigh n_clients=8`에서 `Orig -> New` 전환이 final acc, `-6 dB`, round-wise learning curve, round-wise communication에 어떤 변화를 만들었는가?
3. 현재 `Orig/New` 차이가 “통신량 증가 대비 성능 이득 부재”인지, 아니면 “학습 안정성 악화”에 가까운지 구분할 수 있는가?

## 실행 범위

- 실행:
  - `AWGN`, `CA-SSFL Orig`, seed `1,2,3,4`
- 분석:
  - `Rayleigh n_clients=8`, `CA-SSFL Orig` vs `CA-SSFL New`

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- Docker GPU runtime 사용

## 산출물

- AWGN 결과 루트:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-09-awgn-threeway-benchmark-nclients8`
- 진단 문서:
  - `RESULT.md`
- 진단 요약 json:
  - `rayleigh_orig_vs_new_diagnosis.json`

## 성공 기준

- `AWGN`에서 `CA-SSFL Orig` seed `1,2,3,4` 완료
- 통합 그래프에 `AWGN Orig/New` 둘 다 표시 가능
- `Rayleigh Orig/New` 차이를 final, low-SNR, round-wise 기준으로 요약
