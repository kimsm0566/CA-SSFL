import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image

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
# [설정] 실험 환경에 맞게 이 부분만 확인하세요
# ===================================================================
# BASE_PATH = './old_results2' 
BASE_PATH = './results' 
DATASET = 'cifar100' #'cifar100', 'fashion-mnist'
N_CLIENTS = 9
N_CLIENT_DATA = 3000
BATCH_SIZE = 100
MAJOR_PERCENT = 0.7
LOCAL_EPOCH = 1
SEEDS = [1, 2, 3, 4] #1, 2, 3, 4, 5, 6, 7, 8, 9, 10
PARTITION_TYPE = 'class'

# ★ 중요: 학습시켰던 SNR 설정값
TRAIN_SNR = 12
CHANNEL = 'rayleigh' #'rayleigh' # 'awgn'


# --- [기존] CA-SSFL (Ours) 대표 세팅 ---
OUR_MODEL_TYPE = 'resnetv2'
OUR_CHAMPION_DIM = 4096
OUR_BETA = 0.01
OUR_CHAMPION_THRESH = 1.0
OUR_FILM_MAX_T = 0.7
OUR_FILM_MIN_T = 0.4
ABLATION_FILM_MAX_TS = [ 0.8, OUR_FILM_MAX_T, 0.9]
ABLATION_FILM_MIN_TS = [0.2, OUR_FILM_MIN_T, 0.3]
# --- [신규] Baseline (SFL, SC-USFL) 전용 세팅 ---
BASE_MODEL_TYPE = 'resnet'
BASE_BETA = 0.001
BASE_THRESH = 1.0
BASE_FILM_MAX_T = 0.8
BASE_FILM_MIN_T = 0.3


# ===================================================================
# 1. 데이터 로드 헬퍼 함수
# ===================================================================

def get_result_dir_parts(model_type, beta, threshold):
    return [
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
    ]


def get_file_candidates(algo, train_snr, compress, seed, model_type, beta, threshold, channel_env,
                        film_max_t=OUR_FILM_MAX_T, film_min_t=OUR_FILM_MIN_T):
    base_parts = get_result_dir_parts(model_type, beta, threshold)
    tail_parts = [
        algo,
        f'snr_{train_snr}',
        f'compress_{compress}',
        f'channel_type_{channel_env}',
        f'seed_{seed}.npz',
    ]

    # 신버전 경로를 먼저 확인하고, 없으면 구버전 경로로 fallback합니다.
    return [
        os.path.join(
            *base_parts,
            f'film_max_t_{film_max_t}',
            f'film_min_t_{film_min_t}',
            *tail_parts,
        ),
        os.path.join(*base_parts, *tail_parts),
    ]


def get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold, channel_env,
                  film_max_t=OUR_FILM_MAX_T, film_min_t=OUR_FILM_MIN_T):
    for candidate in get_file_candidates(
        algo, train_snr, compress, seed, model_type, beta, threshold, channel_env, film_max_t, film_min_t
    ):
        if os.path.exists(candidate):
            return candidate

    return get_file_candidates(
        algo, train_snr, compress, seed, model_type, beta, threshold, channel_env, film_max_t, film_min_t
    )[0]

def load_data(algo, train_snr, compress, model_type, beta, threshold, channel_env='awgn', 
              film_max_t=OUR_FILM_MAX_T, film_min_t=OUR_FILM_MIN_T):
    acc_list, comm_list, snr_accs_list, loss_history_list = [], [], [],[]

    for seed in SEEDS:
        file_path = get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold, channel_env, film_max_t, film_min_t)
        
        if not os.path.exists(file_path):
            continue
            
        try:
            data = np.load(file_path)
            if 'train_acc' in data: acc_list.append(data['train_acc'][-1])
            elif 'acc' in data: acc_list.append(data['acc'][-1])
            if 'comm' in data: comm_list.append(data['comm'][-1])
            if 'snr_accs' in data: snr_accs_list.append(data['snr_accs'])
            if 'train_loss' in data: loss_history_list.append(data['train_loss'])
            elif 'loss' in data: loss_history_list.append(data['loss'])
        except Exception:
            pass

    return {
        'acc_mean': np.mean(acc_list) if acc_list else 0,
        'acc_std': np.std(acc_list) if acc_list else 0,
        'comm_mean': np.mean(comm_list) if comm_list else 0,
        'comm_std': np.std(comm_list) if comm_list else 0,
        'snr_accs': np.mean(snr_accs_list, axis=0) if snr_accs_list else[],
        'snr_accs_std': np.std(snr_accs_list, axis=0) if snr_accs_list else[],
        'loss_history': np.mean(loss_history_list, axis=0) if loss_history_list else[]
    }

def load_history_data(algo, train_snr, compress, model_type, beta, threshold, channel, 
                      film_max_t=OUR_FILM_MAX_T, film_min_t=OUR_FILM_MIN_T):
    acc_records = []
    comm_records =[]
    min_len = float('inf')

    for seed in SEEDS:
        file_path = get_file_path(algo, train_snr, compress, seed, model_type, beta, threshold, channel, film_max_t, film_min_t)
        
        if not os.path.exists(file_path):
            continue
            
        try:
            data = np.load(file_path)
            
            if 'train_acc' in data:
                curr_acc = data['train_acc']
            elif 'acc' in data:
                curr_acc = data['acc']
            else:
                continue

            if 'comm' in data:
                curr_comm = data['comm']
            else:
                curr_comm = np.zeros_like(curr_acc)
                
            acc_records.append(curr_acc)
            comm_records.append(curr_comm)
            
            if len(curr_acc) < min_len:
                min_len = len(curr_acc)

        except Exception:
            pass

    if not acc_records:
        return None

    acc_records = [arr[:min_len] for arr in acc_records]
    comm_records = [arr[:min_len] for arr in comm_records]

    acc_matrix = np.array(acc_records)
    comm_matrix = np.array(comm_records)

    return {
        'rounds': np.arange(1, min_len + 1),
        'acc_mean': np.mean(acc_matrix, axis=0),
        'acc_std': np.std(acc_matrix, axis=0),
        'comm_mean': np.mean(comm_matrix, axis=0),
        'comm_std': np.std(comm_matrix, axis=0)
    }


def load_data_from_paths(paths):
    acc_list, comm_list, snr_accs_list = [], [], []

    for file_path in paths:
        if not os.path.exists(file_path):
            continue

        try:
            data = np.load(file_path)
            if 'train_acc' in data:
                acc_list.append(data['train_acc'][-1])
            elif 'acc' in data:
                acc_list.append(data['acc'][-1])
            if 'comm' in data:
                comm_list.append(data['comm'][-1])
            if 'snr_accs' in data:
                snr_accs_list.append(data['snr_accs'])
        except Exception:
            pass

    return {
        'count': len(acc_list),
        'acc_mean': np.mean(acc_list) if acc_list else 0,
        'acc_std': np.std(acc_list) if acc_list else 0,
        'comm_mean': np.mean(comm_list) if comm_list else 0,
        'comm_std': np.std(comm_list) if comm_list else 0,
        'snr_accs': np.mean(snr_accs_list, axis=0) if snr_accs_list else [],
        'snr_accs_std': np.std(snr_accs_list, axis=0) if snr_accs_list else [],
    }


