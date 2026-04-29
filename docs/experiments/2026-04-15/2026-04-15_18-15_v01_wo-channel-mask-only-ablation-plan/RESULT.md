# 실험 결과

## 메타데이터

- 실험 id: `2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan`
- 종료 일시: `2026-04-15 19:49 KST`
- 상태: 완료
- 담당자: Codex

## 요약

`FiLM` gating과 `VIB`는 유지한 채 final `chan_mask`만 all-pass로 강제하는 exact `w/o channel mask only` ablation을 `AWGN`, `Rayleigh`, `seed=1,2,3,4` 조건에서 matched 실행했다. 결과는 두 채널 모두 baseline `CA-SSFL`보다 통신량이 증가하고 정확도는 하락했다. 따라서 현재 `CA-SSFL`에서 `channel mask`는 실제로 통신량 절감과 성능 유지에 기여한다.

동시에 이번 exact ablation은 기존 `SSFLv6_w_o_film` proxy보다 일관되게 덜 나빴다. 즉 기존 proxy는 `channel mask only off`가 아니라 `FiLM gating`까지 함께 제거한 stronger ablation이다. 내부 문서에서는 이 exact 결과를 유지하되, paper-facing Table II 하단은 현재 사용자 결정에 따라 기존 `w_o_film` 결과를 사용한다.

## 고정 조건

- dataset: `cifar10`
- partition_type: `class`
- n_clients: `8`
- n_client_data: `3000`
- batch_size: `100`
- n_epochs: `1`
- n_rounds: `200`
- model_type: `resnetv2`
- compressed_dim: `4096`
- seed_set: `1,2,3,4`
- evaluation path: canonical Docker GPU runtime

## 결과 요약

### AWGN

| 설정 | final acc mean ± std | comm mean ± std | `-6 dB` | `12 dB` |
| --- | ---: | ---: | ---: | ---: |
| Baseline `CA-SSFL` | `41.71 ± 2.14` | `14.03 ± 0.59 GB` | `39.89 ± 2.83` | `41.98 ± 1.91` |
| Exact `w/o channel mask only` | `39.65 ± 3.50` | `15.05 ± 0.79 GB` | `39.39 ± 3.13` | `39.73 ± 3.51` |
| Proxy `SSFLv6_w_o_film` | `39.34 ± 2.01` | `17.22 ± 1.45 GB` | `38.90 ± 2.04` | `39.38 ± 2.13` |

### Rayleigh

| 설정 | final acc mean ± std | comm mean ± std | `-6 dB` | `12 dB` |
| --- | ---: | ---: | ---: | ---: |
| Baseline `CA-SSFL` | `40.41 ± 3.13` | `14.59 ± 0.52 GB` | `37.88 ± 2.71` | `41.11 ± 3.02` |
| Exact `w/o channel mask only` | `39.24 ± 2.27` | `15.70 ± 1.03 GB` | `36.89 ± 2.07` | `39.91 ± 1.93` |
| Proxy `SSFLv6_w_o_film` | `38.07 ± 3.58` | `17.48 ± 1.48 GB` | `36.34 ± 3.32` | `38.51 ± 3.72` |

## 비교 해석

### Exact vs Baseline

- `AWGN`: final acc `-2.06%p`, comm `+1.02 GB`, `-6 dB -0.50%p`, `12 dB -2.25%p`
- `Rayleigh`: final acc `-1.17%p`, comm `+1.11 GB`, `-6 dB -0.98%p`, `12 dB -1.20%p`

해석:

- `channel mask`를 끄면 두 채널 모두 통신량이 늘었다.
- 정확도도 baseline보다 좋아지지 않았다.
- 즉 현재 설정에서 `channel mask`는 단순한 추가 장치가 아니라 실제 trade-off를 지탱하는 핵심 구성요소다.

### Exact vs Proxy `SSFLv6_w_o_film`

- `AWGN`: final acc `+0.31%p`, comm `-2.17 GB`, `-6 dB +0.49%p`, `12 dB +0.35%p`
- `Rayleigh`: final acc `+1.17%p`, comm `-1.78 GB`, `-6 dB +0.56%p`, `12 dB +1.40%p`

해석:

- exact 결과는 기존 proxy보다 consistently 덜 나빴다.
- 따라서 기존 `w_o_film`은 exact `channel mask only off`가 아니라 stronger proxy로 해석해야 한다.
- 다만 paper-facing 표는 현재 사용자 결정에 따라 기존 `w_o_film` 결과를 유지한다.

## 실행 검증

- Level 0:
  - `python3 -m py_compile src/utils/option.py src/run_exp_main.py src/utils/trainer.py src/utils/eval.py`
  - `python3 -m py_compile scripts/analyze_wo_channel_mask_only_ablation.py`
- Level 1:
  - `check-gpu` 통과
  - `AWGN`, `Rayleigh` smoke에서 둘 다 `seed_1.npz` 생성
- Level 2:
  - canonical seed `1,2,3,4`
  - `AWGN 4 runs + Rayleigh 4 runs = 8 runs` 완료
- runtime:
  - `SPEC` 예상 `70~90분`
  - 실제 smoke artifact 시각 `18:38 KST`
  - full queue `18:39 ~ 19:42 KST`
  - 예상보다 약간 빠르게 종료

## 결정

- baseline `CA-SSFL`는 유지
- exact 결과는 internal diagnostic artifact로 보관
- 논문 Table II 하단 `w/o Channel Masking`에는 기존 `SSFLv6_w_o_film` 결과를 사용
- 기존 `SSFLv6_w_o_film`은 내부적으로 `proxy / stronger ablation`이라고 명시
- 결정: `보관`

## 산출물

- 분석 요약: `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/summary.json`
- 실험 로그: `docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan/logs/full_run.log`
- smoke 결과:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-awgn`
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation-smoke-rayleigh`
- main 결과:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation`
- baseline 비교 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`
- proxy 비교 경로:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation`
