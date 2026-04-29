import math
import torch
import numpy as np
import torchvision
from sklearn.model_selection import train_test_split # 층화추출(계층적 샘플링)을 위해 import
from sklearn.utils import shuffle # <--- 이 라인 추가!

from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms

CIFAR10_TRAIN_MEAN = np.array((0.4914, 0.4822, 0.4465))[None, :, None, None]
CIFAR10_TRAIN_STD = np.array((0.2470, 0.2435, 0.2616))[None, :, None, None]


def get_data(args):

    if args.dataset == 'mnist' or args.dataset == 'fashion-mnist':

        data_file = f"{args.data_path}/{args.dataset}.npz"
        dataset = np.load(data_file)
        train_X, train_y = dataset['x_train'], dataset['y_train'].astype(np.int64)
        test_X, test_y = dataset['x_test'], dataset['y_test'].astype(np.int64)

        if args.dataset == 'fashion-mnist':
            train_X = np.reshape(train_X, (-1, 1, 28, 28))
            test_X = np.reshape(test_X, (-1, 1, 28, 28))
        else:
            train_X = np.expand_dims(train_X, 1)
            test_X = np.expand_dims(test_X, 1)

    elif args.dataset == 'cifar10' or args.dataset == 'cifar100':

        # Only load data, transformation done later
        if args.dataset == 'cifar10':
            # ★ download=True 추가
            trainset = torchvision.datasets.CIFAR10(root=f"{args.data_path}/{args.dataset}/",
                                                    train=True, download=True)
            testset = torchvision.datasets.CIFAR10(root=f"{args.data_path}/{args.dataset}/",
                                                   train=False, download=True)
        else:
            # ★ download=True 추가 및 CIFAR100으로 수정
            trainset = torchvision.datasets.CIFAR100(root=f"{args.data_path}/{args.dataset}/",
                                                     train=True, download=True)
            # ★ 핵심 버그 수정: 테스트셋도 CIFAR100으로 불러와야 합니다!
            testset = torchvision.datasets.CIFAR100(root=f"{args.data_path}/{args.dataset}/",
                                                    train=False, download=True)

        train_X = trainset.data.transpose([0, 3, 1, 2])
        train_y = np.array(trainset.targets)

        test_X = testset.data.transpose([0, 3, 1, 2])
        test_y = np.array(testset.targets)

    else:

        raise ValueError("Unknown dataset")

    return train_X, train_y, test_X, test_y


def data_loader(dataset, inputs, targets, batch_size, is_train=True):

    def cifar10_norm(x):
        x -= CIFAR10_TRAIN_MEAN
        x /= CIFAR10_TRAIN_STD
        return x

    def no_norm(x):
        return x

    if dataset == 'cifar10':
        norm_func = cifar10_norm
    else:
        norm_func = no_norm

    assert inputs.shape[0] == targets.shape[0]
    n_examples = inputs.shape[0]

    sample_rate = batch_size / n_examples
    num_blocks = int(n_examples / batch_size)
    if is_train:
        for i in range(num_blocks):
            mask = np.random.rand(n_examples) < sample_rate
            if np.sum(mask) != 0:
                yield (norm_func(inputs[mask].astype(np.float32) / 255.),
                       targets[mask])
    else:
        for i in range(num_blocks):
            yield (norm_func(inputs[i * batch_size: (i+1) * batch_size].astype(np.float32) / 255.),
                   targets[i * batch_size: (i+1) * batch_size])
        if num_blocks * batch_size != n_examples:
            yield (norm_func(inputs[num_blocks * batch_size:].astype(np.float32) / 255.),
                   targets[num_blocks * batch_size:])