def load_history_data_from_paths(paths):
    acc_records = []
    comm_records = []
    min_len = float('inf')

    for file_path in paths:
        if not os.path.exists(file_path):
            continue

        try:
            data = np.load(file_path)

            if 'train_acc' in data:
                curr_acc = data['train_acc']
            elif 'acc' in data:
                curr_acc = data['acc']
            else:
                continue

            curr_comm = data['comm'] if 'comm' in data else np.zeros_like(curr_acc)

            acc_records.append(curr_acc)
            comm_records.append(curr_comm)
            min_len = min(min_len, len(curr_acc))
        except Exception:
            pass

    if not acc_records:
        return None

    acc_records = [arr[:min_len] for arr in acc_records]
    comm_records = [arr[:min_len] for arr in comm_records]

    acc_matrix = np.array(acc_records)
    comm_matrix = np.array(comm_records)

    return {
        'count': len(acc_records),
        'rounds': np.arange(1, min_len + 1),
        'acc_mean': np.mean(acc_matrix, axis=0),
        'acc_std': np.std(acc_matrix, axis=0),
        'comm_mean': np.mean(comm_matrix, axis=0),
        'comm_std': np.std(comm_matrix, axis=0)
    }


def _benchmark_npz_paths(base_root, n_clients, channel, algorithm, seeds, compressed_dim,
                         semantic_spreading, snr_adaptive_beta, dataset_name='cifar10'):
    paths = []
    for seed in seeds:
        path = os.path.join(
            base_root,
            dataset_name,
            f'n_clients_{n_clients}',
            'n_client_data_3000',
            'batch_size_100',
            'data_partition_type_class',
            'model_type_resnetv2',
            'major_percent_0.8',
            'n_epochs_1',
            'beta_0.01',
            'pruning_threshold_1.0',
            'film_max_t_0.7',
            'film_min_t_0.4',
            f'semantic_spreading_{semantic_spreading}',
            f'snr_adaptive_beta_{snr_adaptive_beta}',
            'semantic_power_0',
            'semantic_power_alpha_2.0',
            algorithm,
            'snr_10',
            f'compress_{compressed_dim}',
            f'channel_type_{channel}',
            f'seed_{seed}.npz',
        )
        paths.append(path)
    return paths


def _benchmark_npz_paths_custom(base_root, n_clients, channel, algorithm, seeds, compressed_dim,
                                beta='0.01', threshold='1.0', film_max='0.7', film_min='0.4',
                                semantic_spreading='0', snr_adaptive_beta='0', dataset_name='cifar10'):
    paths = []
    for seed in seeds:
        path = os.path.join(
            base_root,
            dataset_name,
            f'n_clients_{n_clients}',
            'n_client_data_3000',
            'batch_size_100',
            'data_partition_type_class',
            'model_type_resnetv2',
            'major_percent_0.8',
            'n_epochs_1',
            f'beta_{beta}',
            f'pruning_threshold_{threshold}',
            f'film_max_t_{film_max}',
            f'film_min_t_{film_min}',
            f'semantic_spreading_{semantic_spreading}',
            f'snr_adaptive_beta_{snr_adaptive_beta}',
            'semantic_power_0',
            'semantic_power_alpha_2.0',
            'latent_mixing_0',
            'latent_mixing_strength_0.0',
            'latent_mixing_groups_8',
            'encoder_downsample_0',
            'encoder_downsample_mode_stride2_proj',
            'encoder_downsample_proj_dim_4096',
            'semidense_0',
            'semidense_group_size_16',
            'semidense_group_topk_4',
            'support_floor_0',
            'support_floor_min_active_256',
            'support_floor_snr_db_0.0',
            'importance_repetition_0',
            'importance_repetition_topk_32',
            'base_refinement_0',
            'base_refinement_variable_0',
            'base_refinement_semantic_aware_0',
            'base_support_k_128',
            'refinement_support_k_128',
            'refinement_semantic_weight_0.5',
            'refinement_channel_weight_0.5',
            'csi_source_mask_0',
            'server_feature_impute_0',
            algorithm,
            'snr_10',
            f'compress_{compressed_dim}',
            f'channel_type_{channel}',
            f'seed_{seed}.npz',
        )
        paths.append(path)
    return paths


def _resolve_benchmark_root(preferred_root, fallback_root=None):
    if preferred_root and os.path.exists(preferred_root):
        return preferred_root
    if fallback_root and os.path.exists(fallback_root):
        return fallback_root
    return preferred_root


def _save_png_and_png_matched_pdf(fig, pdf_path, dpi=300, bbox_inches='tight'):
    png_path = pdf_path[:-4] + '.png' if pdf_path.endswith('.pdf') else pdf_path + '.png'
    fig.savefig(png_path, dpi=dpi, bbox_inches=bbox_inches)

    image = Image.open(png_path).convert('RGB')
    image.save(pdf_path, 'PDF', resolution=dpi)


