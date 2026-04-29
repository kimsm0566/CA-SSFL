import torch
import torchvision
import torchvision.transforms as transforms
import numpy as np
import os

def download_and_save_fashion_mnist_as_npz(save_path='.', file_name='fashion_mnist.npz'):
    """
    FashionMNIST 데이터셋을 다운로드하여 학습 및 테스트 데이터를 .npz 파일로 저장합니다.

    Args:
        save_path (str): .npz 파일을 저장할 디렉토리 경로입니다.
        file_name (str): 저장할 .npz 파일의 이름입니다.
    """
    print("FashionMNIST 데이터셋 다운로드를 시작합니다...")

    # 데이터 전처리: 이미지를 Tensor로 변환하고 Normalize
    # FashionMNIST는 0-255 범위의 흑백 이미지이므로, 0-1 범위로 만들고 평균 0.5, 표준편차 0.5로 정규화 (일반적인 예시)
    # 또는 단순히 ToTensor()만 사용해도 됩니다 (0-1 범위의 Tensor로 변환).
    transform = transforms.Compose([
        transforms.ToTensor(),
        # transforms.Normalize((0.5,), (0.5,)) # 선택 사항: 정규화
    ])

    # 학습 데이터셋 다운로드
    trainset = torchvision.datasets.FashionMNIST(root='/home/imes-server3/E-ProxyFL/datasets',  # 다운로드 받을 로컬 경로
                                                 train=True,
                                                 download=True,
                                                 transform=transform)
    # 테스트 데이터셋 다운로드
    testset = torchvision.datasets.FashionMNIST(root='/home/imes-server3/E-ProxyFL/datasets',
                                                train=False,
                                                download=True,
                                                transform=transform)

    print("데이터셋 다운로드 완료.")
    print("NumPy 배열로 변환 중...")

    # 학습 데이터를 NumPy 배열로 변환
    # trainset.data는 (60000, 28, 28) 형태의 Tensor, trainset.targets는 (60000) 형태의 Tensor
    x_train = trainset.data.numpy()  # 이미지는 원래 0-255 uint8 형태일 수 있음
    y_train = trainset.targets.numpy()

    # 테스트 데이터를 NumPy 배열로 변환
    x_test = testset.data.numpy()
    y_test = testset.targets.numpy()

    # 만약 transform에서 ToTensor()만 사용했다면, x_train, x_test는 이미 0-1 범위의 float32일 수 있습니다.
    # torchvision.datasets.FashionMNIST.data는 기본적으로 PIL Image 또는 Tensor를 반환합니다.
    # .data 속성은 보통 전처리 전의 원본 데이터를 가리키므로, uint8 형태일 가능성이 높습니다.
    # 필요하다면 데이터 타입을 float32로 변경하고 0-1로 스케일링할 수 있습니다.
    # 예: x_train = x_train.astype(np.float32) / 255.0
    #     x_test = x_test.astype(np.float32) / 255.0

    # 채널 차원 추가 (선택 사항, 모델 입력 형태에 따라 다름)
    # FashionMNIST는 흑백이므로 (num_samples, 28, 28) 형태입니다.
    # CNN 등에서 (num_samples, height, width, channels) 또는 (num_samples, channels, height, width)를 요구할 수 있습니다.
    # 여기서는 (num_samples, 28, 28, 1) 형태로 만듭니다.
    if x_train.ndim == 3: # (N, H, W) 형태라면
        x_train = np.expand_dims(x_train, axis=-1) # (N, H, W, C)
    if x_test.ndim == 3:
        x_test = np.expand_dims(x_test, axis=-1)

    print(f"x_train shape: {x_train.shape}, dtype: {x_train.dtype}")
    print(f"y_train shape: {y_train.shape}, dtype: {y_train.dtype}")
    print(f"x_test shape: {x_test.shape}, dtype: {x_test.dtype}")
    print(f"y_test shape: {y_test.shape}, dtype: {y_test.dtype}")

    # .npz 파일로 저장
    full_file_path = os.path.join(save_path, file_name)
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    np.savez_compressed(full_file_path,
                        x_train=x_train,
                        y_train=y_train,
                        x_test=x_test,
                        y_test=y_test)

    print(f"FashionMNIST 데이터셋이 '{full_file_path}' 파일로 저장되었습니다.")
    print("저장된 키: ['x_train', 'y_train', 'x_test', 'y_test']")

if __name__ == '__main__':
    # 현재 스크립트가 있는 위치에 'datasets' 폴더를 만들고 그 안에 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_directory = os.path.join(current_dir, 'datasets')
    download_and_save_fashion_mnist_as_npz(save_path=save_directory)

    # .npz 파일 로드 테스트 (선택 사항)
    # loaded_data = np.load(os.path.join(save_directory, 'fashion_mnist.npz'))
    # print("\n로드된 데이터 키:", list(loaded_data.keys()))
    # print("로드된 x_train shape:", loaded_data['x_train'].shape)