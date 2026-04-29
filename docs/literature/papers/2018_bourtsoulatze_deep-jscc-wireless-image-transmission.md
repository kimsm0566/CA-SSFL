# Deep Joint Source-Channel Coding for Wireless Image Transmission

## 서지 정보

- 저자: Eirina Bourtsoulatze, David Burth Kurka, Deniz Gunduz
- 학회/저널 및 연도: IEEE TCCN, 2019
- 원문 링크: https://arxiv.org/abs/1809.01733
- 로컬 파일 경로: 없음

## 한 줄 요약

- 의미 표현을 별도 압축/채널코드 없이 dense analog latent로 직접 채널에 실으면 저 SNR에서 graceful degradation을 얻을 수 있다.

## 문제 설정

- 학습 설정: end-to-end autoencoder
- 데이터셋: 이미지 전송
- 파티션 방식: 해당 없음
- 클라이언트 수: 해당 없음
- 로컬 학습 예산: 해당 없음
- 채널 모델: AWGN 중심
- SNR 설정: 학습/평가 SNR mismatch 포함
- 통신 제약: bandwidth ratio 제한

## 방법 요약

- CNN encoder/decoder가 이미지에서 복소 채널 심볼로 직접 매핑
- 별도 source coding, channel coding 없이 JSCC로 일괄 최적화
- dense continuous representation을 채널에 그대로 실어 cliff effect를 피함

## 보고된 결과

- 주요 지표: 재구성 품질
- 비교 기준선: JPEG/JPEG2000 + capacity-approaching channel code
- 핵심 성과: low SNR와 low bandwidth에서 디지털 분리형 전송보다 우수
- 강건성 점검: 학습 SNR과 테스트 SNR mismatch에 대해 graceful degradation 보고

## 이 프로젝트와의 연관성

- 저장소 내 대응 영역: `src/models/model.py`, `src/utils/trainer.py`
- 가장 가까운 in-repo 알고리즘 또는 baseline: `SC-USFL` 쪽 dense semantic transmission 성격
- 바로 재사용 가능해 보이는 점:
  - sparse semantic code보다 distributed dense representation이 fading에 덜 brittle하다는 관찰 근거

## 약점과 재현 리스크

- 분류 정확도보다 재구성 품질 중심
- split/federated semantic bottleneck과는 설정 차이가 큼

## 가능한 개선점

- 우리 문제에 그대로 복제하기보다 “중요 정보가 한 좌표에 몰리지 않는 표현”의 필요성을 정당화하는 근거로 쓰는 것이 적절

## 이 코드베이스에서 검증할 가설

- Rayleigh에서 강건성이 약한 핵심 원인 중 하나는 sparse axis-aligned latent이며, dense/distributed 성질을 일부 회복하면 저 SNR 성능이 개선될 수 있다.

## 액션 상태

- 상태: reviewed
- 다음 단계: `SC-USFL`의 dense robustness를 완전 모방하기보다, 우리 구조 안에서 최소한의 distributed redundancy를 어떻게 만들지 설계
