# FIGURE EXPLAINER

## 목적

교수님께 설명할 때, 기존 Fig. 3에서 일부 subfigure를 빼더라도 `AWGN`과 `Rayleigh` 정보가 사라지지 않도록 하기 위해 만든 대체 레이더 차트다.

## 왜 이 구성을 썼는가

- 기존 `Accuracy + 1 / Communication Overhead + 다른 축` 구성은 채널 정보가 별도 subfigure에 남아 있어야 해석이 쉬웠다.
- 이번 버전은 `AWGN Accuracy`와 `Rayleigh Accuracy`를 각각 축으로 넣어서, 채널별 성능 차이를 한 장에서 바로 볼 수 있게 했다.
- 나머지 2개 축은 `평균 communication overhead`와 `평균 estimated client energy`로 두어, 단순 정확도 비교가 아니라 deployment 관점의 비용도 함께 보이게 했다.

## 각 축 설명

### 1. `AWGN Accuracy`

- `AWGN` 채널에서의 최종 정확도
- 데이터셋 내부에서 최고 정확도 방법을 `1.0`으로 정규화
- 값이 클수록 좋음

### 2. `Rayleigh Accuracy`

- `Rayleigh` 채널에서의 최종 정확도
- 데이터셋 내부에서 최고 정확도 방법을 `1.0`으로 정규화
- 값이 클수록 좋음

### 3. `1 / Avg. Communication Overhead`

- `AWGN`과 `Rayleigh`에서의 communication overhead 평균값 사용
- 평균 overhead가 가장 작은 방법을 `1.0`으로 정규화
- 따라서 값이 클수록 평균 통신 부담이 작음

수식:

```text
avg_comm_mb = 0.5 * (comm_awgn_mb + comm_rayleigh_mb)
score = min(avg_comm_mb) / avg_comm_mb
```

### 4. `1 / Avg. Estimated Client Energy`

- 실측 Joule이 아니라 `클라이언트 에너지 proxy`
- 평균 communication overhead와 computation cost(MFLOPs)를 반반 섞어 구성
- 평균 energy proxy가 가장 작은 방법을 `1.0`으로 정규화
- 값이 클수록 더 에너지 효율적이라고 해석

수식:

```text
energy_proxy = 0.5 * (avg_comm_mb / min_avg_comm_mb)
             + 0.5 * (comp_mflops / min_comp_mflops)
score = min(energy_proxy) / energy_proxy
```

사용한 computation cost:

- `SFL`: `70.50 MFLOPs`
- `SC-USFL`: `80.27 MFLOPs`
- `CA-SSFL (Ours)`: `113.84 MFLOPs`

## 왜 실측 에너지가 아닌 proxy를 썼는가

- 현재 결과에는 `TX power`, `hardware power`, `wall-clock energy` 같은 실측 항목이 없다.
- `transmission energy`만 쓰면 사실상 `communication overhead`와 같은 축이 된다.
- 그래서 이번 그림에서는 중복을 피하기 위해 `통신 비용 + 계산 비용`을 합친 정규화 proxy를 사용했다.

## 그림 링크

- CIFAR-10: [cifar10_combined.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/cifar10_combined.png)
- CIFAR-100: [cifar100_combined.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/cifar100_combined.png)
- 패널: [combined_channel_energy_radar_panel.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/combined_channel_energy_radar_panel.png)
- 수치 요약: [combined_channel_energy_radar_summary.json](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/combined_channel_energy_radar_summary.json)

## 교수님께 설명할 때의 안전한 표현

- `energy`보다는 `estimated client energy proxy`
- `communication overhead`는 `average communication overhead across AWGN and Rayleigh`
- 핵심 메시지는 `양 채널을 함께 고려한 accuracy-cost trade-off`라고 설명하는 것이 안전하다
