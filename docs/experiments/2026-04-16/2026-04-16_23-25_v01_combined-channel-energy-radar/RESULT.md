# RESULT

## 한줄 요약

Fig. 3 대체용으로 `AWGN`과 `Rayleigh`를 한 그래프 안에 함께 넣는 combined radar chart를 만들었다.  
축은 `AWGN Accuracy`, `Rayleigh Accuracy`, `1 / Avg. Communication Overhead`, `1 / Avg. Estimated Client Energy`로 구성했다.

## 산출물

- CIFAR-10 그래프: [cifar10_combined.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/cifar10_combined.png)
- CIFAR-100 그래프: [cifar100_combined.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/cifar100_combined.png)
- 2개 패널: [combined_channel_energy_radar_panel.png](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/combined_channel_energy_radar_panel.png)
- 정규화 값/원값: [combined_channel_energy_radar_summary.json](/home/sunmin/SFL_Semantic/docs/experiments/2026-04-16/2026-04-16_23-25_v01_combined-channel-energy-radar/figures/combined_channel_energy_radar_summary.json)

## 해석 포인트

- 이 버전은 `AWGN`과 `Rayleigh`를 separate axes로 넣어서, 기존 Fig. 3의 다른 subfigure를 제거해도 채널별 정보가 그래프 안에 남도록 설계했다.
- `communication overhead`는 두 채널의 평균값을 사용했다.
- `estimated client energy`는 실측 Joule이 아니라, `평균 통신량 + 계산량(MFLOPs)`을 합친 정규화 proxy다.
- 따라서 이 그림의 메시지는 `절대 accuracy 최고`가 아니라, `양 채널을 함께 고려했을 때 accuracy-overhead-energy trade-off가 어떠한가`에 있다.

## 현재 관찰

### CIFAR-10

- `SFL`은 두 채널 accuracy 축에서 가장 크지만, 평균 overhead와 energy 축은 크게 불리하다.
- `CA-SSFL`은 두 채널 accuracy가 `SFL`보다 낮지만, 평균 overhead와 energy 축에서 가장 유리하다.
- `SC-USFL`는 accuracy는 중간 이하이고, energy 축은 비교적 좋지만 overhead는 `CA-SSFL`보다 불리하다.

### CIFAR-100

- `CA-SSFL`은 두 채널 accuracy와 평균 overhead 축에서 가장 균형이 좋다.
- `SC-USFL`는 energy 축은 가장 좋지만 accuracy 손실이 크다.
- `SFL`은 accuracy는 가장 높지만 평균 overhead와 energy 축에서 크게 불리하다.

## 주의

- `energy`는 실측 하드웨어 전력이나 Joule 단위가 아니다.
- 논문 본문/캡션에는 `estimated client energy`, `normalized energy proxy`, 또는 `client energy proxy` 같은 표현이 안전하다.
- `transmission energy`만 쓰면 `communication overhead`와 거의 같은 정보가 되므로, 이번 그림에서는 의도적으로 `통신 + 계산` proxy를 사용했다.
