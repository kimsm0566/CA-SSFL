# Generative Feature Imputing -- A Technique for Error-resilient Semantic Communication

## 서지 정보

- 저자: Jianhao Huang, Qunsong Zeng, Hongyang Du, Kaibin Huang
- 학회/저널 및 연도: arXiv preprint, 2025
- 원문 링크: https://arxiv.org/abs/2508.17957
- 로컬 파일 경로: 없음

## 한 줄 요약

- fading/packet loss로 semantic feature가 지워지면, 더 강한 보호만이 아니라 “지워진 feature를 복원하는 후단 imputing”도 유효하다.

## 문제 설정

- 학습 설정: error-resilient semantic communication
- 데이터셋: 이미지 semantic transmission
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: block fading, packet loss
- SNR 설정: fading 조건 비교
- 통신 제약: packetization + semantic-aware power allocation

## 방법 요약

- spatial error concentration packetization:
  - 어떤 packet이 깨졌는지 구조적으로 추적 가능하게 왜곡을 집중시킴
- generative feature imputing:
  - diffusion model로 missing feature 복원
- semantic-aware power allocation:
  - 중요 packet에 더 많은 전력 배분

## 보고된 결과

- 주요 지표: semantic accuracy, LPIPS
- 비교 기준선: DJSCC, JPEG2000
- 핵심 성과: block fading에서 더 높은 semantic accuracy와 더 낮은 LPIPS
- 강건성 점검: fading과 packet loss 상황에서 직접 비교

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: server-side decoder, future feature restoration module
- 가장 가까운 in-repo 알고리즘 또는 baseline: `CA-SSFL Orig`
- 바로 재사용 가능해 보이는 점:
  - “지워진 feature를 다른 feature가 대신 못 하면, 후단이 복원하게 하자”는 발상

## 약점과 재현 리스크

- diffusion 기반 imputing은 구현 비용이 큼
- image semantic coding task라 현재 split classification과 완전 동일하진 않음

## 가능한 개선점

- full diffusion 대신 lightweight server-side denoising / missing-feature imputation head로 단순화 가능

## 이 코드베이스에서 검증할 가설

- Rayleigh robustness 문제는 transmitter-side redundancy만으로 풀기 어렵고, 서버 디코더 앞단에 작은 feature restoration module을 두면 개선될 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: 보호 메커니즘 실험이 계속 실패하면 server-side feature denoising/imputing 방향을 새 피벗으로 검토