def partition_data(train_X, train_y, args):
    """
    args.partition_type == 'iid': 균등 분배
    args.partition_type == 'non-iid' (또는 'class'): 디리클레 분포 기반 분배
    args.alpha: Non-IID 정도를 결정 (값이 작을수록 극단적인 Non-IID, 논문 기준 0.5 추천)
    """
    n_train = len(train_X)
    n_clients = args.n_clients
    n_classes = args.n_class
    
    client_data_list =[]
    
    if args.partition_type == 'iid':
        idx = np.arange(n_train)
        np.random.shuffle(idx)
        for i in range(n_clients):
            client_idx = idx[i * args.n_client_data : (i + 1) * args.n_client_data]
            client_data_list.append((train_X[client_idx], train_y[client_idx]))
            
    else: # Non-IID (Dirichlet Distribution)
        # alpha 파라미터가 없으면 0.5를 기본값으로 사용 (작을수록 데이터 불균형 심함)
        alpha = getattr(args, 'alpha', 0.5) 
        
        min_size = 0
        min_require_size = 10 # 클라이언트가 가져야 할 최소 데이터 수
        
        # 클라이언트별로 할당된 데이터 인덱스를 저장할 리스트
        net_dataidx_map = {}

        while min_size < min_require_size:
            idx_batch = [[] for _ in range(n_clients)]
            
            for k in range(n_classes):
                # k번째 클래스에 해당하는 데이터 인덱스 추출
                idx_k = np.where(train_y == k)[0]
                np.random.shuffle(idx_k)
                
                # 각 클라이언트가 k번째 클래스를 얼마나 가져갈지 비율(Proportion)을 디리클레로 뽑음
                proportions = np.random.dirichlet(np.repeat(alpha, n_clients))
                
                # 비율에 따라 데이터 인덱스를 분할
                proportions = np.array([p * (len(idx_j) < args.n_client_data) for p, idx_j in zip(proportions, idx_batch)])
                proportions = proportions / proportions.sum()
                proportions = (np.cumsum(proportions) * len(idx_k)).astype(int)[:-1]
                
                # 잘라낸 인덱스들을 각 클라이언트에게 할당
                idx_batch =[idx_j + idx.tolist() for idx_j, idx in zip(idx_batch, np.split(idx_k, proportions))]
            
            # 클라이언트 중 가장 적은 데이터를 가진 사람의 개수 확인
            min_size = min([len(idx_j) for idx_j in idx_batch])

        # 최종 할당
        for i in range(n_clients):
            # args.n_client_data 갯수만큼만 맞춤 (넘치면 자르고 모자라면 에러 안 나게 처리)
            np.random.shuffle(idx_batch[i])
            client_idx = idx_batch[i][:args.n_client_data]
            client_data_list.append((train_X[client_idx], train_y[client_idx]))
            
    # 호환성을 위해 리턴 형태 유지 (client_major_class_list는 더 이상 안 쓰므로 빈 리스트 반환)
    return client_data_list

# 1. 커스텀 데이터셋 클래스 정의
class CustomTensorDataset(Dataset):
    def __init__(self, data_tensor, target_tensor, transform=None):
        self.data_tensor = data_tensor
        self.target_tensor = target_tensor
        self.transform = transform

    def __getitem__(self, index):
        x = self.data_tensor[index]
        y = self.target_tensor[index]
        
        # Transform 적용 (이미지라면 PIL로 변환 후 적용하거나 Tensor용 Transform 사용)
        if self.transform:
            x = self.transform(x)
            
        return x, y

    def __len__(self):
        return self.data_tensor.size(0)

# 2. get_dataloader 함수 수정
def get_dataloader(data, batch_size, is_train=True):
    X, y = data
    
    # Numpy -> Tensor
    if isinstance(X, np.ndarray):
        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y, dtype=torch.long)
    
    # 0~1 Scaling (필요시)
    if X.max() > 1.0:
        X = X / 255.0

    # =========================================================
    # ★[핵심 수정] 채널 수를 확인하여 MNIST / CIFAR-10 자동 구분
    # =========================================================
    is_mnist = (X.shape[1] == 1)

    if is_mnist:
        # -----------------------------------------------------
        # [1] MNIST용 Transform (1채널, 28x28 -> 32x32)
        # -----------------------------------------------------
        if is_train:
            transform = transforms.Compose([
                transforms.Pad(2), # 28x28을 32x32로 여백을 주어 키움 (ResNet 호환성 완벽 해결)
                # ★ 주의: MNIST는 숫자가 뒤집히면 안 되므로 RandomHorizontalFlip을 쓰지 않음!
                transforms.Normalize((0.5,), (0.5,)) # 1채널 정규화
            ])
        else:
            transform = transforms.Compose([
                transforms.Pad(2), 
                transforms.Normalize((0.5,), (0.5,))
            ])
            
    else:
        # -----------------------------------------------------
        #[2] CIFAR-10용 Transform (3채널, 32x32)
        # -----------------------------------------------------
        if is_train:
            transform = transforms.Compose([
                transforms.RandomCrop(32, padding=4), # 랜덤 크롭
                transforms.RandomHorizontalFlip(),    # 좌우 반전
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
            ])
        else:
            transform = transforms.Compose([
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
            ])

    # Custom Dataset 사용
    dataset = CustomTensorDataset(X, y, transform=transform)
    
    loader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=is_train, 
        drop_last=is_train,
        num_workers=2, # 속도 향상
        pin_memory=True
    )
    return loader

def get_next_batch(dataloader, iterator):
    """
    Iterator가 끝나면 다시 DataLoader를 초기화하여 무한 루프 구현
    """
    try:
        data, target = next(iterator)
    except StopIteration:
        iterator = iter(dataloader)
        data, target = next(iterator)
    return data, target, iterator