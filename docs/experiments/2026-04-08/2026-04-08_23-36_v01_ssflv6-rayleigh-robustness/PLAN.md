# 실험 계획

## 메타데이터

- 실험 id: `2026-04-08_23-36_v01_ssflv6-rayleigh-robustness`
- 초안 일시: `2026-04-08 23:36 KST`
- 상태: `검토중`
- 담당자: `Codex`

## 목표

`SSFLv6` 계열의 `CA-SSFL`가 `Rayleigh` 채널에서 `SC-USFL` 대비 강건성이 크게 떨어지는 원인을 분리해서 확인하고, 통신량 증가 없이 강건성을 보완할 수 있는 1차 개입 후보를 우선순위대로 검증한다.

## 지금 하는 이유

- 현재 관찰된 문제는 accuracy 단독 문제가 아니라 communication-performance frontier의 핵심 병목이다.
- 특히 `Rayleigh`에서의 취약성이 구조적이면, `AWGN`에서의 단일 이득만으로는 방법론 주장을 방어하기 어렵다.
- 사용자가 이미 세 가지 개입 아이디어를 제안했으므로, 지금은 임의 구현보다 원인-대응 매핑을 명확히 한 실험 설계가 우선이다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/trainer.py`
  - `src/models/model.py`
  - 필요 시 `src/utils/option.py`
- 의도한 동작 변화:
  - `SSFLv6`의 활성 semantic feature 전송 직전/직후에 `Rayleigh` 강건성 보강 기법을 삽입한다.
  - 첫 구현은 통신량 증가가 없는 방식만 다룬다.
- 유지할 조건:
  - 기준선 설정은 현재 canonical provisional setting을 유지한다.
  - `dataset=cifar10`, `partition_type=class`, `channel_type=rayleigh`, `n_clients=9`, `n_client_data=3000`, `batch_size=100`, `n_epochs=1`, `n_rounds=200`, `compressed_dim=4096`, `beta=0.0005`, `pruning_threshold=1.0`
  - 결과 비교 시 기존 `.npz` 저장 스키마와 plotting 경로를 불필요하게 바꾸지 않는다.

## 후보 접근법

- 접근 A: `Sliced Feature Spreading`
  - 활성 좌표 `K`개를 전송 직전 고정 직교 변환으로 섞고, 서버에서 역변환 후 zero-fill 복원한다.
  - 첫 구현은 step별 랜덤 행렬 대신 `K`별 고정 transform을 사용한다.
  - 기대 효과:
    - 특정 semantic coordinate failure를 전체 좌표로 분산
    - `Rayleigh + ZF`에서의 국소 치명타를 완화
- 접근 B: `Semantic Power Water-filling`
  - 활성 좌표별 중요도에 따라 전력을 재배분하되 총 전력은 유지한다.
  - 첫 구현은 `KL` 기반 soft weighting만 허용하고, hard boost는 피한다.
  - 기대 효과:
    - 중요한 좌표의 post-channel survivability 향상
- 접근 C: `SNR-aware Reparameterization`
  - 저 SNR일수록 VIB sampling noise를 키워 강건한 latent margin을 유도한다.
  - 기대 효과:
    - representation 자체의 channel tolerance 향상
  - 우려:
    - direct channel protection이 아니라 regularization 강화에 가까워 정확도 회귀 위험이 큼
- 우선 접근법과 그 이유:
  - 1순위 `접근 A`
  - 2순위 `접근 B`
  - 3순위 `접근 C`
  - 이유:
    - 현재 가설상 주원인은 `redundancy 부족 + hard masking + zero-fill 복원 + Rayleigh block fading + ZF noise amplification` 조합이다.
    - `접근 A`가 이 병목에 가장 직접적으로 대응하고, 통신량 증가 없이 dense-like robustness를 모사할 가능성이 가장 높다.
    - `접근 B`는 구현이 단순하고 ablation 가치가 크다.
    - `접근 C`는 간접적이며 실패 모드가 더 많다.

## 계획된 검증

- 스모크 체크:
  - 단계 0: 코드 정적 검증 `python -m py_compile`
  - 단계 1: `1` round 또는 `5` round MPI smoke로 학습/역전파/저장 경로가 유지되는지 확인
- 비교 대상:
  - 기준선 1: `SSFLv6`
  - 기준선 2: `SC-USFL`
  - 진단 비교: `SSFLv6_w_o_vib`, 필요 시 `SSFLv6_w_o_film`
- 예상 산출물 경로:
  - 계획 문서: `docs/experiments/2026-04-08_23-36_v01_ssflv6-rayleigh-robustness/`
  - 실험 결과: 같은 폴더 하위 `artifacts/`

## 리스크와 열린 질문

- 기술적 리스크:
  - `K`가 batch마다 달라지는 구조에서 spreading transform 적용 위치와 shape 관리가 복잡할 수 있다.
  - transform이 decoder 복원 가정과 충돌하면 accuracy가 급락할 수 있다.
  - power weighting이 현재 채널 정규화 로직과 상쇄되거나 예상과 다르게 동작할 수 있다.
- 평가상 리스크:
  - 짧은 smoke run의 개선은 claim이 아니다.
  - `SC-USFL`와의 비교는 동일 seed와 full budget에서 다시 맞춰야 한다.
- 검토가 필요한 질문:
  - 1차 목표를 `SC-USFL` 추격으로 둘지, `SSFLv6` baseline 대비 Rayleigh robustness 회복으로 둘지
  - `접근 A`의 고정 transform 후보를 `Hadamard`류로 볼지, `DCT`류로 볼지
  - 1차 smoke에서 `200` rounds가 아닌 축약 budget을 어디까지 허용할지

## 사용자 검토 메모

- 피드백:
  - 사용자 제안:
    - `Sliced Feature Spreading`
    - `SNR-aware Reparameterization`
    - `Semantic Power Water-filling`
- 합의된 결정:
  - 먼저 계획 문서를 만들고, 승인 후 `SPEC.md`를 고정한다.
  - 초기 우선순위는 `A > B > C`로 둔다.
- 남은 쟁점:
  - 첫 구현 대상을 `A` 단독으로 할지, `A+B`까지 한 번에 묶을지

## 실행 게이트

- 구현 시작 가능?: `아니오`
- 아니라면 먼저 명확히 할 점:
  - 이 `PLAN.md`에 대한 사용자 승인
  - 승인 후 `SPEC.md`에 1차 구현 범위를 `접근 A 단독`으로 고정할지 여부
