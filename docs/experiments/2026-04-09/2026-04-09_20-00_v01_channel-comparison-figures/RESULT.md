# 결과 정리

## 메타데이터

- 실험 id: `2026-04-09_20-00_v01_channel-comparison-figures`
- 상태: `completed`

## 목적

기존에 완료된 `AWGN` 및 `Rayleigh` 3-way benchmark 결과를 채널별 그래프로 정리한다.

## 산출물

- `figures/awgn_snr_accuracy_threeway.png`
- `figures/awgn_snr_accuracy_threeway.pdf`
- `figures/awgn_final_acc_vs_comm_threeway.png`
- `figures/awgn_final_acc_vs_comm_threeway.pdf`
- `figures/rayleigh_snr_accuracy_threeway.png`
- `figures/rayleigh_snr_accuracy_threeway.pdf`
- `figures/rayleigh_final_acc_vs_comm_threeway.png`
- `figures/rayleigh_final_acc_vs_comm_threeway.pdf`
- `figures/channel_threeway_summary.json`

## 비고

- `AWGN` 그래프는 `n_clients=8` 결과 기준
- `Rayleigh` 그래프는 기존 claim용 seed 조합 기준
  - `SFL`, `SC-USFL`: `n_clients=9`, seed `1,2,3,4`
  - `SSFLv6 candidate`: `n_clients=9`, seed `1,2`는 `rayleigh-seq-full`, seed `3,4`는 `cross-benchmark`
