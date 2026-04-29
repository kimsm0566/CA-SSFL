import os
import numpy as np
from statistics import mean

# ==============================
# 실험 조건 직접 설정
# ==============================
config = {
    "dataset": "cifar10",
    "n_clients": 8,
    "n_client_data": 2000,
    "batch_size": 250,
    "optimizer": "adam",
    "lr": 0.001,
    "use_private_SGD": 1,
    "noise_multiplier": 1.0,
    "l2_norm_clip": 1.0,
    "private_model_type": "CNN2",
    "proxy_model_type": "CNN1_classifier",
    "dml_weight": 0.5,
    "alpha": 0.2,
    "beta": 0.5,
    "major_percent": 0.2,
    "n_epochs": 1,
    "n_rounds": 200,
    "algorithm": "PARK",
    "n_seeds": 1,
    "metric_key": "private_accuracies",  # or "proxy_accuracies"
    "root_dir": "/home/imes-server3/ProxyFL/results",
}

# /home/imes-server3/ProxyFL copy/results/cifar10/n_clients_8/data_partition_class/n_client_data_2000/batch_size_250/
# optimizer_adam/lr_0.001/use_private_SGD_1/noise_multiplier_1.0/l2_norm_clip_1.0/private_model_type_CNN2/
# proxy_model_type_CNN1_classifier/dml_weight_0.5/alpha_0.2/beta_0.5/major_percent_0.8/n_epochs_1/n_rounds_200/PARK/seed_0_client_0.log

def build_npz_path(cfg, seed):
    return os.path.join(
        cfg["root_dir"],
        cfg["dataset"],
        f"n_clients_{cfg['n_clients']}",
        "data_partition_class",
        f"n_client_data_{cfg['n_client_data']}",
        f"batch_size_{cfg['batch_size']}",
        f"optimizer_{cfg['optimizer']}",
        f"lr_{cfg['lr']}",
        f"use_private_SGD_{cfg['use_private_SGD']}",
        f"noise_multiplier_{cfg['noise_multiplier']}",
        f"l2_norm_clip_{cfg['l2_norm_clip']}",
        f"private_model_type_{cfg['private_model_type']}",
        f"proxy_model_type_{cfg['proxy_model_type']}",
        f"dml_weight_{cfg['dml_weight']}",
        f"alpha_{cfg['alpha']}",
        f"beta_{cfg['beta']}",
        f"major_percent_{cfg['major_percent']}",
        f"n_epochs_{cfg['n_epochs']}",
        f"n_rounds_{cfg['n_rounds']}",
        cfg["algorithm"],
        f"seed_{seed}.npz"
    )


def load_metric(npz_path, key, last_round=True):
    if not os.path.exists(npz_path):
        print(f"❌ 파일 없음: {npz_path}")
        return None

    try:
        data = np.load(npz_path)
        if key not in data:
            print(f"❗️'{key}' 키 없음 in {npz_path}")
            return None

        arr = data[key]  # shape: (n_clients, n_rounds)
        if arr.ndim != 2:
            print(f"⚠️ 예상 외 차원: {key} shape = {arr.shape}")
            return None

        return arr[:, -1] if last_round else arr.mean(axis=1)
    except Exception as e:
        print(f"⚠️ 로딩 실패: {e}")
        return None


# ==============================
# 분석 실행
# ==============================
config['private_model_type'] = "CNN2"
config['proxy_model_type'] = "CNN1_classifier" # CNN1 # CNN1_classifier
config['dml_weight'] = 0.5
config['alpha'] = 0.5 # 0.8
config['beta'] = 0.5
config['major_percent'] = 0.3 # 0.8
config['algorithm'] = "PARK" # ProxyFL # PARK
config['metric_key'] = "private_accuracies" # private_accuracies # proxy_accuracies
config['root_dir'] = "/home/imes-server3/ProxyFL copy/results"


all_clients_acc = []
for seed in range(0, 6):
    path = build_npz_path(config, seed)
    accs = load_metric(path, key=config["metric_key"])
    if accs is not None:
        all_clients_acc.append(accs)

if all_clients_acc:
    all_clients_acc = np.stack(all_clients_acc)  # (n_seeds, n_clients)
    seed_means = all_clients_acc.mean(axis=1)    # seed별 평균
    overall_mean = seed_means.mean()
    
    print(f"algorithm: {config['algorithm']} / major_percent: {config['major_percent']} / alpha: {config['alpha']}")
    print(f"metric: {config['metric_key']}")
    print(f"✅ 전체 평균 acc (seed×client 평균): {overall_mean:.4f}")
    print(f"   - seed별 평균 acc: {[f'{m:.4f}' for m in seed_means]}")
else:
    print("❌ 수집된 accuracy가 없습니다.")


# services:
#   # 1. PostgreSQL DB
#   helios-db:
#     image: postgres:15-alpine
#     container_name: helios-db
#     environment:
#       - POSTGRES_DB=helios_db      
#       - POSTGRES_USER=helios_user  
#       - POSTGRES_PASSWORD=helios4    
#     ports:
#       - "5432:5432"
#     networks:
#       - helios-network

#   # 2. AI 서버 (FastAPI) 추가
#   helios-ai:
#     platform: linux/arm64
#     build: ./helios_ai # main.py가 있는 폴더 경로 확인
#     container_name: helios-ai
#     ports:
#       - "8000:8000"
#     networks:
#       - helios-network

#   # 3. 백엔드 (Spring Boot)
#   helios-backend:
#     platform: linux/arm64
#     build: ./helios_backend
#     container_name: helios-backend
#     depends_on:
#       - helios-db
#       - helios-ai
#     environment:
#       - SPRING_DATASOURCE_URL=jdbc:postgresql://helios-db:5432/helios_db
#       - SPRING_DATASOURCE_USERNAME=helios_user
#       - SPRING_DATASOURCE_PASSWORD=helios4
#       - AI_SERVER_URL=http://helios-ai:8000 # ✅ 8080에서 8000으로 수정
#     ports:
#       - "8081:8081" # ✅ 백엔드 포트 8081 사용
#     networks:
#       - helios-network

#   # 4. 프론트엔드 (React + Nginx)
#   helios-client:
#     build: ./Heliosclient
#     container_name: helios-client
#     ports:
#       - "3000:80"
#     depends_on:
#       - helios-backend
#     networks:
#       - helios-network

# networks:
#   helios-network:
#     driver: bridge