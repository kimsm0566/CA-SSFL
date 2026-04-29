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
    "2026-04-16_22-05_v01_cifar10-radar-tradeoff-candidates/figures"
)

METHODS = {
    "SFL": {
        "accuracy_awgn": 53.70,
        "comm_mb_awgn": 172882.75,
        "final_acc_rayleigh": 51.07,
        "minus6_acc_rayleigh": 44.92,
        "color": "#ff5a52",
        "marker": "o",
    },
    "SC-USFL": {
        "accuracy_awgn": 39.76,
        "comm_mb_awgn": 23821.53,
        "final_acc_rayleigh": 40.90,
        "minus6_acc_rayleigh": 40.09,
        "color": "#4aa3ff",
        "marker": "s",
    },
    "CA-SSFL (Ours)": {
        "accuracy_awgn": 41.71,
        "comm_mb_awgn": 14363.28,
        "final_acc_rayleigh": 40.41,
        "minus6_acc_rayleigh": 37.88,
        "color": "#2ca25f",
        "marker": "^",
    },
}

CANDIDATES = {
    "candidate1_low_snr_robustness": {
        "title": "Candidate 1: Low-SNR Robustness",
        "axes": [
            "Accuracy",
            "1 / Communication\nLatency",
            "Low-SNR\nRobustness",
        ],
    },
    "candidate2_channel_robustness": {
        "title": "Candidate 2: Channel Robustness",
        "axes": [
            "Accuracy",
            "1 / Communication\nLatency",
            "Channel\nRobustness",
        ],
    },
    "candidate3_comm_efficiency": {
        "title": "Candidate 3: Communication Efficiency",
        "axes": [
            "Accuracy",
            "1 / Communication\nLatency",
            "Communication\nEfficiency",
        ],
    },
    "candidate4_worst_case_accuracy": {
        "title": "Candidate 4: Worst-Case Accuracy",
        "axes": [
            "Accuracy",
            "1 / Communication\nLatency",
            "Worst-Case\nAccuracy",
        ],
    },
}


def compute_summary():
    max_accuracy = max(v["accuracy_awgn"] for v in METHODS.values())
    min_comm = min(v["comm_mb_awgn"] for v in METHODS.values())

    channel_gaps = {
        label: abs(values["accuracy_awgn"] - values["final_acc_rayleigh"])
        for label, values in METHODS.items()
    }
    min_gap = min(channel_gaps.values())

    comm_eff = {
        label: values["accuracy_awgn"] / values["comm_mb_awgn"]
        for label, values in METHODS.items()
    }
    max_eff = max(comm_eff.values())

    worst_case = {
        label: min(
            values["accuracy_awgn"],
            values["final_acc_rayleigh"],
            values["minus6_acc_rayleigh"],
        )
        for label, values in METHODS.items()
    }
    max_worst = max(worst_case.values())

    low_snr_max = max(v["minus6_acc_rayleigh"] for v in METHODS.values())

    summary = {}
    for label, values in METHODS.items():
        summary[label] = {
            "raw": {
                "accuracy_awgn": values["accuracy_awgn"],
                "comm_mb_awgn": values["comm_mb_awgn"],
                "final_acc_rayleigh": values["final_acc_rayleigh"],
                "minus6_acc_rayleigh": values["minus6_acc_rayleigh"],
                "channel_gap_abs": channel_gaps[label],
                "communication_efficiency": comm_eff[label],
                "worst_case_accuracy": worst_case[label],
            },
            "candidate1_low_snr_robustness": {
                "accuracy": values["accuracy_awgn"] / max_accuracy,
                "inv_comm_latency": min_comm / values["comm_mb_awgn"],
                "third_axis": values["minus6_acc_rayleigh"] / low_snr_max,
            },
            "candidate2_channel_robustness": {
                "accuracy": values["accuracy_awgn"] / max_accuracy,
                "inv_comm_latency": min_comm / values["comm_mb_awgn"],
                "third_axis": min_gap / channel_gaps[label],
            },
            "candidate3_comm_efficiency": {
                "accuracy": values["accuracy_awgn"] / max_accuracy,
                "inv_comm_latency": min_comm / values["comm_mb_awgn"],
                "third_axis": comm_eff[label] / max_eff,
            },
            "candidate4_worst_case_accuracy": {
                "accuracy": values["accuracy_awgn"] / max_accuracy,
                "inv_comm_latency": min_comm / values["comm_mb_awgn"],
                "third_axis": worst_case[label] / max_worst,
            },
        }
    return summary


