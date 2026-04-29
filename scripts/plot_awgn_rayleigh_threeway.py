import json
import os
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.unicode_minus"] = False
plt.switch_backend("agg")


OUTPUT_DIR = Path(
    "/workspace/docs/experiments/2026-04-09_20-00_v01_channel-comparison-figures/figures"
)

AWGN_ROOT = Path(
    "/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8/"
    "cifar10/n_clients_8/n_client_data_3000/batch_size_100/"
    "data_partition_type_class/model_type_resnetv2/major_percent_0.8/"
    "n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"
)

RAYLEIGH_CROSS_ROOT = Path(
    "/workspace/tmp/2026-04-09-cross-benchmark/"
    "cifar10/n_clients_9/n_client_data_3000/batch_size_100/"
    "data_partition_type_class/model_type_resnetv2/major_percent_0.8/"
    "n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"
)

RAYLEIGH_LEGACY_ROOT = Path(
    "/workspace/tmp/2026-04-09-rayleigh-seq-full/"
    "cifar10/n_clients_9/n_client_data_3000/batch_size_100/"
    "data_partition_type_class/model_type_resnetv2/major_percent_0.8/"
    "n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"
)

COLORS = {
    "SFL": "#1f77b4",
    "SC-USFL": "#ff7f0e",
    "SSFLv6 Candidate": "#2ca02c",
}

MARKERS = {
    "SFL": "o",
    "SC-USFL": "s",
    "SSFLv6 Candidate": "^",
}


def load_npz_summary(paths, label):
    finals = []
    comms = []
    accs = []
    snrs = None

    for path in paths:
        data = np.load(path, allow_pickle=True)
        finals.append(float(data["train_acc"][-1]))
        comms.append(float(data["comm"][-1]))
        accs.append(data["snr_accs"].astype(float))
        snrs = data["test_snrs"].astype(int)

    accs = np.stack(accs, axis=0)
    return {
        "label": label,
        "paths": [str(p) for p in paths],
        "count": len(paths),
        "snrs": snrs.tolist(),
        "final_acc_mean": float(np.mean(finals)),
        "final_acc_std": float(np.std(finals, ddof=0)),
        "comm_mean": float(np.mean(comms)),
        "comm_std": float(np.std(comms, ddof=0)),
        "snr_acc_mean": np.mean(accs, axis=0).tolist(),
        "snr_acc_std": np.std(accs, axis=0, ddof=0).tolist(),
    }


def awgn_summaries():
    configs = {
        "SFL": AWGN_ROOT / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SFL/snr_10/compress_4096/channel_type_awgn",
        "SC-USFL": AWGN_ROOT / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_awgn",
        "SSFLv6 Candidate": AWGN_ROOT / "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_awgn",
    }
    return {
        label: load_npz_summary(sorted(path.glob("seed_*.npz")), label)
        for label, path in configs.items()
    }


def rayleigh_summaries():
    sfl = sorted(
        (RAYLEIGH_CROSS_ROOT / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SFL/snr_10/compress_4096/channel_type_rayleigh").glob("seed_*.npz")
    )
    sc = sorted(
        (RAYLEIGH_CROSS_ROOT / "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_rayleigh").glob("seed_*.npz")
    )
    ours_12 = sorted(
        (RAYLEIGH_LEGACY_ROOT / "semantic_spreading_1/snr_adaptive_beta_1/SSFLv6/snr_10/compress_4096/channel_type_rayleigh").glob("seed_[12].npz")
    )
    ours_34 = sorted(
        (RAYLEIGH_CROSS_ROOT / "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_rayleigh").glob("seed_[34].npz")
    )

    return {
        "SFL": load_npz_summary(sfl, "SFL"),
        "SC-USFL": load_npz_summary(sc, "SC-USFL"),
        "SSFLv6 Candidate": load_npz_summary(ours_12 + ours_34, "SSFLv6 Candidate"),
    }


def plot_snr_accuracy(channel_name, summaries, note):
    fig, ax = plt.subplots(figsize=(9, 6.5))
    for label in ["SFL", "SC-USFL", "SSFLv6 Candidate"]:
        summary = summaries[label]
        snrs = np.array(summary["snrs"])
        means = np.array(summary["snr_acc_mean"])
        stds = np.array(summary["snr_acc_std"])
        ax.errorbar(
            snrs,
            means,
            yerr=stds,
            label=label,
            color=COLORS[label],
            marker=MARKERS[label],
            linewidth=2.2,
            markersize=6,
            capsize=3,
        )

    ax.set_xlabel("Test SNR (dB)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(f"{channel_name}: Accuracy vs Test SNR (mean +/- std)")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(framealpha=0.95)
    ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=9, alpha=0.85)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{channel_name.lower()}_snr_accuracy_threeway.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / f"{channel_name.lower()}_snr_accuracy_threeway.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_final_acc_vs_comm(channel_name, summaries, note):
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for label in ["SFL", "SC-USFL", "SSFLv6 Candidate"]:
        summary = summaries[label]
        ax.errorbar(
            summary["comm_mean"],
            summary["final_acc_mean"],
            xerr=summary["comm_std"],
            yerr=summary["final_acc_std"],
            fmt=MARKERS[label],
            color=COLORS[label],
            markersize=10,
            capsize=4,
            linewidth=1.8,
        )
        ax.annotate(label, (summary["comm_mean"], summary["final_acc_mean"]), textcoords="offset points", xytext=(8, 8), fontsize=10)

    ax.set_xlabel("Total Communication (MB)")
    ax.set_ylabel("Final Accuracy (%)")
    ax.set_title(f"{channel_name}: Final Accuracy vs Communication (mean +/- std)")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=9, alpha=0.85)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{channel_name.lower()}_final_acc_vs_comm_threeway.png", dpi=220, bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / f"{channel_name.lower()}_final_acc_vs_comm_threeway.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    awgn = awgn_summaries()
    rayleigh = rayleigh_summaries()

    plot_snr_accuracy("AWGN", awgn, "n_clients=8, seeds=1-4")
    plot_final_acc_vs_comm("AWGN", awgn, "n_clients=8, seeds=1-4")
    plot_snr_accuracy("Rayleigh", rayleigh, "n_clients=9, seeds=1-4")
    plot_final_acc_vs_comm("Rayleigh", rayleigh, "n_clients=9, seeds=1-4")

    summary = {"awgn": awgn, "rayleigh": rayleigh}
    with open(OUTPUT_DIR / "channel_threeway_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
