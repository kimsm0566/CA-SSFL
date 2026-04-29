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
    "2026-04-16_21-35_v01_cifar10-awgn-radar-tradeoff/figures"
)

RESULT = {
    "SFL": {
        "accuracy": 53.70,
        "comm_mb": 172882.75,
        "comp_mflops": 70.50,
        "color": "#ff5a52",
        "marker": "o",
    },
    "SC-USFL": {
        "accuracy": 39.76,
        "comm_mb": 23821.53,
        "comp_mflops": 80.27,
        "color": "#4aa3ff",
        "marker": "s",
    },
    "CA-SSFL (Ours)": {
        "accuracy": 41.71,
        "comm_mb": 14363.28,
        "comp_mflops": 113.84,
        "color": "#2ca25f",
        "marker": "^",
    },
}

AXES = [
    "Accuracy",
    "1 / Communication\nLatency",
    "1 / Computation\nLatency",
]


def normalize_scores():
    max_acc = max(v["accuracy"] for v in RESULT.values())
    min_comm = min(v["comm_mb"] for v in RESULT.values())
    min_comp = min(v["comp_mflops"] for v in RESULT.values())

    summary = {}
    for label, values in RESULT.items():
        summary[label] = {
            "accuracy_raw": values["accuracy"],
            "comm_mb_raw": values["comm_mb"],
            "comp_mflops_raw": values["comp_mflops"],
            "accuracy_norm": values["accuracy"] / max_acc,
            "inv_comm_latency_norm": min_comm / values["comm_mb"],
            "inv_comp_latency_norm": min_comp / values["comp_mflops"],
        }
    return summary


def plot_radar(summary):
    labels = AXES
    num_vars = len(labels)
    angles = np.linspace(0, 2 * math.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7.2, 6.2), subplot_kw={"polar": True})
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11, fontweight="semibold")
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.grid(color="#9aa0a6", alpha=0.55, linewidth=0.8)
    ax.spines["polar"].set_color("#80868b")
    ax.spines["polar"].set_linewidth(1.1)

    for label, values in summary.items():
        config = RESULT[label]
        data = [
            values["accuracy_norm"],
            values["inv_comm_latency_norm"],
            values["inv_comp_latency_norm"],
        ]
        data += data[:1]
        ax.plot(
            angles,
            data,
            color=config["color"],
            linewidth=2.2,
            marker=config["marker"],
            markersize=6,
            label=label,
        )
        ax.fill(angles, data, color=config["color"], alpha=0.16)

    ax.set_title(
        "CIFAR-10 AWGN: Accuracy-Latency Trade-off",
        fontsize=13,
        fontweight="bold",
        pad=24,
    )
    legend = ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.30, 1.15),
        frameon=True,
        fontsize=9,
    )
    legend.get_frame().set_alpha(0.95)

    fig.text(
        0.5,
        0.02,
        "Higher is better on all axes. Communication latency is normalized from total MB,\n"
        "and computation latency is normalized from architecture-level MFLOPs.",
        ha="center",
        va="bottom",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 1])

    png_path = os.path.join(OUTPUT_DIR, "cifar10_awgn_radar_tradeoff.png")
    pdf_path = os.path.join(OUTPUT_DIR, "cifar10_awgn_radar_tradeoff.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = normalize_scores()
    plot_radar(summary)
    with open(os.path.join(OUTPUT_DIR, "cifar10_awgn_radar_tradeoff_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
