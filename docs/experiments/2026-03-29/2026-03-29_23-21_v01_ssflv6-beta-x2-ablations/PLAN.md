# 실험 계획

## 메타데이터

- 실험 id: `2026-03-29_23-21_v01_ssflv6-beta-x2-ablations`
- 초안 일시: `2026-03-29 23:21 KST`
- 상태: `초안`
- 담당자: `Codex + 사용자`

## 목표

기존 `SSFLv6` ablation 실험의 고정 조건을 유지한 채 `beta`만 `0.0005 -> 0.001`로 두 배 올렸을 때, baseline과 세 가지 ablation의 communication-performance trade-off가 어떻게 바뀌는지 확인한다.

이번 범위의 직접 실행 대상은 다음 네 가지다.

- `SSFLv6`
- `SSFLv6_w_o_vib`
- `SSFLv6_w_o_film`
- `SSFLv6_w_o_beta`

성공 기준은 다음과 같다.

- 네 알고리즘이 모두 Docker GPU 경로에서 같은 `beta=0.001` 조건으로 실행된다.
- 결과물이 기존 `beta=0.0005` 실험과 섞이지 않게 새 실험 폴더 아래 분리 저장된다.
- 최소한 `seed=1` 기준 trend run과 full run 결과를 확보해, 기존 실험과 방향성을 비교할 수 있다.

## 지금 하는 이유

- 방금 완료한 `2026-03-29_20-32_v01_ssflv6-ablations`에서 `SSFLv6_w_o_beta`가 baseline보다 더 높은 정확도를 보였지만 통신량도 더 컸다.
- 현재 `beta` 강도가 너무 약해서 baseline과 `w_o_beta`의 차이가 충분히 드러나지 않았을 가능성이 있다.
- `beta`를 두 배 올리면 VIB/정보 병목 강도가 바뀌면서 통신량과 정확도 균형이 이동할 수 있다.

현재까지 확인된 사실:

- 원래 threshold 기준 `beta=0.0005`, `seed=1`, full `200` 결과:
  - `SSFLv6`: `28386.97 MB`, `43.17%`, `12dB 43.29%`
  - `SSFLv6_w_o_beta`: `29419.54 MB`, `45.29%`, `12dB 47.09%`
  - `SSFLv6_w_o_film`: `93566.85 MB`, `42.58%`, `12dB 42.43%`
  - `SSFLv6_w_o_vib`: `177271.38 MB`, `21.51%`, `12dB 20.93%`
- 현재 canonical 실행 경로는 Docker GPU `run-exp`다.
- 현재 코드 상태는 comm-debug 수정이 채택되지 않은 원래 threshold 식이다.

## 제안 변경사항

- 대상 코드 경로:
  - 코드 변경 없이 실행 조건만 변경
  - 문서/산출물 경로:
    - `docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/`
- 의도한 동작 변화:
  - 실행 인자의 `beta`만 `0.001`로 바꿔 baseline과 ablation을 다시 비교한다.
  - 기존 `beta=0.0005` 실험과 직접 비교 가능한 새 artifact를 만든다.
- 유지할 조건:
  - `dataset=cifar10`
  - `partition_type=class`
  - `n_clients=9`
  - `n_client_data=3000`
  - `batch_size=100`
  - `n_epochs=1`
  - `n_rounds=200`
  - `model_type=resnetv2`
  - `channel_type=rayleigh`
  - `snr_db=12`
  - `compressed_dim=4096`
  - `pruning_threshold=1.0`
  - `use_private_SGD=0`
  - Docker GPU 실행 경로

## 후보 접근법

- 접근 A:
  - 기존 실험과 동일하게 smoke 후 full run을 진행한다.
  - trend run `20`라운드로 먼저 경향을 본 뒤 full `200`으로 들어간다.
  - 장점: 비싼 full run 전에 이상 징후를 빨리 확인할 수 있다.
  - 단점: 절차가 길어진다.

- 접근 B:
  - 곧바로 baseline과 3개 ablation full `200` run을 실행한다.
  - 장점: 빠르게 최종 비교 결과를 얻는다.
  - 단점: `beta=0.001`이 불안정할 경우 디버깅 비용이 커진다.

- 우선 접근법과 그 이유:
  - 접근 A를 사용한다.
  - 이유: `beta`는 학습 동역학에 직접 영향을 주므로, 최소한 trend run으로 발산/통신량 이상치를 먼저 확인하는 편이 안전하다.

## 계획된 검증

- 스모크 체크:
  - `check-gpu`
  - 필요 시 네 알고리즘 각각 `n_rounds=1` smoke
- 비교 대상:
  - 1차: `beta=0.001` baseline vs `beta=0.0005` baseline
  - 2차: `beta=0.001` baseline vs `beta=0.001` ablations
  - 3차: `beta=0.0005` 실험과 `beta=0.001` 실험 간 방향성 비교
- 예상 산출물 경로:
  - `docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/PLAN.md`
  - 후속 `SPEC.md`, `WORKLOG.md`, `RESULT.md`
  - `docs/experiments/2026-03-29_23-21_v01_ssflv6-beta-x2-ablations/artifacts/`

## 리스크와 열린 질문

- 기술적 리스크:
  - `beta=0.001`에서 학습이 더 불안정해질 수 있다.
  - full `200` run 4개는 여전히 시간이 길다.
- 평가상 리스크:
  - `seed=1`만으로는 claim-making 비교가 아니다.
  - 정확도가 올라가도 통신량이 함께 올라가면 개선으로 볼 수 없다.
- 검토가 필요한 질문:
  - 이번에도 baseline 포함 4개 전체를 `beta=0.001`로 다시 돌릴지?
  - trend `20` 후 바로 full `200`로 갈지, smoke까지 먼저 둘지?

## 사용자 검토 메모

- 피드백:
  - `beta`를 두 배 올려서 같은 실험을 다시 해본다.
- 합의된 결정:
  - 없음
- 남은 쟁점:
  - 실행 범위를 `trend -> full`로 갈지, 바로 full로 갈지

## 실행 게이트

- 구현 시작 가능?: `아니오`
- 아니라면 먼저 명확히 할 점:
  - baseline 포함 4개 전체를 `beta=0.001`로 다시 돌리는지, 그리고 trend를 선행할지 사용자의 확인이 필요하다.
