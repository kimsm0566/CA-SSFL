# Robust Image Semantic Coding with Learnable CSI Fusion Masking over MIMO Fading Channels

## 서지 정보

- 저자: Bingyan Xie, Yongpeng Wu, Yuxuan Shi, Wenjun Zhang, Shuguang Cui, Merouane Debbah
- 학회/저널 및 연도: IEEE TWC, 2024
- 원문 링크: https://arxiv.org/abs/2406.07389
- 로컬 파일 경로: 없음

## 한 줄 요약

- fading 강건성은 feature를 나중에 섞는 것보다, source state와 channel state를 함께 보는 learnable masking/attention 쪽이 더 직접적이다.

## 문제 설정

- 학습 설정: image semantic coding with CSI side information
- 데이터셋: 이미지 semantic coding
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: MIMO fading
- SNR 설정: 다양한 fading 조건
- 통신 제약: masking ratio/CSI-aware coding

## 방법 요약

- CSI를 semantic extractor의 side information으로 사용
- abrupt concatenation 대신 non-invasive multi-head attention으로 CSI fusion
- learned attention masking map과 learnable mask ratio로 robust attention distribution 유도

## 보고된 결과

- 주요 지표: semantic transmission 성능
- 비교 기준선: 기존 semantic communication frameworks
- 핵심 성과: MIMO fading에서 기존 방법 대비 우수
- 강건성 점검: 다양한 fading 조건에서 superiority 보고

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `FiLM` gating, `support floor`, future masking policy
- 가장 가까운 in-repo 알고리즘 또는 baseline: `CA-SSFL Orig`의 FiLM masking
- 바로 재사용 가능해 보이는 점:
  - 고정 threshold 기반 gating보다 source+channel-aware learned masking이 더 자연스럽다는 근거

## 약점과 재현 리스크

- Swin Transformer 기반 MIMO image semantic coding
- 현재 ResNet split-learning 구조와 차이가 큼

## 가능한 개선점

- 우리 구조에서는 full CSI fusion 대신, current SNR와 latent statistics를 함께 보는 learned threshold predictor로 축소 가능

## 이 코드베이스에서 검증할 가설

- 현재 `film_max_t/film_min_t`의 선형 규칙 대신, feature statistics와 SNR을 함께 받는 learned support policy가 Rayleigh에 더 적합할 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: `FiLM threshold rule reshape`를 hand-crafted 선형식이 아니라 작은 learned head로 바꾸는 후속 실험 고려
