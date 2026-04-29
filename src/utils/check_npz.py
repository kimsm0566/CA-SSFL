import numpy as np
import sys
import os

def check_npz_file(file_path, print_values=True, num_values_to_print=5):
    """
    .npz 파일의 내용을 확인하고 정보를 출력합니다.

    Args:
        file_path (str): 확인할 .npz 파일의 경로.
        print_values (bool): 배열의 일부 값을 출력할지 여부.
        num_values_to_print (int): 출력할 값의 개수.
    """
    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"오류: 파일을 찾을 수 없습니다 - '{file_path}'")
        return

    print(f"--- NPZ 파일 정보: {os.path.basename(file_path)} ---")
    print(f"전체 경로: {os.path.abspath(file_path)}")
    print("-" * 50)

    try:
        # .npz 파일 로드
        data = np.load(file_path, allow_pickle=True)
        
        # 1. 파일 내에 저장된 배열들의 키(이름) 목록 출력
        keys = list(data.keys())
        print(f"저장된 배열 (키): {keys}")
        print(f"총 {len(keys)}개의 배열이 저장되어 있습니다.")
        print("-" * 50)

        # 2. 각 배열의 상세 정보 출력
        for key in keys:
            array = data[key]
            
            # array.item()은 0차원 배열(스칼라)에서 값을 추출할 때 사용
            # 만약 array가 객체 배열이고, 그 안에 딕셔너리 등이 있으면 item()으로 내용 확인
            if array.ndim == 0 and array.item() is not None:
                try:
                    # 0차원 배열에 객체(딕셔너리 등)가 저장된 경우
                    content = array.item()
                    print(f"▶ 키: '{key}'")
                    print(f"  - 타입: {type(content)}")
                    print(f"  - 내용: {content}")
                except Exception:
                    # 일반적인 0차원 배열(스칼라)
                    print(f"▶ 키: '{key}'")
                    print(f"  - 타입: {type(array)} (0-dim array)")
                    print(f"  - Shape: {array.shape}")
                    print(f"  - Dtype: {array.dtype}")
                    print(f"  - 값: {array.item()}")
            else:
                # 1차원 이상의 배열
                print(f"▶ 키: '{key}'")
                print(f"  - 타입: {type(array)}")
                print(f"  - Shape: {array.shape}")
                print(f"  - Dtype: {array.dtype}")
                
                if print_values and array.size > 0:
                    # 배열의 일부 값 출력
                    # 1D 배열이면 앞 부분, 2D 이상이면 슬라이싱하여 보여줌
                    if array.ndim == 1:
                        values_to_show = array[:num_values_to_print]
                        print(f"  - 일부 값 (앞 {num_values_to_print}개): {values_to_show}")
                    else:
                        # 다차원 배열은 복잡하므로 간단히 to-string으로 일부만 보여줌
                        # (너무 길면 잘릴 수 있음)
                        with np.printoptions(threshold=50, edgeitems=2):
                             print(f"  - 일부 값: \n{array}")

            print("-" * 20)
            
        # 로드한 파일 닫기
        data.close()

    except Exception as e:
        print(f"오류: 파일을 로드하거나 분석하는 중 문제가 발생했습니다.")
        print(f"  - 에러 메시지: {e}")

if __name__ == "__main__":
    # --- 사용 방법 ---
    # 1. 스크립트 실행 시 파일 경로를 인자로 전달
    #    예: python check_npz.py /path/to/your/file.npz
    if len(sys.argv) > 1:
        file_to_check = sys.argv[1]
        check_npz_file(file_to_check)
    else:
        # 2. 또는, 이 변수에 직접 파일 경로를 지정
        #    (터미널 인자 없이 실행할 경우)
        file_to_check = "/home/imes-server4/E-ProxyFL/results/cifar10/n_clients_8/data_partition_class/n_client_data_2000/batch_size_250/optimizer_adam/lr_0.001/af_1/use_private_SGD_0/noise_multiplier_1.0/l2_norm_clip_1.0/private_model_type_CNN2/proxy_model_type_CNN1/dml_weight_0.5/major_percent_0.7/n_epochs_1/n_rounds_200/entropy_0.8/private_update_2/PARK/seed_1.npz" # <--- 확인할 파일 경로로 수정하세요!
        print(f"사용법: python {sys.argv[0]} [파일 경로]")
        print(f"기본 파일 경로로 확인을 시도합니다: '{file_to_check}'\n")
        check_npz_file(file_to_check)