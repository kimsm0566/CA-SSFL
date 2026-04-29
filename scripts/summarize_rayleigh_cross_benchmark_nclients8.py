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
    "/workspace/docs/experiments/2026-04-09_20-05_v01_rayleigh-cross-benchmark-nclients8"
)


def summarize(paths):
    finals = []
    comms = []
    snr_accs = []
    snrs = None

    for path in paths:
        data = np.load(path, allow_pickle=True)
        finals.append(float(data["train_acc"][-1]))
        comms.append(float(data["comm"][-1]))
        snr_accs.append(data["snr_accs"].astype(float))
        snrs = data["test_snrs"].astype(int)

    arr = np.stack(snr_accs)
    return {
        "count": len(paths),
        "final_acc_mean": float(np.mean(finals)),
        "final_acc_std": float(np.std(finals, ddof=0)),
        "comm_mean": float(np.mean(comms)),
        "comm_std": float(np.std(comms, ddof=0)),
        "m6_mean": float(np.mean(arr[:, 0])),
        "p12_mean": float(np.mean(arr[:, -1])),
        "snrs": snrs.tolist(),
        "snr_acc_mean": np.mean(arr, axis=0).round(4).tolist(),
    }


def main():
    summaries = {
        "SFL": summarize(sorted((BASE_RAY / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SFL/snr_10/compress_4096/channel_type_rayleigh").glob("seed_*.npz"))),
        "SC-USFL": summarize(sorted((BASE_RAY / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh").glob("seed_*.npz"))),
        "CA-SSFL Orig": summarize(sorted((BASE_RAY / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh").glob("seed_*.npz"))),
        "CA-SSFL New": summarize(sorted((BASE_RAY / "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh").glob("seed_*.npz"))),
    }

    DOC_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOC_DIR / "summary.json"
    out_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
