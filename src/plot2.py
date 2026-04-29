import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# --- 폰트 및 Matplotlib 전역 설정 ---
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rcParams['axes.unicode_minus'] = False
plt.switch_backend('agg')

# ===================================================================
# [설정] 되찾은 챔피언 세팅 (경로에 맞게 확인하세요)
# ===================================================================
BASE_PATH = './results' 
DATASET = 'cifar10'
N_CLIENTS = 9
N_CLIENT_DATA = 3000
BATCH_SIZE = 100
MAJOR_PERCENT = 0.7
LOCAL_EPOCH = 1
SEEDS =[1, 2, 3, 4]
PARTITION_TYPE = 'class'

# ★ 중요: 학습시켰던 SNR 설정값
TRAIN_SNR = 19   
CHANNEL = 'awgn'

# 🏆 CA-SSFL 대표 세팅 (Champion Setting)
OUR_CHAMPION_DIM = 256
OUR_CHAMPION_BETA = 0.01
OUR_CHAMPION_THRESH = 1.0
OUR_MODEL_TYPE = 'resnetv2'

# ===================================================================
# 1. 데이터 로드 헬퍼 함수
# ===================================================================
def get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold):
    path = os.path.join(
        BASE_PATH,
        DATASET,
        f'n_clients_{N_CLIENTS}',
        f'n_client_data_{N_CLIENT_DATA}',
        f'batch_size_{BATCH_SIZE}',
        f'data_partition_type_{PARTITION_TYPE}',
        f'model_type_{model_type}',
        f'major_percent_{MAJOR_PERCENT}',
        f'n_epochs_{LOCAL_EPOCH}', 
        f'beta_{beta}',
        f'pruning_threshold_{threshold}',
        algo,
        f'snr_{train_snr}',
        f'compress_{compress}',
        f'channel_type_{CHANNEL}',
        f'seed_{seed}.npz'
    )
    return path

def load_data(algo, train_snr, compress, model_type, beta, threshold):
    acc_list, comm_list, snr_accs_list, loss_history_list = [], [], [],[]

    for seed in SEEDS:
        file_path = get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold)
        if not os.path.exists(file_path): continue
            
        try:
            data = np.load(file_path)
            if 'train_acc' in data: acc_list.append(data['train_acc'][-1])
            elif 'acc' in data: acc_list.append(data['acc'][-1])
                
            if 'comm' in data: comm_list.append(data['comm'][-1])
            if 'snr_accs' in data: snr_accs_list.append(data['snr_accs'])
            
            if 'train_loss' in data: loss_history_list.append(data['train_loss'])
            elif 'loss' in data: loss_history_list.append(data['loss'])
        except Exception as e:
            print(f"[Error] Loading {file_path}: {e}")

    return {
        'acc_mean': np.mean(acc_list) if acc_list else 0,
        'acc_std': np.std(acc_list) if acc_list else 0,
        'comm_mean': np.mean(comm_list) if comm_list else 0,
        'comm_std': np.std(comm_list) if comm_list else 0,
        'snr_accs': np.mean(snr_accs_list, axis=0) if snr_accs_list else[],
        'snr_accs_std': np.std(snr_accs_list, axis=0) if snr_accs_list else[],
        'loss_history': np.mean(loss_history_list, axis=0) if loss_history_list else[]
    }

def load_history_data(algo, train_snr, compress, model_type, beta, threshold):
    acc_records, comm_records = [],[]
    min_len = float('inf')

    for seed in SEEDS:
        file_path = get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold)
        if not os.path.exists(file_path): continue
            
        try:
            data = np.load(file_path)
            curr_acc = data['train_acc'] if 'train_acc' in data else data.get('acc', None)
            if curr_acc is None: continue

            curr_comm = data['comm'] if 'comm' in data else np.zeros_like(curr_acc)
                
            acc_records.append(curr_acc)
            comm_records.append(curr_comm)
            min_len = min(min_len, len(curr_acc))
        except Exception:
            pass

    if not acc_records: return None

    acc_records = [arr[:min_len] for arr in acc_records]
    comm_records = [arr[:min_len] for arr in comm_records]

    return {
        'rounds': np.arange(1, min_len + 1),
        'acc_mean': np.mean(np.array(acc_records), axis=0),
        'acc_std': np.std(np.array(acc_records), axis=0),
        'comm_mean': np.mean(np.array(comm_records), axis=0),
        'comm_std': np.std(np.array(comm_records), axis=0)
    }

