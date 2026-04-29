import torch
from data.data import data_loader

def evaluate_model(model, data, args):

    model.eval()
    x, y = data

    loader = data_loader(args.dataset, x, y, batch_size=1000, is_train=False)
    acc = 0.
    for xt, yt in loader:
        xt = torch.tensor(xt, requires_grad=False, dtype=torch.float32).to(args.device)
        yt = torch.tensor(yt, requires_grad=False, dtype=torch.int64).to(args.device)
        preds_labels = torch.squeeze(torch.max(model(xt), 1)[1])
        acc += torch.sum(preds_labels == yt).item()

    return acc / x.shape[0]

def evaluate_model_inf(private_model, proxy_model, data, args):
    private_model.eval()    
    
    
    proxy_model.extract_features = private_model.extract_features
    proxy_model.eval()
    
    x, y = data

    loader = data_loader(args.dataset, x, y, batch_size=args.batch_size, is_train=False)
    private_acc = 0.
    proxy_acc = 0.
    entropy_acc = 0.
    private_inferences = 0
    proxy_inferences = 0
    total_samples = 0
    
    for xt, yt in loader:
        xt = torch.tensor(xt, requires_grad=False, dtype=torch.float32).to(args.device)
        yt = torch.tensor(yt, requires_grad=False, dtype=torch.int64).to(args.device)
        batch_size = xt.size(0)
        total_samples += batch_size

        # private 모델로 예측 확률 계산
        preds_labels = torch.squeeze(torch.max(private_model(xt), 1)[1])
        private_acc += torch.sum(preds_labels == yt).item()
        
        # proxy 모델로 예측 확률 계산
        preds_labels = torch.squeeze(torch.max(proxy_model(xt), 1)[1])
        proxy_acc += torch.sum(preds_labels == yt).item()
        
        # private 모델로 예측 확률 계산
        private_outputs = private_model(xt)
        private_probs = torch.nn.functional.softmax(private_outputs, dim=1)

        private_preds = torch.max(private_probs, 1)[1]
        
        proxy_outputs = proxy_model(xt)
        proxy_preds = torch.max(proxy_outputs, 1)[1] 
        
        # 샘플별 엔트로피 계산
        entropy = -torch.sum(private_probs * torch.log(private_probs + 1e-10), dim=1)
        # 1. 마스크 생성 (각 샘플별로 조건 확인) - 올바른 로직 적용!
        use_private_mask = entropy <= args.entropy_threshold # 엔트로피 낮으면 True
        use_proxy_mask = ~use_private_mask                 # 엔트로피 높으면 True
        
        # 2. 최종 예측 결합 (샘플별 선택)
        final_preds = private_preds.clone()             # 기본값: 클라이언트 예측
        final_preds[use_proxy_mask] = proxy_preds[use_proxy_mask] # 엔트로피 높았던 샘플만 서버 예측으로 덮어쓰기

        # 3. 하이브리드 정확도 계산 (결합된 예측 기반)
        entropy_acc += torch.sum(final_preds == yt).item()
        # (entropy_acc 변수에 이 값을 누적해야 함)

        # 4. 추론 비율 계산 (마스크 기반 샘플 수 계산)
        private_inferences += torch.sum(use_private_mask).item()
        proxy_inferences += torch.sum(use_proxy_mask).item()
        # (client_inferences, server_inferences 변수에 이 값들을 누적해야 함)
    
    private_acc = private_acc / total_samples
    proxy_acc = proxy_acc / total_samples
    entropy_acc = entropy_acc / total_samples
    private_ratio = private_inferences / total_samples
    proxy_ratio = proxy_inferences / total_samples


    return private_acc, proxy_acc, entropy_acc, private_ratio, proxy_ratio



def evaluate_model_loss(model, data, criterion, args): # criterion (손실 함수) 인자 추가
    """
    모델을 평가하고 정확도와 평균 손실을 반환합니다.

    Args:
        model (torch.nn.Module): 평가할 모델.
        data (tuple): (입력 데이터, 레이블 데이터)를 포함하는 튜플.
        criterion (torch.nn.Module): 손실 함수 (예: nn.CrossEntropyLoss()).
        args (Namespace): 설정값을 담고 있는 객체 (device 정보 등 포함).

    Returns:
        tuple: (평균 정확도, 평균 손실)
    """
    model.eval()  # 모델을 평가 모드로 설정
    x, y = data

    loader = data_loader(args.dataset, data[0], data[1], args.batch_size, is_train=False) # 평가용 배치 크기 사용 권장
    
    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0
    
    with torch.no_grad(): # 평가 시에는 그래디언트 계산이 필요 없으므로, torch.no_grad() 사용
        for xt, yt in loader:
            xt = torch.from_numpy(xt).float().to(args.device) # NumPy에서 변환 시 .float() 명시, dtype 직접 지정보다 일반적
            yt = torch.from_numpy(yt).long().to(args.device)  # CrossEntropyLoss는 LongTensor 타겟을 기대

            # 모델 예측 (로짓)
            outputs = model(xt)
            
            # 손실 계산
            loss = criterion(outputs, yt)
            total_loss += loss.item() * xt.size(0) # 배치 손실 합계 (나중에 평균 계산 위함)
                                                  # loss.item()은 스칼라 값, xt.size(0)은 현재 배치 크기

            # 정확도 계산
            _, predicted_labels = torch.max(outputs, 1) # torch.max는 (값, 인덱스) 반환
                                                        # squeeze는 보통 불필요
            correct_predictions += (predicted_labels == yt).sum().item()
            total_samples += yt.size(0)

    avg_accuracy = correct_predictions / total_samples if total_samples > 0 else 0.0
    avg_loss = total_loss / total_samples if total_samples > 0 else float('inf') # 샘플 없으면 무한대 또는 적절한 값

    return avg_accuracy, avg_loss


def evaluate_model_park(private_model, proxy_model, data, args):
    private_model.eval()
    proxy_model.eval()
    x, y = data

    loader = data_loader(args.dataset, x, y, batch_size=100, is_train=False)
    acc = 0.
    for xt, yt in loader:
        xt = torch.tensor(xt, requires_grad=False, dtype=torch.float32).to(args.device)
        yt = torch.tensor(yt, requires_grad=False, dtype=torch.int64).to(args.device)
        
        # ✅ CNN2 (Private Model) Feature 추출
        feature_private = private_model.extract_features(xt)
        output = proxy_model.fc_forward(feature_private)

        preds_labels = torch.squeeze(torch.max(output, 1)[1])
        acc += torch.sum(preds_labels == yt).item()   

    return acc / x.shape[0]
