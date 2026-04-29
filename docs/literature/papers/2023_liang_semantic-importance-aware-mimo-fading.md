# Semantic Importance-Aware Based for Multi-User Communication Over MIMO Fading Channels

## 서지 정보

- 저자: Haotai Liang, Zhicheng Bao, Wannian An, Chen Dong, Xiaodong Xu
- 학회/저널 및 연도: arXiv preprint, 2023
- 원문 링크: https://arxiv.org/abs/2312.16057
- 로컬 파일 경로: 없음

## 한 줄 요약

- fading에서 semantic importance가 다른 심볼을 동일하게 다루지 않고, 더 좋은 subchannel에 중요 심볼을 우선 매핑하면 성능이 올라간다.

## 문제 설정

- 학습 설정: semantic communication over MIMO Rayleigh
- 데이터셋: semantic transmission task
- 파티션 방식: 해당 없음
- 클라이언트 수: 단일/다중 사용자
- 로컬 학습 예산: 해당 없음
- 채널 모델: MIMO Rayleigh fading
- SNR 설정: SID, SOP 분석 포함
- 통신 제약: channel bandwidth ratio

## 방법 요약

- semantic symbols의 중요도 차이를 전제로 함
- MIMO equivalent subchannels를 SVD로 분해
- 중요 semantic layer를 더 좋은 subchannel에 매핑
- multi-user에선 semantic interference cancellation 추가

## 보고된 결과

- 주요 지표: semantic information distortion, semantic outage probability
- 비교 기준선: non-importance-aware semantic communication
- 핵심 성과: 여러 MIMO fading 시나리오에서 semantic 성능 향상
- 강건성 점검: CBR, SNR에 따른 성능 분석 제시

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `src/utils/trainer.py` support selection / power allocation
- 가장 가까운 in-repo 알고리즘 또는 baseline: `semantic power` 및 future stream mapping
- 바로 재사용 가능해 보이는 점:
  - “중요한 feature를 더 좋은 channel condition에 우선 배치”라는 사고방식

## 약점과 재현 리스크

- MIMO/SVD channel decomposition 가정
- 현재 저장소는 single-stream sparse transmission이므로 직접 적용은 어려움

## 가능한 개선점

- 현재 구조에서는 subchannel mapping 대신 “중요 feature에 더 높은 reliability budget” 또는 “중요 feature 우선 support guarantee”로 해석해 이식하는 편이 적절

## 이 코드베이스에서 검증할 가설

- semantic importance를 반영한 protection은 유효하되, 현재 `alpha=2.0`처럼 과도한 집중은 오히려 해롭다. 더 약한 importance-aware allocation이 필요하다.

## 액션 상태

- 상태: reviewed
- 다음 단계: semantic power를 low-alpha와 capped weighting으로 재설계
