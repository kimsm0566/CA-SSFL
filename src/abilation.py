import os
import numpy as np
import csv

def generate_ablation_table():
    # 고정된 경로 (사용자님 환경)
    base_dir = "/home/imes-server4/sunmin/SFL_Semantic/results/cifar10/n_clients_9/n_client_data_3000/batch_size_100/data_partition_type_class/model_type_resnetv2/major_percent_0.7/n_epochs_1"
    algo = "SSFLv4"
    train_snr = 19
    channel_type = "awgn"
    
    # Ablation 대상 하이퍼파라미터 리스트
    betas =[0.01, 0.005, 0.001]
    thresholds =[0.1, 0.05, 0.01, 0.001]
    compress_dims =[64, 128, 256]
    seeds = [1, 2, 3, 4]
    
    results_list =[]

    print("=== Extracting Ablation Study Results ===")
    
    # 3중 루프로 모든 조합 탐색
    for dim in compress_dims:
        for beta in betas:
            for threshold in thresholds:
                
                acc_seeds = []
                comm_seeds =[]
                
                # 각 시드별 결과 로드
                for seed in seeds:
                    file_path = os.path.join(
                        base_dir,
                        f"beta_{beta}",
                        f"pruning_threshold_{threshold}",
                        algo,
                        f"snr_{train_snr}",
                        f"compress_{dim}",
                        f"channel_type_{channel_type}",
                        f"seed_{seed}.npz"
                    )
                    
                    if os.path.exists(file_path):
                        try:
                            data = np.load(file_path)
                            
                            # 정확도
                            if 'train_acc' in data:
                                acc_seeds.append(data['train_acc'][-1])
                            elif 'acc' in data:
                                acc_seeds.append(data['acc'][-1])
                                
                            # 통신량
                            if 'comm' in data:
                                comm_seeds.append(data['comm'][-1])
                                
                        except Exception as e:
                            print(f"[Error] Loading failed: {file_path}")
                
                # 결과가 있으면 리스트에 저장
                if acc_seeds:
                    acc_mean = np.mean(acc_seeds)
                    acc_std = np.std(acc_seeds)
                    
                    comm_mean = np.mean(comm_seeds)
                    comm_std = np.std(comm_seeds)
                    
                    results_list.append({
                        "Compress_Dim": dim,
                        "Beta": beta,
                        "Threshold": threshold,
                        "Accuracy": f"{acc_mean:.2f} ± {acc_std:.2f}",
                        "Comm_Cost": f"{comm_mean:.1f} ± {comm_std:.1f}",
                        "_acc_val": acc_mean # 정렬용 숨김 데이터
                    })
                else:
                    pass # 파일이 없는 경우는 조용히 넘어감

    if not results_list:
        print("\n[Warning] 조건에 맞는 데이터가 하나도 없습니다. 경로를 다시 확인해주세요.")
        return

    # ★ Pandas 없이 파이썬 기본 기능으로 정렬 (차원 오름차순, 정확도 내림차순)
    results_list.sort(key=lambda x: (x["Compress_Dim"], -x["_acc_val"]))

    # 터미널에 예쁘게 표 출력
    print("\n[ Ablation Study Results Table ]")
    print(f"{'Dim':<5} | {'Beta':<7} | {'Threshold':<10} | {'Accuracy (%)':<15} | {'Comm Cost (MB)':<15}")
    print("-" * 65)
    for r in results_list:
        print(f"{r['Compress_Dim']:<5} | {r['Beta']:<7} | {r['Threshold']:<10} | {r['Accuracy']:<15} | {r['Comm_Cost']:<15}")

    # CSV 파일로 저장 (Pandas 없이 csv 모듈 사용)
    save_path = "./ablation_results.csv"
    with open(save_path, mode='w', newline='', encoding='utf-8') as f:
        # 엑셀 헤더 정의
        fieldnames =["Compress_Dim", "Beta", "Threshold", "Accuracy", "Comm_Cost"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore') # _acc_val은 무시하고 저장
        
        writer.writeheader()
        writer.writerows(results_list)
        
    print(f"\n[Saved] 결과가 {save_path} 에 저장되었습니다. 엑셀에서 열어보세요!")

if __name__ == "__main__":
    generate_ablation_table()