# 실험 결과

## 메타데이터

- 실험 id: `2026-04-15_12-20_v01_channel-specific-ablation-plan`
- 종료 일시: `2026-04-15 14:20 KST`
- 상태: 완료
- 담당자: Codex

## 요약

채널별 best `CA-SSFL` baseline 위에서 `w/o VIB`, `w/o FiLM`을 `AWGN`, `Rayleigh`, `seed=1,2,3,4`로 재실행했다. 현재 paper-facing 목적에서는 이 중 `SSFLv6_w_o_film` 결과를 논문 Table II 하단 `w/o Channel Masking` 행에 사용한다.

다만 이 결과는 코드 기준 exact `channel mask only off`가 아니라, `FiLM` gating까지 함께 제거한 stronger proxy다. 내부 재현성 문서에서는 이 점을 유지하되, 원고 표에는 현재 사용자 결정에 따라 기존 `w_o_film` 결과를 사용한다.

## paper-facing 비교

### AWGN

| 설정 | final acc mean ± std | comm mean ± std | `-6 dB` | `12 dB` |
| --- | ---: | ---: | ---: | ---: |
| Baseline `CA-SSFL` | `41.71 ± 2.14` | `14.03 ± 0.59 GB` | `39.89 ± 2.83` | `41.98 ± 1.91` |
| `SSFLv6_w_o_film` | `39.34 ± 2.01` | `17.22 ± 1.45 GB` | `38.90 ± 2.04` | `39.38 ± 2.13` |

### Rayleigh

| 설정 | final acc mean ± std | comm mean ± std | `-6 dB` | `12 dB` |
| --- | ---: | ---: | ---: | ---: |
| Baseline `CA-SSFL` | `40.41 ± 3.13` | `14.59 ± 0.52 GB` | `37.88 ± 2.71` | `41.11 ± 3.02` |
| `SSFLv6_w_o_film` | `38.07 ± 3.58` | `17.48 ± 1.48 GB` | `36.34 ± 3.32` | `38.51 ± 3.72` |

## 해석

- `w_o_film`은 두 채널 모두 baseline 대비 통신량이 증가하고 정확도도 하락한다.
- 따라서 논문 메시지 측면에서는 `FiLM` 기반 channel-adaptive masking이 실제 trade-off에 기여한다는 방향을 더 강하게 보여준다.
- exact `w/o channel mask only`보다 열화가 더 크므로, 내부적으로는 stronger proxy라는 주석을 유지해야 한다.

## 결정

- 논문 Table II 하단 `w/o Channel Masking` 행에는 현재 `SSFLv6_w_o_film` 결과를 사용
- exact `w/o channel mask only` 결과는 내부 진단용으로만 보관
- raw `w/o VIB` 결과는 동일 result root 아래 유지

## 산출물

- 실행 스펙: [SPEC.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/SPEC.md)
- 실행 로그:
  - [RUNLOG_AWGN.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RUNLOG_AWGN.md)
  - [RUNLOG_RAYLEIGH.md](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RUNLOG_RAYLEIGH.md)
- result root:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation`
- baseline root:
  - `/home/sunmin/SFL_Semantic/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun`
