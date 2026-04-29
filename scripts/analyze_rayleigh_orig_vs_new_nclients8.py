import json
from pathlib import Path

import numpy as np


BASE_RAY = Path(
    "/workspace/tmp/2026-04-09-rayleigh-cross-benchmark-nclients8/"
    "cifar10/n_clients_8/n_client_data_3000/batch_size_100/"
    "data_partition_type_class/model_type_resnetv2/major_percent_0.8/"
    "n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"
)
DOC_DIR = Path(
    "/workspace/docs/experiments/2026-04-09_21-55_v01_awgn-orig-plus-rayleigh-diagnosis"
)


def load_group(path):
    accs = []
    comms = []
    snr_accs = []
    snrs = None
    for file_path in sorted(path.glob("seed_*.npz")):
        data = np.load(file_path, allow_pickle=True)
        accs.append(data["train_acc"].astype(float))
        comms.append(data["comm"].astype(float))
        snr_accs.append(data["snr_accs"].astype(float))
        snrs = data["test_snrs"].astype(int)

    min_len = min(len(a) for a in accs)
    accs = np.stack([a[:min_len] for a in accs], axis=0)
    comms = np.stack([c[:min_len] for c in comms], axis=0)
    snr_accs = np.stack(snr_accs, axis=0)

    return {
        "count": int(accs.shape[0]),
        "rounds": np.arange(1, min_len + 1),
        "acc_mean": np.mean(accs, axis=0),
        "acc_std": np.std(accs, axis=0, ddof=0),
        "comm_mean": np.mean(comms, axis=0),
        "comm_std": np.std(comms, axis=0, ddof=0),
        "snrs": snrs,
        "snr_acc_mean": np.mean(snr_accs, axis=0),
        "final_acc_mean": float(np.mean(accs[:, -1])),
        "final_acc_std": float(np.std(accs[:, -1], ddof=0)),
        "comm_final_mean": float(np.mean(comms[:, -1])),
        "comm_final_std": float(np.std(comms[:, -1], ddof=0)),
    }


def main():
    orig = load_group(BASE_RAY / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh")
    new = load_group(BASE_RAY / "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh")

    snr_to_idx = {int(s): i for i, s in enumerate(orig["snrs"])}

    diagnosis = {
        "orig_count": orig["count"],
        "new_count": new["count"],
        "final_acc_delta_new_minus_orig": float(new["final_acc_mean"] - orig["final_acc_mean"]),
        "final_comm_delta_new_minus_orig": float(new["comm_final_mean"] - orig["comm_final_mean"]),
        "m6_delta_new_minus_orig": float(new["snr_acc_mean"][snr_to_idx[-6]] - orig["snr_acc_mean"][snr_to_idx[-6]]),
        "p12_delta_new_minus_orig": float(new["snr_acc_mean"][snr_to_idx[12]] - orig["snr_acc_mean"][snr_to_idx[12]]),
        "best_round_orig": int(np.argmax(orig["acc_mean"]) + 1),
        "best_round_new": int(np.argmax(new["acc_mean"]) + 1),
        "best_acc_orig": float(np.max(orig["acc_mean"])),
        "best_acc_new": float(np.max(new["acc_mean"])),
        "acc_gap_round_50": float(new["acc_mean"][49] - orig["acc_mean"][49]),
        "acc_gap_round_100": float(new["acc_mean"][99] - orig["acc_mean"][99]),
        "acc_gap_round_150": float(new["acc_mean"][149] - orig["acc_mean"][149]),
        "acc_gap_round_200": float(new["acc_mean"][199] - orig["acc_mean"][199]),
        "comm_gap_round_50": float(new["comm_mean"][49] - orig["comm_mean"][49]),
        "comm_gap_round_100": float(new["comm_mean"][99] - orig["comm_mean"][99]),
        "comm_gap_round_150": float(new["comm_mean"][149] - orig["comm_mean"][149]),
        "comm_gap_round_200": float(new["comm_mean"][199] - orig["comm_mean"][199]),
    }

    output = {
        "orig": {
            "final_acc_mean": orig["final_acc_mean"],
            "final_acc_std": orig["final_acc_std"],
            "comm_mean": orig["comm_final_mean"],
            "comm_std": orig["comm_final_std"],
            "snrs": orig["snrs"].tolist(),
            "snr_acc_mean": orig["snr_acc_mean"].round(4).tolist(),
        },
        "new": {
            "final_acc_mean": new["final_acc_mean"],
            "final_acc_std": new["final_acc_std"],
            "comm_mean": new["comm_final_mean"],
            "comm_std": new["comm_final_std"],
            "snrs": new["snrs"].tolist(),
            "snr_acc_mean": new["snr_acc_mean"].round(4).tolist(),
        },
        "diagnosis": diagnosis,
    }

    DOC_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOC_DIR / "rayleigh_orig_vs_new_diagnosis.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
