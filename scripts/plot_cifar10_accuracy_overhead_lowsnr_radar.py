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
    "2026-04-16_22-25_v01_cifar10-accuracy-overhead-lowsnr-radar/figures"
)

METHODS = {
    "SFL": {
        "accuracy_awgn": 53.70,
        "comm_mb_awgn": 172882.75,
        "minus6_acc_rayleigh": 44.92,
        "color": "#ff5a52",
        "marker": "o",
    },
    "SC-USFL": {
        "accuracy_awgn": 39.76,
        "comm_mb_awgn": 23821.53,
        "minus6_acc_rayleigh": 40.09,
        "color": "#4aa3ff",
        "marker": "s",
    },
    "CA-SSFL (Ours)": {
        "accuracy_awgn": 41.71,
        "comm_mb_awgn": 14363.28,
        "minus6_acc_rayleigh": 37.88,
        "color": "#2ca25f",
        "marker": "^",
    },
}

AXES = [
    "Accuracy",
    "1 / Communication\nOverhead",
    "Low-SNR\nRobustness",
]


def compute_summary():
    max_accuracy = max(v["accuracy_awgn"] for v in METHODS.values())
    min_comm_mb = min(v["comm_mb_awgn"] for v in METHODS.values())
    max_minus6 = max(v["minus6_acc_rayleigh"] for v in METHODS.values())

    summary = {}
    for label, values in METHODS.items():
        comm_gb = values["comm_mb_awgn"] / 1024.0
        summary[label] = {
            "raw": {
                "accuracy_awgn": values["accuracy_awgn"],
                "comm_mb_awgn": values["comm_mb_awgn"],
                "comm_gb_awgn": comm_gb,
                "minus6_acc_rayleigh": values["minus6_acc_rayleigh"],
            },
            "normalized": {
                "accuracy": values["accuracy_awgn"] / max_accuracy,
                "inv_comm_overhead": min_comm_mb / values["comm_mb_awgn"],
                "low_snr_robustness": values["minus6_acc_rayleigh"] / max_minus6,
            },
        }
    return summary


def plot_radar(summary):
    angles = np.linspace(0, 2 * math.pi, len(AXES), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7.2, 6.4), subplot_kw={"polar": True})
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(AXES, fontsize=11, fontweight="semibold")
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.grid(color="#9aa0a6", alpha=0.55, linewidth=0.8)
    ax.spines["polar"].set_color("#80868b")
    ax.spines["polar"].set_linewidth(1.05)

    for label, style in METHODS.items():
        values = summary[label]["normalized"]
        data = [
            values["accuracy"],
            values["inv_comm_overhead"],
            values["low_snr_robustness"],
        ]
        data += data[:1]
        ax.plot(
            angles,
            data,
            color=style["color"],
            linewidth=2.2,
            marker=style["marker"],
            markersize=6,
            label=label,
        )
        ax.fill(angles, data, color=style["color"], alpha=0.15)

    ax.set_title(
        "CIFAR-10: Accuracy-Overhead-Robustness Trade-off",
        fontsize=13,
        fontweight="bold",
        pad=24,
    )
    legend = ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.34, 1.14),
        frameon=True,
        fontsize=9,
    )
    legend.get_frame().set_alpha(0.95)

    fig.text(
        0.5,
        0.02,
        "Higher is better on all axes. The communication-overhead axis is normalized as the inverse of AWGN total GB,\n"
        "and the robustness axis uses Rayleigh -6 dB accuracy.",
        ha="center",
        va="bottom",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])

    png_path = os.path.join(OUTPUT_DIR, "cifar10_accuracy_overhead_lowsnr_radar.png")
    pdf_path = os.path.join(OUTPUT_DIR, "cifar10_accuracy_overhead_lowsnr_radar.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = compute_summary()
    plot_radar(summary)
    payload = {
        "sources": {
            "accuracy_overhead": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            "ours_lowsnr": "docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md",
        },
        "definition": {
            "axis1": "AWGN final accuracy",
            "axis2": "inverse-normalized AWGN communication overhead in GB",
            "axis3": "normalized Rayleigh -6 dB accuracy",
        },
        "summary": summary,
    }
    with open(os.path.join(OUTPUT_DIR, "cifar10_accuracy_overhead_lowsnr_radar_summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()