# ===================================================================
# 2. 시각화 및 표 출력 함수들
# ===================================================================

def print_numerical_results(save_dir):
    """ 터미널에 깔끔한 표 출력 및 CSV 저장 """
    configs =[
        {'algo': 'SFL', 'dim': 64, 'beta': 0.001, 'threshold': OUR_CHAMPION_THRESH, 'model': 'resnet', 'label': 'Standard SFL'},
        {'algo': 'SC-USFL', 'dim': 1352, 'beta': 0.001, 'threshold': OUR_CHAMPION_THRESH, 'model': 'resnet', 'label': 'SC-USFL'},
        {'algo': 'SSFLv4', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL (Ours)'},
        {'algo': 'SSFL_w_o_beta', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o Beta Sched.'},
        {'algo': 'SSFL_w_o_vib', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o VIB'},
        {'algo': 'SSFL_w_o_film', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o FiLM'}
    ]

    table_data =[]
    print("\n" + "="*70)
    print(" "*20 + "[ Final Numerical Results ]")
    print("="*70)

    for c in configs:
        data = load_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'])
        if data['acc_mean'] > 0:
            acc_str = f"{data['acc_mean']:.2f} ± {data['acc_std']:.2f}"
            comm_str = f"{data['comm_mean']:,.1f} ± {data['comm_std']:.1f}"
        else:
            acc_str, comm_str = "-", "-"
            
        table_data.append({'Method': c['label'], 'Test Accuracy (%)': acc_str, 'Total Comm Cost (MB)': comm_str})

    df = pd.DataFrame(table_data)
    print(df.to_string(index=False))
    print("="*70 + "\n")
    df.to_csv(os.path.join(save_dir, 'final_numerical_results.csv'), index=False)

def plot_snr_vs_accuracy_clean(save_dir):
    test_snr_list =[-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]
    plt.figure(figsize=(10, 8)) 

    configs =[
        {'algo': 'SFL', 'dim': 64, 'beta': 0.001, 'threshold': 0.01, 'model': 'resnet', 'label': 'Standard SFL', 'color': 'black', 'marker': 's', 'style': '-.'},
        {'algo': 'SC-USFL', 'dim': 1352, 'beta': 0.001, 'threshold': 0.01, 'model': 'resnet', 'label': 'SC-USFL', 'color': 'blue', 'marker': 'o', 'style': '-'},
        {'algo': 'SSFLv4', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL (Ours)', 'color': 'red', 'marker': 'v', 'style': '-'},
        {'algo': 'SSFL_w_o_beta', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o Beta Sched.', 'color': 'orange', 'marker': '^', 'style': '--'},
        {'algo': 'SSFL_w_o_vib', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o VIB', 'color': 'purple', 'marker': '<', 'style': '--'},
        {'algo': 'SSFL_w_o_film', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o FiLM', 'color': 'brown', 'marker': '>', 'style': '--'}
    ]

    for c in configs:
        data = load_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'])
        if len(data.get('snr_accs', [])) > 0:
            lw = 3 if c['algo'] == 'SSFLv4' else 2
            ms = 10 if c['algo'] == 'SSFLv4' else 8
            plt.plot(test_snr_list, data['snr_accs'], label=c['label'], color=c['color'], marker=c['marker'], linestyle=c['style'], linewidth=lw)

    plt.xlabel('SNR (dB)', fontsize=28, fontweight='bold')
    plt.ylabel('Test Accuracy (%)', fontsize=28, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xticks(test_snr_list, fontsize=26)
    plt.yticks(fontsize=26)
    plt.legend(fontsize=18, ncol=2, loc='lower right', framealpha=0.9)
    plt.tight_layout() # 잘림 방지
    plt.savefig(os.path.join(save_dir, 'snr_vs_accuracy.pdf'), bbox_inches='tight')
    plt.close()

def plot_history_graphs(save_dir):
    configs =[
        {'algo': 'SSFLv4', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL (Ours)', 'color': 'red', 'style': '-'},
        {'algo': 'SFL', 'dim': 64, 'beta': 0.001, 'threshold': OUR_CHAMPION_THRESH, 'model': 'resnet', 'label': 'Standard SFL', 'color': 'black', 'style': '-'},
        {'algo': 'SC-USFL', 'dim': 1352, 'beta': 0.001, 'threshold': OUR_CHAMPION_THRESH, 'model': 'resnet', 'label': 'SC-USFL', 'color': 'blue', 'style': '-'},
        {'algo': 'SSFL_w_o_beta', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o Beta Sched.', 'color': 'orange', 'style': '--'},
        {'algo': 'SSFL_w_o_vib', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o VIB', 'color': 'purple', 'style': '--'},
        {'algo': 'SSFL_w_o_film', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'w/o FiLM', 'color': 'brown', 'style': '--'}
    ]
    
    plt.rcParams['font.size'] = 26
    fig_acc, ax_acc = plt.subplots(figsize=(10, 8))
    fig_eff, ax_eff = plt.subplots(figsize=(10, 8))

    for c in configs:
        stats = load_history_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'])
        if stats is None: continue
            
        rounds = stats['rounds']
        lw = 3 if c['algo'] == 'SSFLv4' else 2
        
        ax_acc.plot(rounds, stats['acc_mean'], label=c['label'], color=c['color'], linewidth=lw, linestyle=c['style'])
        ax_acc.fill_between(rounds, stats['acc_mean'] - stats['acc_std'], stats['acc_mean'] + stats['acc_std'], color=c['color'], alpha=0.1)

        ax_eff.plot(rounds, stats['comm_mean'], label=c['label'], color=c['color'], linewidth=lw, linestyle=c['style'])
        mark_indices = np.linspace(0, len(rounds)-1, 8, dtype=int)
        ax_eff.scatter(rounds[mark_indices], stats['comm_mean'][mark_indices], color=c['color'], s=50 if c['algo']=='SSFLv4' else 30, marker='o')

    # Accuracy Plot 저장
    ax_acc.set_xlabel('Communication Rounds', fontweight='bold')
    ax_acc.set_ylabel('Test Accuracy (%)', fontweight='bold')
    ax_acc.grid(True, linestyle='--', alpha=0.6)
    ax_acc.legend(loc='lower right', fontsize=18, ncol=2)
    fig_acc.tight_layout()
    fig_acc.savefig(os.path.join(save_dir, 'history_accuracy.pdf'), dpi=300, bbox_inches='tight')

    # Efficiency Plot 저장
    ax_eff.set_xlabel('Communication Rounds', fontweight='bold')
    ax_eff.set_ylabel('Cumulative Comm. Cost (MB)', fontweight='bold')
    ax_eff.grid(True, linestyle='--', alpha=0.6)
    ax_eff.legend(loc='upper left', fontsize=18, ncol=2)
    fig_eff.tight_layout()
    fig_eff.savefig(os.path.join(save_dir, 'history_efficiency.pdf'), dpi=300, bbox_inches='tight')
    plt.close('all')

def plot_final_comm_cost_bar(save_dir):
    configs =[
        {'algo': 'SFL', 'dim': 64, 'beta': 0.001, 'threshold': 0.01, 'model': 'resnet', 'label': 'Standard SFL', 'color': 'black'},
        {'algo': 'SC-USFL', 'dim': 1352, 'beta': 0.001, 'threshold': 0.01, 'model': 'resnet', 'label': 'SC-USFL', 'color': 'blue'},
        {'algo': 'SSFLv4', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL\n(Ours)', 'color': 'red'}
    ]

    labels, values, colors = [], [],[]

    for c in configs:
        data = load_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'])
        if data['comm_mean'] > 0:
            labels.append(c['label'])
            values.append(data['comm_mean'])
            colors.append(c['color'])

    if not values: return

    plt.rcParams['font.size'] = 24
    fig, ax = plt.subplots(figsize=(9, 8))
    bars = ax.bar(labels, values, color=colors, edgecolor='black', linewidth=2, alpha=0.8, width=0.6)

    ax.set_ylabel('Total Communication Cost (MB)', fontsize=26, fontweight='bold')
    ax.set_ylim(0, max(values) * 1.25)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 200, f'{int(height):,} MB', ha='center', va='bottom', fontsize=22, fontweight='bold')

    plt.xticks(fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'final_comm_cost_bar.pdf'), dpi=300, bbox_inches='tight')
    plt.close()

# ===================================================================
# Main
# ===================================================================
if __name__ == "__main__":
    output_dir = './results/final_graphs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print("--- Plotting Started ---")
    
    print_numerical_results(output_dir)
    plot_snr_vs_accuracy_clean(output_dir)
    plot_history_graphs(output_dir)
    plot_final_comm_cost_bar(output_dir)
    
    print("\n--- Plotting Finished! Check the 'results/final_graphs' folder ---")