def _plot_benchmark_integrated_from_roots(
    save_dir,
    snr_filename,
    round_filename,
    awgn_root,
    rayleigh_root,
    ca_awgn_root,
    ca_rayleigh_root,
    dataset_name='cifar10',
    ca_beta='0.01',
    ca_threshold='1.0',
    base_awgn_beta='0.01',
    base_awgn_threshold='1.0',
    base_rayleigh_beta='0.01',
    base_rayleigh_threshold='1.0',
    base_awgn_film_max='0.7',
    base_awgn_film_min='0.4',
    base_rayleigh_film_max='0.7',
    base_rayleigh_film_min='0.4',
    base_use_short_paths=False,
    ca_awgn_beta=None,
    ca_awgn_threshold=None,
    ca_rayleigh_beta=None,
    ca_rayleigh_threshold=None,
    ca_awgn_film_max='0.7',
    ca_awgn_film_min='0.2',
    ca_rayleigh_film_max='0.7',
    ca_rayleigh_film_min='0.2',
    snr_ylim=None,
):
    if ca_awgn_beta is None:
        ca_awgn_beta = ca_beta
    if ca_awgn_threshold is None:
        ca_awgn_threshold = ca_threshold
    if ca_rayleigh_beta is None:
        ca_rayleigh_beta = ca_beta
    if ca_rayleigh_threshold is None:
        ca_rayleigh_threshold = ca_threshold

    configs = [
        {
            'label': 'SFL (AWGN)',
            'color': 'black',
            'marker': 's',
            'linestyle': '-',
            'paths': (
                _benchmark_npz_paths(awgn_root, 8, 'awgn', 'SFL', [1, 2, 3, 4], 4096, 0, 0, dataset_name=dataset_name)
                if base_use_short_paths else
                _benchmark_npz_paths_custom(
                    awgn_root, 8, 'awgn', 'SFL', [1, 2, 3, 4], 4096,
                    dataset_name=dataset_name,
                    beta=base_awgn_beta, threshold=base_awgn_threshold, film_max=base_awgn_film_max, film_min=base_awgn_film_min,
                    semantic_spreading='0', snr_adaptive_beta='0'
                )
            ),
        },
        {
            'label': 'SC-USFL (AWGN)',
            'color': 'blue',
            'marker': 'o',
            'linestyle': '-',
            'paths': (
                _benchmark_npz_paths(awgn_root, 8, 'awgn', 'SC-USFL', [1, 2, 3, 4], 1352, 0, 0, dataset_name=dataset_name)
                if base_use_short_paths else
                _benchmark_npz_paths_custom(
                    awgn_root, 8, 'awgn', 'SC-USFL', [1, 2, 3, 4], 1352,
                    dataset_name=dataset_name,
                    beta=base_awgn_beta, threshold=base_awgn_threshold, film_max=base_awgn_film_max, film_min=base_awgn_film_min,
                    semantic_spreading='0', snr_adaptive_beta='0'
                )
            ),
        },
        {
            'label': 'CA-SSFL (AWGN)',
            'color': 'red',
            'marker': 'v',
            'linestyle': '-',
            'paths': _benchmark_npz_paths_custom(
                ca_awgn_root, 8, 'awgn', 'SSFLv6', [1, 2, 3, 4], 4096,
                dataset_name=dataset_name,
                beta=ca_awgn_beta, threshold=ca_awgn_threshold, film_max=ca_awgn_film_max, film_min=ca_awgn_film_min,
                semantic_spreading='0', snr_adaptive_beta='0'
            ),
        },
        {
            'label': 'SFL (Rayleigh)',
            'color': 'black',
            'marker': 's',
            'linestyle': '--',
            'paths': (
                _benchmark_npz_paths(rayleigh_root, 8, 'rayleigh', 'SFL', [1, 2, 3, 4], 4096, 0, 0, dataset_name=dataset_name)
                if base_use_short_paths else
                _benchmark_npz_paths_custom(
                    rayleigh_root, 8, 'rayleigh', 'SFL', [1, 2, 3, 4], 4096,
                    dataset_name=dataset_name,
                    beta=base_rayleigh_beta, threshold=base_rayleigh_threshold, film_max=base_rayleigh_film_max, film_min=base_rayleigh_film_min,
                    semantic_spreading='0', snr_adaptive_beta='0'
                )
            ),
        },
        {
            'label': 'SC-USFL (Rayleigh)',
            'color': 'blue',
            'marker': 'o',
            'linestyle': '--',
            'paths': (
                _benchmark_npz_paths(rayleigh_root, 8, 'rayleigh', 'SC-USFL', [1, 2, 3, 4], 1352, 0, 0, dataset_name=dataset_name)
                if base_use_short_paths else
                _benchmark_npz_paths_custom(
                    rayleigh_root, 8, 'rayleigh', 'SC-USFL', [1, 2, 3, 4], 1352,
                    dataset_name=dataset_name,
                    beta=base_rayleigh_beta, threshold=base_rayleigh_threshold, film_max=base_rayleigh_film_max, film_min=base_rayleigh_film_min,
                    semantic_spreading='0', snr_adaptive_beta='0'
                )
            ),
        },
        {
            'label': 'CA-SSFL (Rayleigh)',
            'color': 'red',
            'marker': 'v',
            'linestyle': '--',
            'paths': _benchmark_npz_paths_custom(
                ca_rayleigh_root, 8, 'rayleigh', 'SSFLv6', [1, 2, 3, 4], 4096,
                dataset_name=dataset_name,
                beta=ca_rayleigh_beta, threshold=ca_rayleigh_threshold, film_max=ca_rayleigh_film_max, film_min=ca_rayleigh_film_min,
                semantic_spreading='0', snr_adaptive_beta='0'
            ),
        },
    ]

    test_snr_list = [-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]
    plt.figure(figsize=(8.5, 6.5))
    all_accs = []
    for config in configs:
        data = load_data_from_paths(config['paths'])
        if len(data.get('snr_accs', [])) == 0:
            continue
        plt.plot(
            test_snr_list,
            data['snr_accs'],
            label=config['label'],
            color=config['color'],
            marker=config['marker'],
            markersize=7,
            linestyle=config['linestyle'],
            linewidth=2.5,
            alpha=0.9,
        )
        all_accs.extend(data['snr_accs'])

    plt.xlabel('SNR (dB)', fontsize=30, fontweight='bold')
    plt.ylabel('Test Accuracy (%)', fontsize=30, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(test_snr_list, fontsize=26)
    plt.yticks(fontsize=26)
    if snr_ylim is not None:
        plt.ylim(*snr_ylim)
    elif all_accs:
        plt.ylim(max(0, min(all_accs) - 3), min(100, max(all_accs) + 3))
    plt.legend(
        fontsize=18,
        ncol=2,
        loc='lower right',
        framealpha=0.85,
        columnspacing=0.8,
        handletextpad=0.5,
        borderpad=0.4,
        labelspacing=0.4,
    )
    plt.tight_layout()
    snr_path = os.path.join(save_dir, snr_filename)
    _save_png_and_png_matched_pdf(plt.gcf(), snr_path, dpi=300, bbox_inches='tight')
    plt.close()

    plt.rcParams['font.size'] = 28
    plt.rcParams['axes.grid'] = True
    fig_acc, ax_acc = plt.subplots(figsize=(8.5, 6.5))
    all_accs = []
    smooth_factor = 0.6
    for config in configs:
        stats = load_history_data_from_paths(config['paths'])
        if stats is None:
            continue

        rounds = stats['rounds']
        raw_mean = stats['acc_mean']
        smoothed_mean = smooth_curve(raw_mean, factor=smooth_factor)

        ax_acc.plot(rounds, raw_mean, color=config['color'], alpha=0.12, linewidth=1)
        ax_acc.plot(
            rounds,
            smoothed_mean,
            label=config['label'],
            color=config['color'],
            linestyle=config['linestyle'],
            linewidth=2.8,
        )
        fill_alpha = 0.12 if config['linestyle'] == '-' else 0.05
        ax_acc.fill_between(
            rounds,
            smoothed_mean - stats['acc_std'],
            smoothed_mean + stats['acc_std'],
            color=config['color'],
            alpha=fill_alpha,
            edgecolor='none',
        )
        all_accs.extend(smoothed_mean)

    ax_acc.set_xlabel('Communication Rounds', fontweight='bold', fontsize=30)
    ax_acc.set_ylabel('Test Accuracy (%)', fontweight='bold', fontsize=30)
    ax_acc.set_xlim(0, 200)
    ax_acc.tick_params(axis='both', which='major', labelsize=26)
    if all_accs:
        ax_acc.set_ylim(max(0, min(all_accs) - 5), min(100, max(all_accs) + 5))
    ax_acc.legend(
        fontsize=16,
        ncol=2,
        loc='lower right',
        framealpha=0.85,
        columnspacing=0.8,
        handletextpad=0.5,
        borderpad=0.4,
        labelspacing=0.4,
    )
    fig_acc.tight_layout()
    round_path = os.path.join(save_dir, round_filename)
    _save_png_and_png_matched_pdf(fig_acc, round_path, dpi=300, bbox_inches='tight')
    plt.close(fig_acc)


def _plot_benchmark_integrated_orig_only(save_dir, snr_filename, round_filename):
    awgn_root = _resolve_benchmark_root(
        '/workspace/tmp/2026-04-09/2026-04-09-awgn-threeway-benchmark-nclients8',
        '/workspace/.tmp_legacy_root_owned/2026-04-09/2026-04-09-awgn-threeway-benchmark-nclients8',
    )
    awgn_blockb_root = _resolve_benchmark_root(
        '/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun',
        None,
    )
    rayleigh_blockb_root = _resolve_benchmark_root(
        '/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun',
        None,
    )
    rayleigh_root = _resolve_benchmark_root(
        '/workspace/tmp/2026-04-09/2026-04-09-rayleigh-cross-benchmark-nclients8',
        '/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8',
    )

    _plot_benchmark_integrated_from_roots(
        save_dir,
        snr_filename,
        round_filename,
        awgn_root=awgn_root,
        rayleigh_root=rayleigh_root,
        ca_awgn_root=awgn_blockb_root,
        ca_rayleigh_root=rayleigh_blockb_root,
        dataset_name='cifar10',
        ca_beta='0.01',
        ca_threshold='1.0',
        base_awgn_beta='0.01',
        base_awgn_threshold='1.0',
        base_rayleigh_beta='0.01',
        base_rayleigh_threshold='1.0',
        base_awgn_film_max='0.7',
        base_awgn_film_min='0.4',
        base_rayleigh_film_max='0.7',
        base_rayleigh_film_min='0.4',
        base_use_short_paths=True,
        ca_awgn_beta='0.05',
        ca_awgn_threshold='1.0',
        ca_rayleigh_beta='0.1',
        ca_rayleigh_threshold='1.0',
        ca_awgn_film_max='0.7',
        ca_awgn_film_min='0.2',
        ca_rayleigh_film_max='0.7',
        ca_rayleigh_film_min='0.4',
        snr_ylim=(30, 55),
    )


def plot_current_benchmark_integrated_snr_vs_accuracy(save_dir):
    test_snr_list = [-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]
    plt.figure(figsize=(8.5, 6.5))
    all_accs = []

    configs = [
        {
            'label': 'SFL (AWGN)',
            'color': 'black',
            'marker': 's',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SFL', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SC-USFL (AWGN)',
            'color': 'blue',
            'marker': 'o',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SC-USFL', [1,2,3,4], 1352, 0, 0),
        },
        {
            'label': 'CA-SSFL New (AWGN)',
            'color': 'red',
            'marker': 'v',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SSFLv6', [1,2,3,4], 4096, 1, 1),
        },
        {
            'label': 'CA-SSFL Orig (AWGN)',
            'color': 'darkred',
            'marker': '^',
            'linestyle': '-.',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SSFLv6', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SFL (Rayleigh)',
            'color': 'black',
            'marker': 's',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SFL', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SC-USFL (Rayleigh)',
            'color': 'blue',
            'marker': 'o',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SC-USFL', [1,2,3,4], 1352, 0, 0),
        },
        {
            'label': 'CA-SSFL Orig (Rayleigh)',
            'color': 'darkred',
            'marker': '^',
            'linestyle': '-.',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SSFLv6', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'CA-SSFL New (Rayleigh)',
            'color': 'red',
            'marker': 'v',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SSFLv6', [1,2,3,4], 4096, 1, 1),
        },
    ]

    for config in configs:
        data = load_data_from_paths(config['paths'])
        if len(data.get('snr_accs', [])) == 0:
            continue
        plt.plot(
            test_snr_list,
            data['snr_accs'],
            label=f"{config['label']} (n={data['count']})",
            color=config['color'],
            marker=config['marker'],
            markersize=7,
            linestyle=config['linestyle'],
            linewidth=2.5,
            alpha=0.9,
        )
        all_accs.extend(data['snr_accs'])

    plt.xlabel('SNR (dB)', fontsize=26, fontweight='bold')
    plt.ylabel('Test Accuracy (%)', fontsize=26, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(test_snr_list, fontsize=22)
    plt.yticks(fontsize=22)
    if all_accs:
        plt.ylim(max(0, min(all_accs) - 5), min(100, max(all_accs) + 5))
    plt.legend(fontsize=16, ncol=2, loc='lower right', framealpha=0.5)
    plt.tight_layout()

    save_path = os.path.join(save_dir, 'current_integrated_snr_vs_accuracy.pdf')
    plt.savefig(save_path)
    plt.close()
    print(f"[Saved] {save_path}")


def plot_current_benchmark_integrated_round_vs_accuracy(save_dir):
    plt.rcParams['font.size'] = 26
    plt.rcParams['axes.grid'] = True

    fig_acc, ax_acc = plt.subplots(figsize=(8.5, 6.5))
    all_accs = []
    smooth_factor = 0.6

    configs = [
        {
            'label': 'SFL (AWGN)',
            'color': 'black',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SFL', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SC-USFL (AWGN)',
            'color': 'blue',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SC-USFL', [1,2,3,4], 1352, 0, 0),
        },
        {
            'label': 'CA-SSFL New (AWGN)',
            'color': 'red',
            'linestyle': '-',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SSFLv6', [1,2,3,4], 4096, 1, 1),
        },
        {
            'label': 'CA-SSFL Orig (AWGN)',
            'color': 'darkred',
            'linestyle': '-.',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8', 8, 'awgn', 'SSFLv6', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SFL (Rayleigh)',
            'color': 'black',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SFL', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'SC-USFL (Rayleigh)',
            'color': 'blue',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SC-USFL', [1,2,3,4], 1352, 0, 0),
        },
        {
            'label': 'CA-SSFL Orig (Rayleigh)',
            'color': 'darkred',
            'linestyle': '-.',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SSFLv6', [1,2,3,4], 4096, 0, 0),
        },
        {
            'label': 'CA-SSFL New (Rayleigh)',
            'color': 'red',
            'linestyle': '--',
            'paths': _benchmark_npz_paths('/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8', 8, 'rayleigh', 'SSFLv6', [1,2,3,4], 4096, 1, 1),
        },
    ]

    for config in configs:
        stats = load_history_data_from_paths(config['paths'])
        if stats is None:
            continue

        rounds = stats['rounds']
        raw_mean = stats['acc_mean']
        smoothed_mean = smooth_curve(raw_mean, factor=smooth_factor)

        ax_acc.plot(rounds, raw_mean, color=config['color'], alpha=0.12, linewidth=1)
        ax_acc.plot(
            rounds,
            smoothed_mean,
            label=f"{config['label']} (n={stats['count']})",
            color=config['color'],
            linestyle=config['linestyle'],
            linewidth=2.8,
        )
        fill_alpha = 0.12 if config['linestyle'] == '-' else 0.05
        ax_acc.fill_between(
            rounds,
            smoothed_mean - stats['acc_std'],
            smoothed_mean + stats['acc_std'],
            color=config['color'],
            alpha=fill_alpha,
            edgecolor='none',
        )
        all_accs.extend(smoothed_mean)

    ax_acc.set_xlabel('Communication Rounds', fontweight='bold', fontsize=28)
    ax_acc.set_ylabel('Test Accuracy (%)', fontweight='bold', fontsize=28)
    ax_acc.set_xlim(0, 200)
    ax_acc.tick_params(axis='both', which='major', labelsize=24)
    if all_accs:
        ax_acc.set_ylim(max(0, min(all_accs) - 5), min(100, max(all_accs) + 5))
    ax_acc.legend(fontsize=16, ncol=2, loc='lower right', framealpha=0.5)

    fig_acc.tight_layout()
    save_path = os.path.join(save_dir, 'current_integrated_history_accuracy_smoothed.pdf')
    fig_acc.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig_acc)
    print(f"[Saved] {save_path}")

# ===================================================================
# 2. 그래프 그리기 함수들 (레이아웃 보존)
# ===================================================================
def plot_snr_vs_accuracy_clean(save_dir):
    test_snr_list =[-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]
    
    plt.figure(figsize=(8, 6))

    # 1. Standard SFL
    sfl_data = load_data('SFL', TRAIN_SNR, 64, 'resnet', BASE_BETA, BASE_THRESH, CHANNEL)
    if len(sfl_data.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, sfl_data['snr_accs'], 
                 label='SFL', color='black', 
                 marker='s', markersize=8, linestyle='-.', linewidth=2)
    
    # 2. CA-SSFL (Ours) - Champion 세팅만
    ours_data = load_data('SSFLv6', TRAIN_SNR, OUR_CHAMPION_DIM, OUR_MODEL_TYPE, OUR_BETA, OUR_CHAMPION_THRESH, CHANNEL)
    if len(ours_data.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, ours_data['snr_accs'], 
                 label='CA-SSFL (Ours)', color='red', 
                 marker='v', markersize=8, linestyle='--', linewidth=2, alpha=0.9)
        
    # 3. SC-USFL
    sc_data = load_data('SC-USFL', TRAIN_SNR, 1352, 'resnet', BASE_BETA, BASE_THRESH, CHANNEL)
    if len(sc_data.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, sc_data['snr_accs'], 
                 label='SC-USFL', color='blue', 
                 marker='o', markersize=8, linestyle='-', linewidth=2, alpha=0.9)

    plt.xlabel('SNR (dB)', fontsize=28, fontweight='bold')
    plt.ylabel('Test Accuracy (%)', fontsize=28, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.xticks(test_snr_list, fontsize=26)
    plt.yticks(fontsize=26)
    plt.ylim(30, 65)
    plt.legend(fontsize=25, ncol=1, loc='lower right', framealpha=0.9)
    plt.tight_layout()
    
    save_path = os.path.join(save_dir, 'snr_vs_accuracy.pdf')
    plt.savefig(save_path)
    plt.close()
    print(f"[Saved] {save_path}")

def plot_integrated_snr_vs_accuracy(save_dir):
    test_snr_list =[-6, -4, -2, 0, 2, 4, 6, 8, 10, 12]
    
    plt.figure(figsize=(8, 6)) # 선이 많아지므로 가로를 약간 넓힘
    all_accs = []

    # =======================================================
    # [AWGN Channel] - 실선 (Solid Line)
    # =======================================================
    # 1. SFL (AWGN)
    sfl_awgn = load_data('SFL', TRAIN_SNR, 64, BASE_MODEL_TYPE, BASE_BETA, BASE_THRESH, 'awgn',
                         film_max_t=0.8, film_min_t=0.3)    
    if len(sfl_awgn.get('snr_accs', [])) > 0:
        plt.plot(test_snr_list, sfl_awgn['snr_accs'], label='SFL (AWGN)', 
                 color='black', marker='s', markersize=8, linestyle='-', linewidth=2.5)
        all_accs.extend(sfl_awgn['snr_accs'])
    # 2. SC-USFL (AWGN)
    sc_awgn = load_data('SC-USFL', TRAIN_SNR, 1352, BASE_MODEL_TYPE, BASE_BETA, BASE_THRESH, 'awgn',
                        film_max_t=0.8, film_min_t=0.3)
    if len(sc_awgn.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, sc_awgn['snr_accs'], label='SC-USFL (AWGN)', 
                 color='blue', marker='o', markersize=8, linestyle='-', linewidth=2.5, alpha=0.8)
        all_accs.extend(sc_awgn['snr_accs'])

    # 3. CA-SSFL (AWGN)
    ours_awgn = load_data('SSFLv6', TRAIN_SNR, OUR_CHAMPION_DIM, OUR_MODEL_TYPE, OUR_BETA, OUR_CHAMPION_THRESH, 'awgn',
                          film_max_t=OUR_FILM_MAX_T, film_min_t=OUR_FILM_MIN_T)
    if len(ours_awgn.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, ours_awgn['snr_accs'], label='CA-SSFL (AWGN)', 
                 color='red', marker='v', markersize=8, linestyle='-', linewidth=2.5)
        all_accs.extend(ours_awgn['snr_accs'])

    # =======================================================
    # [Rayleigh Channel] - 점선 (Dashed Line)
    # =======================================================
    # 1. SFL (Rayleigh)
    sfl_ray = load_data('SFL', TRAIN_SNR, 64, BASE_MODEL_TYPE, BASE_BETA, BASE_THRESH, 'rayleigh',
                         film_max_t=0.8, film_min_t=0.3)  
    if len(sfl_ray.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, sfl_ray['snr_accs'], label='SFL (Rayleigh)', 
                 color='black', marker='s', markerfacecolor='white', markersize=8, linestyle='--', linewidth=2.5)
        all_accs.extend(sfl_ray['snr_accs'])

    # 2. SC-USFL (Rayleigh)
    sc_ray = load_data('SC-USFL', TRAIN_SNR, 1352, BASE_MODEL_TYPE, BASE_BETA, BASE_THRESH, 'rayleigh',
                        film_max_t=0.8, film_min_t=0.3)
    if len(sc_ray.get('snr_accs',[])) > 0:
        plt.plot(test_snr_list, sc_ray['snr_accs'], label='SC-USFL (Rayleigh)', 
                 color='blue', marker='o', markerfacecolor='white', markersize=8, linestyle='--', linewidth=2.5, alpha=0.8)
        all_accs.extend(sc_ray['snr_accs'])

    # 3. CA-SSFL (Rayleigh)
    ours_ray = load_data('SSFLv6', TRAIN_SNR, OUR_CHAMPION_DIM, OUR_MODEL_TYPE, 0.005, OUR_CHAMPION_THRESH, 'rayleigh',
                          film_max_t=0.8, film_min_t=0.3)
    if len(ours_ray.get('snr_accs', [])) > 0:
        plt.plot(test_snr_list, ours_ray['snr_accs'], label='CA-SSFL (Rayleigh)', 
                 color='red', marker='v', markerfacecolor='white', markersize=8, linestyle='--', linewidth=2.5)
        all_accs.extend(ours_ray['snr_accs'])
    # =======================================================
    # 축 및 디자인 설정
    # =======================================================
    plt.xlabel('SNR (dB)', fontsize=26, fontweight='bold')
    plt.ylabel('Test Accuracy (%)', fontsize=26, fontweight='bold')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(test_snr_list, fontsize=22)
    plt.yticks(fontsize=22)
    
    # 동적 Y축 설정 (위아래 5% 여백)
    if all_accs:
        plt.ylim(max(0, min(all_accs)-5), min(100, max(all_accs)+5))

    # 범례 설정 (2줄로 나누어 공간 절약)
    plt.legend(fontsize=18, ncol=2, loc='lower right', framealpha=0.5)
    plt.tight_layout()
    
    save_path = os.path.join(save_dir, 'integrated_snr_vs_accuracy.pdf')
    plt.savefig(save_path)
    plt.close()
    print(f"[Saved] {save_path}")


def generate_ablation_table(save_dir):
    """
    Phase 1 (VIB)과 Phase 2 (FiLM)에 대한 두 개의 Ablation Table을 생성합니다.
    """
    print("\n>>> Ablation Study 데이터를 불러오는 중...")

    dim = 4096

    # 데이터 로드 및 통계 계산을 위한 내부 헬퍼 함수
    def get_results(beta, thresh, film_max_t, film_min_t):
        acc_list, comm_list = [], []
        for seed in SEEDS:
            path = get_file_path(
                'SSFLv6',
                TRAIN_SNR,
                dim,
                seed,
                OUR_MODEL_TYPE,
                beta,
                thresh,
                CHANNEL,
                film_max_t=film_max_t,
                film_min_t=film_min_t,
            )
            if os.path.exists(path):
                try:
                    data = np.load(path)
                    if 'acc' in data: acc_list.append(data['acc'][-1])
                    elif 'train_acc' in data: acc_list.append(data['train_acc'][-1])
                    
                    if 'comm' in data: comm_list.append(data['comm'][-1])
                except Exception:
                    pass
        
        if acc_list:
            return (f"{np.mean(acc_list):.2f} ± {np.std(acc_list):.2f}",
                    f"{np.mean(comm_list):.1f} ± {np.std(comm_list):.1f}")
        return None, None

    # =====================================================================
    # [Table 1] Phase 1: VIB Tuning (Beta & Threshold)
    # =====================================================================
    vib_betas = [0.1, 0.05, 0.01, 0.005, 0.001]
    vib_thresholds = [1.5, 1.0, 0.5]
    
    # Phase 1 고정값
    fixed_film_max = 0.7
    fixed_film_min = 0.4

    vib_table_data = []
    for beta in vib_betas:
        for thresh in vib_thresholds:
            acc_str, comm_str = get_results(beta, thresh, fixed_film_max, fixed_film_min)
            if acc_str:
                vib_table_data.append({
                    'Dim': dim,
                    'Beta': beta,
                    'Threshold': thresh,
                    'Accuracy (%)': acc_str,
                    'Comm Cost (MB)': comm_str
                })

    df_vib = pd.DataFrame(vib_table_data)

    # =====================================================================
    # [Table 2] Phase 2: FiLM Tuning (Max T & Min T)
    # =====================================================================
    film_betas = [0.01, 0.005]
    film_max_ts = [0.7, 0.8, 0.9]
    film_min_ts = [0.2, 0.3, 0.4]
    
    # Phase 2 고정값
    # fixed_thresh = 1.0
    vib_thresholds = [1.0] # VIB Threshold는 고정 (1.0)으로 설정하여 FiLM 파라미터 변화에 따른 영향만 평가

    film_table_data = []
    for thresh in vib_thresholds:
        for beta in film_betas:
            for f_max in film_max_ts:
                for f_min in film_min_ts:
                    acc_str, comm_str = get_results(beta, thresh, f_max, f_min)
                    if acc_str:
                        film_table_data.append({
                            'Dim': dim,
                            'Beta': beta,
                            'FiLM Max T': f_max,
                            'FiLM Min T': f_min,
                            'Accuracy (%)': acc_str,
                            'Comm Cost (MB)': comm_str
                        })

    df_film = pd.DataFrame(film_table_data)

    # =====================================================================
    # 출력 및 저장
    # =====================================================================
    
    # 1. VIB 테이블 출력
    print("\n" + "="*80)
    print(" "*15 + "[ Table 1: VIB Ablation Study (Beta & Threshold) ]")
    print(f" "*15 + f"(Fixed FiLM settings -> Max T: {fixed_film_max}, Min T: {fixed_film_min})")
    print("="*80)
    if not df_vib.empty:
        print(df_vib.to_string(index=False))
    else:
        print("No data found for Table 1.")
    print("="*80 + "\n")

    # 2. FiLM 테이블 출력
    print("\n" + "="*80)
    print(" "*15 + "[ Table 2: FiLM Ablation Study (Max T & Min T) ]")
    print(f" "*15 + f"(Fixed VIB setting -> Threshold: {1.0, 1.5})")
    print("="*80)
    if not df_film.empty:
        print(df_film.to_string(index=False))
    else:
        print("No data found for Table 2.")
    print("="*80 + "\n")

    # 3. CSV 파일로 각각 저장
    if not df_vib.empty:
        vib_csv_path = os.path.join(save_dir, 'ablation_table_1_VIB.csv')
        df_vib.to_csv(vib_csv_path, index=False)
        
    if not df_film.empty:
        film_csv_path = os.path.join(save_dir, 'ablation_table_2_FiLM.csv')
        df_film.to_csv(film_csv_path, index=False) 
def plot_final_comm_cost_bar_grouped(save_dir):
    configs =[
        {
            'algo': 'SFL', 'dim': 64, 'beta': BASE_BETA, 'threshold': BASE_THRESH, 
            'model': 'resnet', 'label': 'Standard SFL', 'color': '#555555' # 진한 회색
        },
        {
            'algo': 'SC-USFL', 'dim': 1352, 'beta': BASE_BETA, 'threshold': BASE_THRESH, 
            'model': 'resnet', 'label': 'SC-USFL', 'color': 'royalblue'
        },
        {
            'algo': 'SSFLv6', 'dim': OUR_CHAMPION_DIM, 'beta': OUR_BETA, 'threshold': OUR_CHAMPION_THRESH, 
            'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL\n(Ours)', 'color': 'red'
        }
    ]

    channels = ['awgn', 'rayleigh'] #'awgn', 
    labels, colors = [],[]
    comm_data = {'awgn': [], 'rayleigh':[]}

    print(">>> 채널별 그룹 막대 그래프용 통신량 데이터 로드 중 (GB 단위 변환)...")

    # 파일에서 데이터 읽기 (명시적으로 channel_type 전달!)
    for c in configs:
        labels.append(c['label'])
        colors.append(c['color'])
        
        for ch in channels:
            # ★ load_data의 마지막 인자로 채널명(ch)을 확실하게 넘겨줌!
            data = load_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'], channel_env=ch)
            
            if data['comm_mean'] > 0:
                # ★ [수정 1] MB 단위를 GB로 변환 (1024로 나눔)
                gb_val = data['comm_mean'] / 1024.0
                comm_data[ch].append(gb_val)
            else:
                comm_data[ch].append(0)
                print(f"[Warning] 데이터를 찾을 수 없음: {c['algo']} ({ch})")

    # 그래프 그리기
    plt.rcParams['font.size'] = 24
    fig, ax = plt.subplots(figsize=(10, 8))

    x = np.arange(len(labels))
    width = 0.35

    # AWGN 막대
    bars_awgn = ax.bar(x - width/2, comm_data['awgn'], width, 
                       color=colors, edgecolor='black', linewidth=2, alpha=0.8)
    
    # Rayleigh 막대 (빗금)
    bars_ray = ax.bar(x + width/2, comm_data['rayleigh'], width, 
                      color=colors, edgecolor='black', linewidth=2, alpha=0.8, hatch='///')

    # ★ [수정 2] Y축 레이블을 GB로 변경
    ax.set_ylabel('Total Communication Cost (GB)', fontsize=26, fontweight='bold')
    
    # max_val = max(max(comm_data['awgn']), max(comm_data['rayleigh']))
    max_val = max(comm_data['rayleigh'])
    ax.set_ylim(0, max_val * 1.25)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                # ★ [수정 3] GB 단위이므로 소수점 둘째 자리까지 표기 (예: 15.03)
                ax.text(bar.get_x() + bar.get_width()/2., height + (max_val * 0.02),
                        f'{height:.2f}', 
                        ha='center', va='bottom', fontsize=18, fontweight='bold', rotation=30)

    add_labels(bars_awgn)
    add_labels(bars_ray)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontweight='bold', fontsize=22)

    legend_elements =[
        mpatches.Patch(facecolor='lightgray', edgecolor='black', alpha=0.8, label='AWGN Channel'),
        mpatches.Patch(facecolor='lightgray', edgecolor='black', alpha=0.8, hatch='///', label='Rayleigh Channel')
    ]
    ax.legend(handles=legend_elements, fontsize=20, loc='upper right')

    plt.tight_layout()
    save_path = os.path.join(save_dir, 'final_comm_cost_bar_grouped.pdf')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[Saved] {save_path}")

def smooth_curve(points, factor=0.7):
    """
    TensorBoard 스타일의 지수 이동 평균(EMA) 스무딩 함수.
    factor가 0에 가까울수록 원본 유지, 1에 가까울수록 부드러워짐 (추천: 0.7~0.8)
    """
    smoothed_points =[]
    for point in points:
        if smoothed_points:
            previous = smoothed_points[-1]
            smoothed_points.append(previous * factor + point * (1 - factor))
        else:
            smoothed_points.append(point)
    return np.array(smoothed_points)


def plot_integrated_round_vs_accuracy_smoothed(save_dir):
    plt.rcParams['font.size'] = 26
    plt.rcParams['axes.grid'] = True
    
    fig_acc, ax_acc = plt.subplots(figsize=(8, 6))
    print("\n>>> Integrated Learning Curves 생성 중 (알고리즘별 개별 경로 적용)...")

    SMOOTH_FACTOR = 0.6
    all_accs = []

    # =========================================================================
    # [설정] Baseline 전용 (SC-USFL, SFL용) 파라미터 정의
    # =========================================================================
    BASE_F_MAX = 0.8
    BASE_F_MIN = 0.3

    # =========================================================================
    # [헬퍼 함수] f_max, f_min 인자를 추가하여 개별 경로를 탐색하게 수정
    # =========================================================================
    def draw_convergence_line(algo, dim, model, beta, thresh, channel, 
                              color, label, linestyle, marker, is_filled,
                              f_max, f_min): # f_max, f_min 인자 추가
        
        # load_history_data에 f_max와 f_min을 명시적으로 전달
        stats = load_history_data(algo, TRAIN_SNR, dim, model, beta, thresh, channel,
                                  film_max_t=f_max, film_min_t=f_min)
        
        if stats is None:
            print(f"[Warning] {label} 데이터를 찾을 수 없어 건너뜜 (경로 확인 필요)")
            return
            
        rounds = stats['rounds']
        raw_mean = stats['acc_mean']
        std_acc = stats['acc_std']
        
        # 1. 스무딩 적용
        smoothed_mean = smooth_curve(raw_mean, factor=SMOOTH_FACTOR)
        
        # 2. 원본 데이터는 투명하게 깔아줌
        ax_acc.plot(rounds, raw_mean, color=color, alpha=0.15, linewidth=1)
        
        # 3. 부드러운 스무딩 선을 메인으로 그림
        ax_acc.plot(rounds, smoothed_mean, label=label, color=color, 
                    linestyle=linestyle, linewidth=3, 
                    marker=marker, markevery=30, markersize=8) # 가독성을 위해 마커 크기 조정
        
        # 4. 표준편차 그림자
        alpha_fill = 0.12 if is_filled else 0.05
        ax_acc.fill_between(rounds, smoothed_mean - std_acc, smoothed_mean + std_acc, 
                            color=color, alpha=alpha_fill, edgecolor='none')
        
        all_accs.extend(smoothed_mean)

    # =======================================================
    # [AWGN Channel] 호출부
    # =======================================================
    # 1. SFL (Baseline 설정: 0.8 / 0.3)
    draw_convergence_line('SFL', 64, 'resnet', BASE_BETA, BASE_THRESH, 'awgn',
                          'black', 'SFL (AWGN)', '-', 's', True,
                          f_max=BASE_F_MAX, f_min=BASE_F_MIN)
                     
    # 2. SC-USFL (Baseline 설정: 0.8 / 0.3)
    draw_convergence_line('SC-USFL', 1352, 'resnet', BASE_BETA, BASE_THRESH, 'awgn',
                          'blue', 'SC-USFL (AWGN)', '-', 'o', True,
                          f_max=BASE_F_MAX, f_min=BASE_F_MIN)
                     
    # 3. CA-SSFL (Ours 설정: 0.7 / 0.4)
    draw_convergence_line('SSFLv6', OUR_CHAMPION_DIM, OUR_MODEL_TYPE, OUR_BETA, OUR_CHAMPION_THRESH, 'awgn',
                          'red', 'CA-SSFL (AWGN)', '-', 'v', True,
                          f_max=OUR_FILM_MAX_T, f_min=OUR_FILM_MIN_T)

    # =======================================================
    # [Rayleigh Channel] 호출부
    # =======================================================
    # 1. SFL (Baseline 설정: 0.8 / 0.3)
    draw_convergence_line('SFL', 64, 'resnet', BASE_BETA, BASE_THRESH, 'rayleigh',
                          'black', 'SFL (Rayleigh)', '--', 's', False,
                          f_max=BASE_F_MAX, f_min=BASE_F_MIN)
                     
    # 2. SC-USFL (Baseline 설정: 0.8 / 0.3)
    draw_convergence_line('SC-USFL', 1352, 'resnet', BASE_BETA, BASE_THRESH, 'rayleigh',
                          'blue', 'SC-USFL (Rayleigh)', '--', 'o', False,
                          f_max=BASE_F_MAX, f_min=BASE_F_MIN)
                     
    # 3. CA-SSFL (Ours 설정: 0.7 / 0.4)
    draw_convergence_line('SSFLv6', OUR_CHAMPION_DIM, OUR_MODEL_TYPE, 0.005, OUR_CHAMPION_THRESH, 'rayleigh',
                          'red', 'CA-SSFL (Rayleigh)', '--', 'v', False,
                          f_max=0.8, f_min=0.3)

    # =======================================================
    # 축 및 디자인 설정
    # =======================================================
    ax_acc.set_xlabel('Communication Rounds', fontweight='bold', fontsize=28)
    ax_acc.set_ylabel('Test Accuracy (%)', fontweight='bold', fontsize=28)
    ax_acc.set_xlim(0, 200)
    ax_acc.tick_params(axis='both', which='major', labelsize=24)
    
    if all_accs:
        y_min = max(0, min(all_accs) - 5)
        y_max = min(100, max(all_accs) + 5)
        ax_acc.set_ylim(y_min, y_max)

    # 범례 설정 (2줄)
    ax_acc.legend(fontsize=17, ncol=2, loc='lower right', framealpha=0.5)
    
    fig_acc.tight_layout()
    
    save_path = os.path.join(save_dir, 'integrated_history_accuracy_smoothed.pdf')
    fig_acc.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig_acc)
    print(f">>> [완료] 알고리즘별 개별 설정이 적용된 그래프가 저장되었습니다: {save_path}")
    
