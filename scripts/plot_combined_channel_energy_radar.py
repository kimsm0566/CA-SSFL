import glob
import json
import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
plt.rcParams["axes.unicode_minus"] = False
plt.switch_backend("agg")


OUTPUT_DIR = (
    "/workspace/docs/experiments/2026-04-16/"
    "2026-04-16_23-25_v01_combined-channel-energy-radar/figures"
)

METHOD_STYLES = {
    "SFL": {"color": "#ff5a52", "marker": "o"},
    "SC-USFL": {"color": "#4aa3ff", "marker": "s"},
    "CA-SSFL (Ours)": {"color": "#2ca25f", "marker": "^"},
}

COMP_MFLOPS = {
    "SFL": 70.50,
    "SC-USFL": 80.27,
    "CA-SSFL (Ours)": 113.84,
}

AXES = [
    "AWGN\nAccuracy",
    "Rayleigh\nAccuracy",
    "1 / Avg.\nComm. Overhead",
    "1 / Avg. Est.\nClient Energy",
]


def load_npz_group(pattern):
    paths = sorted(glob.glob(pattern, recursive=True))
    if len(paths) != 4:
        raise RuntimeError(f"Expected 4 seeds, got {len(paths)} for pattern: {pattern}")
    finals = []
    comms = []
    for path in paths:
        data = np.load(path, allow_pickle=True)
        finals.append(float(np.asarray(data["train_acc"], dtype=float)[-1]))
        comms.append(float(np.asarray(data["comm"], dtype=float)[-1]))
    return {
        "final_acc_mean": float(np.mean(finals)),
        "comm_mb_mean": float(np.mean(comms)),
        "paths": paths,
    }


def build_channel_metrics():
    return {
        "cifar10": {
            "title": "CIFAR-10",
            "awgn": {
                "SFL": {"final_acc_mean": 53.70, "comm_mb_mean": 172882.75},
                "SC-USFL": {"final_acc_mean": 39.76, "comm_mb_mean": 23821.53},
                "CA-SSFL (Ours)": {"final_acc_mean": 41.71, "comm_mb_mean": 14363.28},
            },
            "rayleigh": {
                "SFL": {"final_acc_mean": 51.07, "comm_mb_mean": 172882.75},
                "SC-USFL": {"final_acc_mean": 40.90, "comm_mb_mean": 23821.53},
                "CA-SSFL (Ours)": {"final_acc_mean": 40.41, "comm_mb_mean": 14943.447068214417},
            },
        },
        "cifar100": {
            "title": "CIFAR-100",
            "awgn": {
                "SFL": load_npz_group(
                    "/workspace/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8/**/SFL/snr_10/compress_4096/channel_type_awgn/seed_*.npz"
                ),
                "SC-USFL": load_npz_group(
                    "/workspace/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8/**/SC-USFL/snr_10/compress_1352/channel_type_awgn/seed_*.npz"
                ),
                "CA-SSFL (Ours)": load_npz_group(
                    "/workspace/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun/**/SSFLv6/snr_10/compress_4096/channel_type_awgn/seed_*.npz"
                ),
            },
            "rayleigh": {
                "SFL": load_npz_group(
                    "/workspace/tmp/2026-04-11/2026-04-11-cifar100-rayleigh-threeway-benchmark-nclients8/**/SFL/snr_10/compress_4096/channel_type_rayleigh/seed_*.npz"
                ),
                "SC-USFL": load_npz_group(
                    "/workspace/tmp/2026-04-11/2026-04-11-cifar100-rayleigh-threeway-benchmark-nclients8/**/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_*.npz"
                ),
                "CA-SSFL (Ours)": load_npz_group(
                    "/workspace/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun/**/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_*.npz"
                ),
            },
        },
    }


