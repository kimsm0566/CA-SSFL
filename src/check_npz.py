import numpy as np
import os

# 1. 확인하고 싶은 파일 경로를 입력하세요
file_path = "/home/imes-server4/sunmin/SFL_Semantic/results/cifar10/n_clients_9/n_client_data_5000/batch_size_250/model_type_resnet/major_percent_0.7/beta_0.001/SSFLv2/snr_12/compress_32/seed_2.npz"  # 예: './results/SSFL_snr12_dim64.npz'

if not os.path.exists(file_path):
    print(f"Error: 파일을 찾을 수 없습니다 -> {file_path}")
else:
    # 2. 파일 로드
    data = np.load(file_path)

    print(f"\n📂 File: {file_path}")
    print("=" * 40)

    # 3. 저장된 변수명(Key) 목록 출력
    print(f"🔑 Keys (저장된 변수명): {data.files}")
    print("-" * 40)

    # 4. 각 변수의 상세 정보(Shape, 데이터 타입, 내용 일부) 출력
    for key in data.files:
        val = data[key]
        print(f"🔹 [{key}]")
        print(f"   • Shape: {val.shape}")  # 배열 크기 (예: (10,))
        print(f"   • Dtype: {val.dtype}")  # 데이터 타입 (예: float64)
        
        # 내용이 너무 길면 앞부분만, 짧으면 전체 출력
        if val.size > 10:
            print(f"   • Data (Preview): {val.flatten()[:5]} ... (총 {val.size}개)")
        else:
            print(f"   • Data: {val}")
        print("-" * 20)

    # 5. (선택) 특정 데이터 전체를 보고 싶다면 아래 주석 해제
    # print(data['snr_accs'])