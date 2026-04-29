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
    "2026-04-16_23-05_v01_energy-radar-cifar10-cifar100-channels/figures"
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
    "Accuracy",
    "1 / Communication\nOverhead",
    "1 / Estimated\nClient Energy",
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


def build_metrics():
    metrics = {
        "cifar10_awgn": {
            "title": "CIFAR-10 AWGN",
            "SFL": {
                "final_acc_mean": 53.70,
                "comm_mb_mean": 172882.75,
                "source": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            },
            "SC-USFL": {
                "final_acc_mean": 39.76,
                "comm_mb_mean": 23821.53,
                "source": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            },
            "CA-SSFL (Ours)": {
                "final_acc_mean": 41.71,
                "comm_mb_mean": 14363.28,
                "source": "docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md",
            },
        },
        "cifar10_rayleigh": {
            "title": "CIFAR-10 Rayleigh",
            "SFL": {
                "final_acc_mean": 51.07,
                "comm_mb_mean": 172882.75,
                "source": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            },
            "SC-USFL": {
                "final_acc_mean": 40.90,
                "comm_mb_mean": 23821.53,
                "source": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            },
            "CA-SSFL (Ours)": {
                "final_acc_mean": 40.41,
                "comm_mb_mean": 14943.447068214417,
                "source": "docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md",
            },
        },
        "cifar100_awgn": {
            "title": "CIFAR-100 AWGN",
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
        "cifar100_rayleigh": {
            "title": "CIFAR-100 Rayleigh",
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
    }
    return metrics


def normalize_metrics(metrics):
    normalized = {}
    for key, bundle in metrics.items():
        max_acc = max(bundle[m]["final_acc_mean"] for m in METHOD_STYLES)
        min_comm = min(bundle[m]["comm_mb_mean"] for m in METHOD_STYLES)
        comp_min = min(COMP_MFLOPS.values())

        energy_proxy = {}
        for method in METHOD_STYLES:
            comm_ratio = bundle[method]["comm_mb_mean"] / min_comm
            comp_ratio = COMP_MFLOPS[method] / comp_min
            energy_proxy[method] = 0.5 * (comm_ratio + comp_ratio)

        min_energy = min(energy_proxy.values())

        normalized[key] = {"title": bundle["title"], "methods": {}}
        for method in METHOD_STYLES:
            normalized[key]["methods"][method] = {
                "accuracy": bundle[method]["final_acc_mean"] / max_acc,
                "inv_comm_overhead": min_comm / bundle[method]["comm_mb_mean"],
                "inv_est_client_energy": min_energy / energy_proxy[method],
                "raw": {
                    "final_acc_mean": bundle[method]["final_acc_mean"],
                    "comm_mb_mean": bundle[method]["comm_mb_mean"],
                    "comm_gb_mean": bundle[method]["comm_mb_mean"] / 1024.0,
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
            vals["accuracy"],
            vals["inv_comm_overhead"],
            vals["inv_est_client_energy"],
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
    fig, ax = plt.subplots(figsize=(7.1, 6.3), subplot_kw={"polar": True})
    draw_radar(ax, title, method_summary)
    legend = ax.legend(loc="upper right", bbox_to_anchor=(1.34, 1.14), frameon=True, fontsize=9)
    legend.get_frame().set_alpha(0.95)
    fig.tight_layout()

    png_path = os.path.join(OUTPUT_DIR, f"{key}.png")
    pdf_path = os.path.join(OUTPUT_DIR, f"{key}.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def plot_panel(normalized):
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 11.2), subplot_kw={"polar": True})
    axes = axes.flatten()
    for ax, key in zip(axes, ["cifar10_awgn", "cifar10_rayleigh", "cifar100_awgn", "cifar100_rayleigh"]):
        draw_radar(ax, normalized[key]["title"], normalized[key]["methods"])

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="upper center", ncol=3, frameon=True, bbox_to_anchor=(0.5, 0.98))
    legend.get_frame().set_alpha(0.96)
    fig.text(
        0.5,
        0.02,
        "Higher is better on all axes. The energy axis uses an estimated client-energy proxy:\n"
        "0.5 x normalized communication overhead + 0.5 x normalized computation cost.",
        ha="center",
        va="bottom",
        fontsize=10,
    )
    fig.tight_layout(rect=[0, 0.05, 1, 0.93])

    png_path = os.path.join(OUTPUT_DIR, "energy_radar_panel_cifar10_cifar100_channels.png")
    pdf_path = os.path.join(OUTPUT_DIR, "energy_radar_panel_cifar10_cifar100_channels.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    metrics = build_metrics()
    normalized = normalize_metrics(metrics)

    for key, bundle in normalized.items():
        plot_individual(key, bundle["title"], bundle["methods"])

    plot_panel(normalized)

    payload = {
        "axes": {
            "axis1": "channel-specific final accuracy",
            "axis2": "inverse-normalized channel-specific communication overhead",
            "axis3": "inverse-normalized estimated client energy proxy",
        },
        "energy_proxy_definition": {
            "formula": "0.5 * (comm_mb / min_comm_mb) + 0.5 * (comp_mflops / min_comp_mflops)",
            "comp_mflops": COMP_MFLOPS,
        },
        "summary": normalized,
    }
    with open(os.path.join(OUTPUT_DIR, "energy_radar_summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()