def normalize_combined_metrics(channel_metrics):
    normalized = {}
    for dataset_key, dataset_bundle in channel_metrics.items():
        awgn_max_acc = max(
            dataset_bundle["awgn"][method]["final_acc_mean"] for method in METHOD_STYLES
        )
        rayleigh_max_acc = max(
            dataset_bundle["rayleigh"][method]["final_acc_mean"] for method in METHOD_STYLES
        )

        avg_comm = {}
        energy_proxy = {}
        for method in METHOD_STYLES:
            avg_comm[method] = 0.5 * (
                dataset_bundle["awgn"][method]["comm_mb_mean"]
                + dataset_bundle["rayleigh"][method]["comm_mb_mean"]
            )

        min_avg_comm = min(avg_comm.values())
        min_comp = min(COMP_MFLOPS.values())

        for method in METHOD_STYLES:
            comm_ratio = avg_comm[method] / min_avg_comm
            comp_ratio = COMP_MFLOPS[method] / min_comp
            energy_proxy[method] = 0.5 * (comm_ratio + comp_ratio)

        min_energy = min(energy_proxy.values())

        normalized[dataset_key] = {"title": dataset_bundle["title"], "methods": {}}
        for method in METHOD_STYLES:
            normalized[dataset_key]["methods"][method] = {
                "awgn_accuracy": dataset_bundle["awgn"][method]["final_acc_mean"] / awgn_max_acc,
                "rayleigh_accuracy": dataset_bundle["rayleigh"][method]["final_acc_mean"] / rayleigh_max_acc,
                "inv_avg_comm_overhead": min_avg_comm / avg_comm[method],
                "inv_avg_est_client_energy": min_energy / energy_proxy[method],
                "raw": {
                    "awgn_final_acc_mean": dataset_bundle["awgn"][method]["final_acc_mean"],
                    "rayleigh_final_acc_mean": dataset_bundle["rayleigh"][method]["final_acc_mean"],
                    "awgn_comm_gb_mean": dataset_bundle["awgn"][method]["comm_mb_mean"] / 1024.0,
                    "rayleigh_comm_gb_mean": dataset_bundle["rayleigh"][method]["comm_mb_mean"] / 1024.0,
                    "avg_comm_gb_mean": avg_comm[method] / 1024.0,
                    "comp_mflops": COMP_MFLOPS[method],
                    "energy_proxy": energy_proxy[method],
                },
            }
    return normalized


def draw_radar(ax, title, method_summary):
    angles = np.linspace(0, 2 * math.pi, len(AXES), endpoint=False).tolist()
    angles += angles[:1]

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(AXES, fontsize=10, fontweight="semibold")
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.grid(color="#9aa0a6", alpha=0.55, linewidth=0.8)
    ax.spines["polar"].set_color("#80868b")
    ax.spines["polar"].set_linewidth(1.0)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=20)

    for method, style in METHOD_STYLES.items():
        vals = method_summary[method]
        data = [
            vals["awgn_accuracy"],
            vals["rayleigh_accuracy"],
            vals["inv_avg_comm_overhead"],
            vals["inv_avg_est_client_energy"],
        ]
        data += data[:1]
        ax.plot(
            angles,
            data,
            color=style["color"],
            linewidth=2.1,
            marker=style["marker"],
            markersize=5.5,
            label=method,
        )
        ax.fill(angles, data, color=style["color"], alpha=0.14)


def plot_individual(key, title, method_summary):
    fig, ax = plt.subplots(figsize=(7.2, 6.4), subplot_kw={"polar": True})
    draw_radar(ax, title, method_summary)
    legend = ax.legend(loc="upper right", bbox_to_anchor=(1.34, 1.14), frameon=True, fontsize=9)
    legend.get_frame().set_alpha(0.95)
    fig.tight_layout()

    fig.savefig(os.path.join(OUTPUT_DIR, f"{key}_combined.png"), dpi=240, bbox_inches="tight")
    fig.savefig(os.path.join(OUTPUT_DIR, f"{key}_combined.pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_panel(normalized):
    fig, axes = plt.subplots(1, 2, figsize=(12.6, 6.2), subplot_kw={"polar": True})
    keys = ["cifar10", "cifar100"]
    for ax, key in zip(axes, keys):
        draw_radar(ax, normalized[key]["title"], normalized[key]["methods"])

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="upper center", ncol=3, frameon=True, bbox_to_anchor=(0.5, 0.98))
    legend.get_frame().set_alpha(0.96)
    fig.text(
        0.5,
        0.03,
        "Higher is better on all axes. Communication and energy use AWGN/Rayleigh averages.\n"
        "Estimated client energy = 0.5 x normalized average communication overhead + 0.5 x normalized computation cost.",
        ha="center",
        va="bottom",
        fontsize=9.5,
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.92])

    fig.savefig(os.path.join(OUTPUT_DIR, "combined_channel_energy_radar_panel.png"), dpi=240, bbox_inches="tight")
    fig.savefig(os.path.join(OUTPUT_DIR, "combined_channel_energy_radar_panel.pdf"), bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    channel_metrics = build_channel_metrics()
    normalized = normalize_combined_metrics(channel_metrics)

    for key, bundle in normalized.items():
        plot_individual(key, bundle["title"], bundle["methods"])

    plot_panel(normalized)

    payload = {
        "axes": {
            "axis1": "awgn final accuracy",
            "axis2": "rayleigh final accuracy",
            "axis3": "inverse-normalized average communication overhead across awgn and rayleigh",
            "axis4": "inverse-normalized average estimated client energy across awgn and rayleigh",
        },
        "energy_proxy_definition": {
            "formula": "0.5 * (avg_comm_mb / min_avg_comm_mb) + 0.5 * (comp_mflops / min_comp_mflops)",
            "comp_mflops": COMP_MFLOPS,
        },
        "summary": normalized,
    }
    with open(os.path.join(OUTPUT_DIR, "combined_channel_energy_radar_summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()
