# 결과 요약

## 결과

- 상태: `부분 성공`
- 결정: `stage 3만 후속 확장`

## 무엇을 테스트했는가

`SSFLv6` 통신량 절감을 위해 세 가지 후보를 `seed=2`, `200`라운드 full run으로 baseline과 다시 비교했다. `20`라운드 trend 기록은 참고용으로만 남기고, 이 문서의 결론은 full `200` 결과만 기준으로 잡는다.

## 최종 비교

- baseline: `현재 active 코드의 seed=2 full 200 run`
- candidate: `stage 1 samplewise-union`, `stage 2 small FiLM gate`, `stage 3 beta=0.00075`
- 고정 조건 일치 여부: `예`
- seeds: `2`
- 산출물 경로:
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage1-samplewise-union-full200/`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage2-small-film-gate-full200/`
  - `docs/experiments/2026-03-30_00-41_v01_ssflv6-staged-mask-reduction/artifacts/stage3-beta-00075-full200/`

## 주요 지표

- baseline round `200`:
  - `Acc 42.19%`
  - `Total comm 30541.49 MB`
  - `Total data comm 21146.86 MB`
  - `Total model comm 9394.63 MB`
  - `Test SNR 12dB 42.32%`
- stage 1 samplewise-union round `200`:
  - `Acc 45.82%`
  - `Total comm 39875.66 MB`
  - `Total data comm 30481.03 MB`
  - `Total model comm 9394.63 MB`
  - `Test SNR 12dB 46.93%`
- stage 2 small FiLM gate round `200`:
  - `Acc 42.54%`
  - `Total comm 33109.13 MB`
  - `Total data comm 27342.62 MB`
  - `Total model comm 5766.50 MB`
  - `Test SNR 12dB 42.26%`
- stage 3 `beta=0.00075` round `200`:
  - `Acc 42.71%`
  - `Total comm 28950.00 MB`
  - `Total data comm 19555.37 MB`
  - `Total model comm 9394.63 MB`
  - `Test SNR 12dB 44.19%`
- seed 분산: `해당 없음`

## 해석

stage 1은 full `200`에서도 같은 결론이었다. 샘플별 average active는 줄지만 batch union indices가 크기 때문에 누적 `data comm`가 baseline보다 크게 증가했다. 정확도는 높아졌지만 이 저장소의 목표인 communication-performance trade-off 기준으로는 미채택이다.

stage 2는 `model comm` 절감에는 확실히 성공했다. 다만 active 차원이 덜 줄어들어 `data comm`가 더 커졌고, 그 증가폭이 `model comm` 감소폭을 상쇄하고도 남았다. 따라서 total comm 기준으로 baseline보다 나빴다.

stage 3 `beta=0.00075`만이 이번 세 후보 중 유일하게 matched single-seed run에서 baseline보다 좋아졌다. total comm가 `30541.49 MB -> 28950.00 MB`로 줄었고 accuracy도 `42.19% -> 42.71%`로 소폭 상승했다. 아직 single-seed 결과라 default change로 승격하진 않지만, 이번 실험의 우선 후속 후보는 명확히 stage 3이다.

## 알려진 한계

- 세 후보 모두 `seed=2` 단일 결과다.
- `beta=0.00075`는 promising하지만 multi-seed 검증 전에는 promotion claim을 할 수 없다.

## 다음 권장 행동

- `SSFLv6 beta=0.00075`를 `seed 1,3,4`로 확장
- 필요 시 `beta=0.000625`, `0.001`도 같은 full `200` budget으로 추가 비교
