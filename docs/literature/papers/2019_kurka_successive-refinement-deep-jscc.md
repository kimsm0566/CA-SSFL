# Successive Refinement of Images with Deep Joint Source-Channel Coding

## 서지 정보

- 저자: David Burth Kurka, Deniz Gunduz
- 학회/저널 및 연도: IEEE SPAWC, 2019
- 원문 링크: https://arxiv.org/abs/1903.06333
- 로컬 파일 경로: 없음

## 한 줄 요약

- 하나의 semantic description만 보내지 않고 layered/progressive description으로 나누면, 일부 layer가 손상돼도 기본 품질을 방어할 수 있다.

## 문제 설정

- 학습 설정: progressive deep JSCC
- 데이터셋: 이미지 전송
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: Gaussian channel
- SNR 설정: 저 SNR 포함
- 통신 제약: layer별 incremental bandwidth

## 방법 요약

- 단일 shot이 아니라 refinement layer를 순차 전송
- base layer는 coarse semantics를 전달하고, 이후 layer가 추가 세부정보를 보강
- 서로 다른 complexity-performance trade-off를 갖는 3개 전략 제안

## 보고된 결과

- 주요 지표: 재구성 품질
- 비교 기준선: 단일-layer transmission
- 핵심 성과: deep JSCC가 layered representation을 학습해 single-layer 성능에 근접
- 강건성 점검: progressive setting에서도 graceful degradation 유지

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `src/utils/trainer.py`의 active feature selection / transmission
- 가장 가까운 in-repo 알고리즘 또는 baseline: `CA-SSFL Orig`
- 바로 재사용 가능해 보이는 점:
  - “핵심 feature + 보강 feature”의 2계층 전송 아이디어
  - 일부 feature가 지워져도 base semantics가 남는 설계

## 약점과 재현 리스크

- 이미지 reconstruction 문맥이라 classification task와 직접 매칭되지는 않음
- 통신 횟수와 스케줄 설계가 필요해 구현 복잡도 증가

## 가능한 개선점

- 우리 구조에선 전체 progressive 전송보다 “small base support + optional refinement support” 형태가 더 현실적

## 이 코드베이스에서 검증할 가설

- Rayleigh에서 top semantic features만으로 구성된 작은 base support를 항상 보장하고, 나머지는 추가 refinement로 보내면 강건성이 개선될 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: `support floor`를 단순 floor가 아니라 `base-support guarantee`로 다시 재설계하는 근거로 사용
