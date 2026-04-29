# 2026-04-15 v01 w/o channel mask only ablation plan

## 메타데이터

- 실험 id: `2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan`
- 문서 폴더: `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/`
- 초안 일시: `2026-04-15 18:15 KST`
- 상태: `초안`
- 담당자: `Codex`

## 목표

논문 Table II 하단의 `w/o Channel Masking`을 코드 기준으로 더 정확하게 재현한다.

핵심은:

- `semantic mask`는 유지
- `VIB/KL loss`는 유지
- encoder 내부 `FiLM` gating은 유지
- 최종 전송 support를 만드는 `SNR-driven channel mask`만 비활성화

하는 공정한 단일 ablation을 정의하고 실행 준비를 마치는 것이다.

## 지금 하는 이유

현재 저장된 `SSFLv6_w_o_film` 결과는 사용 가능한 참고 결과이긴 하지만, 엄밀히는 `w/o channel mask only`가 아니다.

코드상:

- `SSFLv6_w_o_film`은 trainer에서 `chan_mask = ones`로 만들어 최종 channel mask를 끄고
- 동시에 encoder 내부에서 `self.use_film = False`가 되어 FiLM gating 자체도 비활성화된다

즉 기존 결과는 `channel mask 제거 + encoder FiLM gating 제거`가 함께 들어간 stronger ablation이다.

반면 사용자가 원하는 것은:

- `threshold 0/1` 조절이 아니라
- `semantic mask`와는 별개인 `channel mask`만 끄는 실험

이다.

## 제안 변경사항

- 대상 코드 경로:
  - `src/utils/option.py`
  - `src/run_exp_main.py`
  - `src/utils/trainer.py`
  - `src/utils/eval.py`
- 의도한 동작 변화:
  - `channel mask only off` 전용 제어 인자를 추가한다
  - 이 인자가 켜지면 최종 support selection에서만 `chan_mask = ones`를 사용한다
  - encoder 내부 `FiLM` generator 및 `mu/log_var`에 적용되는 gating은 그대로 유지한다
- 유지할 조건:
  - `SSFLv6` backbone / split 구조
  - `VIB` parameterization
  - `KL loss`
  - stochastic sampling
  - decoder / classifier / communication accounting
  - 기존 channel-specific best hyperparameter
  - `src/models/model.py`는 수정하지 않는다

## 후보 접근법

- 접근 A:
  - 새 CLI 플래그 추가
  - 예: `--channel_mask_allpass_enable=1`
  - 장점: 의미가 명확하고 재현성이 좋다
  - 장점: `w_o_film`와 혼동되지 않는다
  - 단점: `option.py`, `run_exp_main.py`까지 수정 범위가 늘어난다
- 접근 B:
  - 최소 하드코딩 분기
  - trainer/eval에서만 `chan_mask = ones`를 강제
  - 장점: 수정 범위가 가장 작다
  - 장점: `model.py`와 기존 encoder 구조를 그대로 둔다
  - 단점: 결과를 다시 재현할 때 제어 방식이 덜 명시적일 수 있다
- 우선 접근법과 그 이유:
  - `접근 A`
  - 이유: 기본 동작을 전혀 바꾸지 않으면서 exact ablation을 명시적으로 재현할 수 있다
  - 구현 시에도 `model.py`는 건드리지 않고 최종 `chan_mask`에만 스위치를 걸 수 있다

## 실험 정의

### baseline 재사용

- `CA-SSFL`
  - AWGN: `beta=0.05`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.2`
  - Rayleigh: `beta=0.1`, `pruning_threshold=1.0`, `film_max_t=0.7`, `film_min_t=0.4`

### 기존 proxy 결과 재사용

- `SSFLv6_w_o_film`
  - 해석: `w/o channel mask only`의 exact 결과가 아니라 stronger proxy
  - 용도: 새 exact ablation과의 차이 확인

### 새로 실행할 exact ablation

- `SSFLv6 + --channel_mask_allpass_enable=1`
- 의미:
  - semantic mask 유지
  - final `chan_mask`만 all-ones
  - encoder-side FiLM gating 유지

## 계획된 검증

- 스모크 체크:
  - Docker GPU runtime
  - `AWGN`, `seed=1`, `n_rounds=1`
  - `Rayleigh`, `seed=1`, `n_rounds=1`
  - 확인 항목:
    - 실행 성공 여부
    - active count 증가 여부
    - baseline 대비 comm 증가 여부
    - `w_o_film` 대비 comm가 과도하게 같아지지 않는지 여부
- 비교 대상:
  - baseline `CA-SSFL`
  - 기존 `SSFLv6_w_o_film`
  - 새 `w/o channel mask only`
- 예상 산출물 경로:
  - `/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`
- 예상 실행 수:
  - smoke: `2 runs`
  - main: `2 channels x 4 seeds = 8 runs`
  - total: `10 runs`
- 예상 소요 시간:
  - smoke: 약 `10~15분`
  - main: 약 `60~75분`
  - total: 약 `70~90분`
- 시간 추정 전제:
  - 최근 `cifar10`, `n_clients=8`, `200 rounds` 기준
  - Docker GPU runtime 정상 동작
  - queue 중단 없이 연속 수행

## 고정 조건

- dataset: `cifar10`
- partition type: `class`
- `n_clients=8`
- `n_client_data=3000`
- `batch_size=100`
- `n_epochs=1`
- `n_rounds=200`
- `compressed_dim=4096`
- seed: `1,2,3,4`
- channel: `AWGN`, `Rayleigh`

## 성공 기준

- 새 exact ablation이 baseline 대비 더 높은 통신량을 보이는지 확인
- 새 exact ablation이 기존 `w_o_film` proxy보다 통신량이 낮거나 해석 가능한 차이를 보이는지 확인
- 정확도 변화가 `channel mask` 제거 효과로 설명 가능한 방향인지 확인
- 결과 표에서 `w/o channel masking`을 더 이상 `w_o_film` proxy로 대신 쓰지 않아도 될 정도로 정의가 명확해질 것

## 리스크와 열린 질문

- 기술적 리스크:
  - trainer와 eval에서 동일한 스위치가 일관되게 반영되지 않으면 train/eval semantics가 어긋날 수 있다
  - result path에 새 스위치가 반영되지 않으면 baseline artifact와 구분이 흐려질 수 있다
- 평가상 리스크:
  - exact ablation과 기존 `w_o_film` proxy의 차이가 생각보다 작으면, 논문 표에서 둘을 구분해 넣을 실익이 제한될 수 있다
  - 반대로 차이가 크면 기존 Table II 하단 해석 문구를 수정해야 할 수 있다
- 검토가 필요한 질문:
  - 결과 표 라벨을 최종적으로 `w/o Channel Masking`으로 둘지, `w/o Channel Mask Only`로 내부 문서에서 먼저 구분할지
  - 실험 문서에서 이 스위치 이름을 그대로 노출할지, 논문용 서술만 유지할지

## 사용자 검토 메모

- 피드백:
  - 대기중
- 합의된 결정:
  - 없음
- 남은 쟁점:
  - exact ablation 실행 여부
  - smoke 후 full run 진행 여부

## 실행 게이트

- 구현 시작 가능?: `아니오`
- 아니라면 먼저 명확히 할 점:
  - 이 계획 문서 검토
  - `--channel_mask_allpass_enable=1` 기준으로 실행 범위 확정
