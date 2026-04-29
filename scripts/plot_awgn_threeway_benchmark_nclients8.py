import glob
import json
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.unicode_minus"] = False
plt.switch_backend("agg")


RESULT_ROOT = (
    "/workspace/tmp/2026-04-09-awgn-threeway-benchmark-nclients8/"
    "cifar10/n_clients_8/n_client_data_3000/batch_size_100/"
    "data_partition_type_class/model_type_resnetv2/major_percent_0.8/"
    "n_epochs_1/beta_0.01/pruning_threshold_1.0/film_max_t_0.7/film_min_t_0.4"
)
OUTPUT_DIR = (
    "/workspace/docs/experiments/"
    "2026-04-09_18-45_v01_awgn-threeway-benchmark-nclients8/figures"
)

CONFIGS = [
    {
        "label": "SFL",
        "path": (
            "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/"
            "semantic_power_alpha_2.0/SFL/snr_10/compress_4096/channel_type_awgn"
        ),
        "color": "#1f77b4",
        "marker": "o",
    },
    {
        "label": "SC-USFL",
        "path": (
            "semantic_spreading_0/snr_adaptive_beta_0/semantic_power_0/"
            "semantic_power_alpha_2.0/SC-USFL/snr_10/compress_1352/channel_type_awgn"
        ),
        "color": "#ff7f0e",
        "marker": "s",
    },
    {
        "label": "SSFLv6 Candidate",
        "path": (
            "semantic_spreading_1/snr_adaptive_beta_1/semantic_power_0/"
            "semantic_power_alpha_2.0/SSFLv6/snr_10/compress_4096/channel_type_awgn"
        ),
        "color": "#2ca02c",
        "marker": "^",
    },
]


def load_config_summary(config):
    paths = sorted(glob.glob(os.path.join(RESULT_ROOT, config["path"], "seed_*.npz")))
    if not paths:
        raise FileNotFoundError(f"No result files found for {config['label']}")

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
        "label": config["label"],
        "paths": paths,
        "snrs": snrs.tolist(),
        "final_acc_mean": float(np.mean(finals)),
        "final_acc_std": float(np.std(finals, ddof=0)),
        "comm_mean": float(np.mean(comms)),
        "comm_std": float(np.std(comms, ddof=0)),
        "snr_acc_mean": np.mean(accs, axis=0).tolist(),
        "snr_acc_std": np.std(accs, axis=0, ddof=0).tolist(),
    }


def plot_snr_accuracy(summaries):
    fig, ax = plt.subplots(figsize=(9, 6.5))

    for config, summary in zip(CONFIGS, summaries):
        snrs = np.array(summary["snrs"])
        means = np.array(summary["snr_acc_mean"])
        stds = np.array(summary["snr_acc_std"])
        ax.errorbar(
            snrs,
            means,
            yerr=stds,
            label=summary["label"],
            color=config["color"],
            marker=config["marker"],
            linewidth=2.2,
            markersize=6,
            capsize=3,
        )

    ax.set_xlabel("Test SNR (dB)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("AWGN: Accuracy vs Test SNR (mean +/- std, seeds 1-4)")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(framealpha=0.95)
    fig.tight_layout()

    png_path = os.path.join(OUTPUT_DIR, "awgn_snr_accuracy_threeway.png")
    pdf_path = os.path.join(OUTPUT_DIR, "awgn_snr_accuracy_threeway.pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def plot_final_acc_vs_comm(summaries):
    fig, ax = plt.subplots(figsize=(8.5, 6.5))

    for config, summary in zip(CONFIGS, summaries):
        ax.errorbar(
            summary["comm_mean"],
            summary["final_acc_mean"],
            xerr=summary["comm_std"],
            yerr=summary["final_acc_std"],
            fmt=config["marker"],
            color=config["color"],
            markersize=10,
            capsize=4,
            linewidth=1.8,
            label=summary["label"],
        )
        ax.annotate(
            summary["label"],
            (summary["comm_mean"], summary["final_acc_mean"]),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=10,
        )

    ax.set_xlabel("Total Communication (MB)")
    ax.set_ylabel("Final Accuracy (%)")
    ax.set_title("AWGN: Final Accuracy vs Communication (mean +/- std, seeds 1-4)")
    ax.grid(True, linestyle="--", alpha=0.35)
    fig.tight_layout()

    png_path = os.path.join(OUTPUT_DIR, "awgn_final_acc_vs_comm_threeway.png")
    pdf_path = os.path.join(OUTPUT_DIR, "awgn_final_acc_vs_comm_threeway.pdf")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summaries = [load_config_summary(config) for config in CONFIGS]

    plot_snr_accuracy(summaries)
    plot_final_acc_vs_comm(summaries)

    with open(os.path.join(OUTPUT_DIR, "awgn_threeway_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summaries": summaries}, f, indent=2)


if __name__ == "__main__":
    main()