def draw_radar(ax, candidate_key, candidate_cfg, summary):
    angles = np.linspace(0, 2 * math.pi, 3, endpoint=False).tolist()
    angles += angles[:1]

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(candidate_cfg["axes"], fontsize=10, fontweight="semibold")
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
    ax.grid(color="#9aa0a6", alpha=0.55, linewidth=0.8)
    ax.spines["polar"].set_color("#80868b")
    ax.spines["polar"].set_linewidth(1.0)
    ax.set_title(candidate_cfg["title"], fontsize=12, fontweight="bold", pad=20)

    for label, method_cfg in METHODS.items():
        values = summary[label][candidate_key]
        data = [
            values["accuracy"],
            values["inv_comm_latency"],
            values["third_axis"],
        ]
        data += data[:1]
        ax.plot(
            angles,
            data,
            color=method_cfg["color"],
            linewidth=2.0,
            marker=method_cfg["marker"],
            markersize=5,
            label=label,
        )
        ax.fill(angles, data, color=method_cfg["color"], alpha=0.14)


def plot_individual(candidate_key, candidate_cfg, summary):
    fig, ax = plt.subplots(figsize=(7.0, 6.2), subplot_kw={"polar": True})
    draw_radar(ax, candidate_key, candidate_cfg, summary)
    legend = ax.legend(loc="lower center", bbox_to_anchor=(1.32, 1.14), frameon=True, fontsize=9)
    legend.get_frame().set_alpha(0.95)
    fig.tight_layout()

    png_path = os.path.join(OUTPUT_DIR, f"{candidate_key}.png")
    pdf_path = os.path.join(OUTPUT_DIR, f"{candidate_key}.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def plot_panel(summary):
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(8, 8),
        subplot_kw={"polar": True},
    )
    axes = axes.flatten()

    for ax, (candidate_key, candidate_cfg) in zip(axes, CANDIDATES.items()):
        draw_radar(ax, candidate_key, candidate_cfg, summary)

    handles, labels = axes[0].get_legend_handles_labels()
    legend = fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True, bbox_to_anchor=(0.5, 0.98))
    legend.get_frame().set_alpha(0.96)

    fig.tight_layout(rect=[0, 0.05, 1, 0.93])

    png_path = os.path.join(OUTPUT_DIR, "cifar10_radar_tradeoff_candidates_panel.png")
    pdf_path = os.path.join(OUTPUT_DIR, "cifar10_radar_tradeoff_candidates_panel.pdf")
    fig.savefig(png_path, dpi=240, bbox_inches="tight")
    fig.savefig(pdf_path, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = compute_summary()

    for candidate_key, candidate_cfg in CANDIDATES.items():
        plot_individual(candidate_key, candidate_cfg, summary)

    plot_panel(summary)

    payload = {
        "sources": {
            "accuracy_and_comm": "docs/experiments/2026-04-09/2026-04-09_16-40_v01_cross-benchmark-rayleigh-awgn/RESULT.md",
            "ours_awgn_rayleigh": "docs/experiments/2026-04-15/2026-04-15_12-20_v01_channel-specific-ablation-plan/RESULT.md",
        },
        "definitions": {
            "candidate1": "third axis = normalized Rayleigh -6 dB accuracy",
            "candidate2": "third axis = normalized inverse |AWGN final acc - Rayleigh final acc|",
            "candidate3": "third axis = normalized AWGN final accuracy / AWGN communication MB",
            "candidate4": "third axis = normalized min(AWGN final acc, Rayleigh final acc, Rayleigh -6 dB acc)",
        },
        "summary": summary,
    }
    with open(os.path.join(OUTPUT_DIR, "cifar10_radar_tradeoff_candidates_summary.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()