def plot_history_graphs(save_dir):
    configs =[
        {'algo': 'SFL', 'snr': TRAIN_SNR, 'dim': 64, 'model_type': 'resnet', 'beta': BASE_BETA, 'threshold': BASE_THRESH, 'label': 'SFL', 'color': 'black', 'style': '-'},
        {'algo': 'SC-USFL', 'snr': TRAIN_SNR, 'dim': 1352, 'model_type': 'resnet', 'beta': BASE_BETA, 'threshold': BASE_THRESH, 'label': 'SC-USFL', 'color': 'blue', 'style': '-'},
        # {'algo': 'FL', 'snr': TRAIN_SNR, 'dim': 64, 'model_type': 'resnet', 'beta': 0.001, 'threshold': OUR_CHAMPION_THRESH, 'label': 'FedAvg', 'color': 'green', 'style': '-'},
        # {'algo': 'SSFLv4', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFL (Ours)', 'color': 'red', 'style': '-'},
        # {'algo': 'SSFLv5', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFLv5 (Ours)', 'color': 'orange', 'style': '--'},
        {'algo': 'SSFLv6', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFL (Ours)', 'color': 'red', 'style': '--'},
        # {'algo': 'SSFLv6_w_o_film', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFLv6 w/o FiLM (Ours)', 'color': 'brown', 'style': '-'},
        # {'algo': 'SSFLv6_w_o_vib', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFLv6 w/o VIB (Ours)', 'color': 'purple', 'style': '-'},
        # {'algo': 'SSFLv6_w_o_beta', 'snr': TRAIN_SNR, 'dim': OUR_CHAMPION_DIM, 'model_type': OUR_MODEL_TYPE, 'beta': OUR_CHAMPION_BETA, 'threshold': OUR_CHAMPION_THRESH, 'label': 'CA-SSFLv6 w/o Beta Sched. (Ours)', 'color': 'gray', 'style': '-'}

    ]
    
    plt.rcParams['font.size'] = 26
    plt.rcParams['axes.grid'] = True
    
    fig_acc, ax_acc = plt.subplots(figsize=(8, 6)) # 가로 길이를 좀 더 키움
    fig_eff, ax_eff = plt.subplots(figsize=(8, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, len(configs)))
    print(">>> Learning Curves 생성 중 (Smoothing 적용)...")

    # 스무딩 강도 설정 (0.7 ~ 0.8 추천)
    SMOOTH_FACTOR = 0.6

    for idx, config in enumerate(configs):
        stats = load_history_data(config['algo'], config['snr'], config['dim'], config['model_type'], config['beta'], config['threshold'], CHANNEL)
        if stats is None:
            continue
            
        rounds = stats['rounds']
        
        # ★ 1. 스무딩 적용된 평균과 원본 평균
        raw_mean = stats['acc_mean']
        smoothed_mean = smooth_curve(raw_mean, factor=SMOOTH_FACTOR)
        
        # ★ 2. 원본 데이터는 투명하게(alpha=0.2) 얇게 깔아줌
        ax_acc.plot(rounds, raw_mean, color=config['color'], alpha=0.2, linewidth=1)
        
        # ★ 3. 부드러운 스무딩 선을 메인으로 진하게 그림
        ax_acc.plot(rounds, smoothed_mean, label=config['label'], color=config['color'], linewidth=2.5)
        
        # 표준편차 그림자 (부드러운 선 기준)
        ax_acc.fill_between(rounds, smoothed_mean - stats['acc_std'], smoothed_mean + stats['acc_std'], color=config['color'], alpha=0.1)

        # Efficiency 그래프 (통신량은 원래 누적이라 스무딩이 필요 없음)
        ax_eff.plot(rounds, stats['comm_mean'], label=config['label'], color=config['color'], linewidth=3)
        mark_indices = np.linspace(0, len(rounds)-1, 8, dtype=int)
        ax_eff.scatter(rounds[mark_indices], stats['comm_mean'][mark_indices], color=config['color'], s=50, marker='o')

    # Accuracy Plot 저장
    ax_acc.set_xlabel('Communication Rounds', fontweight='bold')
    ax_acc.set_ylabel('Test Accuracy (%)', fontweight='bold')
    ax_acc.legend(loc='lower right', fontsize=25)
    fig_acc.tight_layout() 
    fig_acc.savefig(os.path.join(save_dir, 'history_accuracy_smoothed.pdf'), dpi=300, bbox_inches='tight')

    # Efficiency Plot 저장
    ax_eff.set_xlabel('Communication Rounds', fontweight='bold')
    ax_eff.set_ylabel('Cumulative Comm. Cost (MB)', fontweight='bold')
    ax_eff.legend(loc='upper left', fontsize=20)
    fig_eff.tight_layout()
    fig_eff.savefig(os.path.join(save_dir, 'history_efficiency.pdf'), dpi=300, bbox_inches='tight')
    
    print(">>> 스무딩된 그래프 저장 완료!")
    plt.close('all')

def print_numerical_results(save_dir):
    """ 터미널에 깔끔한 표 출력 및 CSV 저장 """
    configs =[
        {'algo': 'SFL', 'dim': 64, 'beta': BASE_BETA, 'threshold': BASE_THRESH, 'model': 'resnet', 'label': 'Standard SFL', 'max': 0.8, 'min':0.3},
        {'algo': 'SC-USFL', 'dim': 1352, 'beta': BASE_BETA, 'threshold': BASE_THRESH, 'model': 'resnet', 'label': 'SC-USFL', 'max': 0.8, 'min':0.3},
        {'algo': 'SSFLv6', 'dim': 4096, 'beta': 0.01, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL (Ours)', 'max': 0.7, 'min':0.4},
        {'algo': 'SSFLv6_w_o_vib', 'dim': 4096, 'beta': 0.005, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL w/o VIB', 'max': 0.7, 'min':0.4},
        {'algo': 'SSFLv6_w_o_film', 'dim': 4096, 'beta': 0.005, 'threshold': OUR_CHAMPION_THRESH, 'model': OUR_MODEL_TYPE, 'label': 'CA-SSFL w/o FiLM', 'max': 0.7, 'min':0.4}
    ]

    table_data =[]
    print("\n" + "="*70)
    print(" "*20 + "[ Final Numerical Results ]")
    print("="*70)

    for c in configs:
        data = load_data(c['algo'], TRAIN_SNR, c['dim'], c['model'], c['beta'], c['threshold'], CHANNEL ,c['max'], c['min'])
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


# ===================================================================
# Main
# ===================================================================
if __name__ == "__main__":
    plot_mode = os.environ.get('PLOT_COPY_MODE', 'legacy')

    if plot_mode == 'benchmark_current':
        output_dir = '/workspace/tmp/current_benchmark_graphs'
        os.makedirs(output_dir, exist_ok=True)

        print("--- Benchmark Plotting Started ---")
        plot_current_benchmark_integrated_snr_vs_accuracy(output_dir)
        plot_current_benchmark_integrated_round_vs_accuracy(output_dir)
        print("--- Benchmark Plotting Finished ---")
    elif plot_mode == 'benchmark_orig_integrated':
        output_dir = '/workspace/tmp/misc/current_benchmark_graphs'
        os.makedirs(output_dir, exist_ok=True)

        print("--- Benchmark Orig Integrated Plotting Started ---")
        _plot_benchmark_integrated_orig_only(
            output_dir,
            'integrated_snr_accuracy_cifar10_ca_ssfl_awgn0510_0702_rayleigh1010_0704_plotcopy.pdf',
            'integrated_history_accuracy_cifar10_ca_ssfl_awgn0510_0702_rayleigh1010_0704_plotcopy.pdf',
        )
        print("--- Benchmark Orig Integrated Plotting Finished ---")
    elif plot_mode == 'benchmark_cifar100_integrated':
        output_dir = '/workspace/tmp/misc/current_benchmark_graphs'
        os.makedirs(output_dir, exist_ok=True)

        print("--- Benchmark CIFAR100 Integrated Plotting Started ---")
        _plot_benchmark_integrated_from_roots(
            output_dir,
            'integrated_snr_accuracy_cifar100_ca_ssfl_awgn0510_0702_rayleigh1010_0704_plotcopy.pdf',
            'integrated_history_accuracy_cifar100_ca_ssfl_awgn0510_0702_rayleigh1010_0704_plotcopy.pdf',
            awgn_root='/workspace/tmp/2026-04-14/2026-04-14-cifar100-awgn-threeway-benchmark-updated-ca-ssfl',
            rayleigh_root='/workspace/tmp/2026-04-14/2026-04-14-cifar100-rayleigh-threeway-benchmark-updated-ca-ssfl',
            ca_awgn_root='/workspace/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun',
            ca_rayleigh_root='/workspace/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun',
            dataset_name='cifar100',
            base_use_short_paths=False,
            base_awgn_beta='0.01',
            base_awgn_threshold='1.0',
            base_awgn_film_max='0.7',
            base_awgn_film_min='0.2',
            base_rayleigh_beta='0.01',
            base_rayleigh_threshold='1.0',
            base_rayleigh_film_max='0.7',
            base_rayleigh_film_min='0.2',
            ca_awgn_beta='0.05',
            ca_awgn_threshold='1.0',
            ca_rayleigh_beta='0.1',
            ca_rayleigh_threshold='1.0',
            ca_awgn_film_max='0.7',
            ca_awgn_film_min='0.2',
            ca_rayleigh_film_max='0.7',
            ca_rayleigh_film_min='0.4',
            snr_ylim=(0, 30),
        )
        print("--- Benchmark CIFAR100 Integrated Plotting Finished ---")
    else:
        output_dir = f'./results/final_graphs/{DATASET}/{CHANNEL}'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print("--- Plotting Started ---")
        plot_snr_vs_accuracy_clean(output_dir)
        plot_integrated_snr_vs_accuracy(output_dir)
        plot_integrated_round_vs_accuracy_smoothed(output_dir)
        plot_history_graphs(output_dir)
        generate_ablation_table(output_dir)
        # plot_final_comm_cost_bar_grouped(output_dir)
        print_numerical_results(output_dir)
        print("--- Plotting Finished ---")
