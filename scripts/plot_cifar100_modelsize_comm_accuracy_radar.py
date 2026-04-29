import glob
import json
import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# Global style: Times New Roman
# -----------------------------
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif"]
matplotlib.rcParams["axes.unicode_minus"] = False
plt.switch_backend("agg")


OUTPUT_DIR = (
    "/home/sunmin/SFL_Semantic/results/"
    "2026-04-16_23-55_v01_cifar100-modelsize-comm-accuracy-radar/figures"
)

METHOD_STYLES = {
    "SFL": {"color": "black", "marker": "o", "linestyle": "-"},
    "SC-USFL": {"color": "blue", "marker": "s", "linestyle": "-"},
    "CA-SSFL (Ours)": {"color": "red", "marker": "D", "linestyle": "-"},
}

TOTAL_MODEL_SIZE_MB = {
    "SFL": 42.62,
    "SC-USFL": 45.37,
    "CA-SSFL (Ours)": 44.93,
}

# 12시 방향부터 시계방향
AXES = [
    "1 / Avg. Comm.\nOverhead",
    "Rayleigh\nAccuracy",
    "1 / Total Model Size",
    "AWGN\nAccuracy",
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
    return {
        "title": "",
        "awgn": {
            "SFL": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8/**/SFL/snr_10/compress_4096/channel_type_awgn/seed_*.npz"
            ),
            "SC-USFL": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-cifar100-awgn-threeway-benchmark-nclients8/**/SC-USFL/snr_10/compress_1352/channel_type_awgn/seed_*.npz"
            ),
            "CA-SSFL (Ours)": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar100-awgn-ca-ssfl-channel-specific-rerun/**/SSFLv6/snr_10/compress_4096/channel_type_awgn/seed_*.npz"
            ),
        },
        "rayleigh": {
            "SFL": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-cifar100-rayleigh-threeway-benchmark-nclients8/**/SFL/snr_10/compress_4096/channel_type_rayleigh/seed_*.npz"
            ),
            "SC-USFL": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-11/2026-04-11-cifar100-rayleigh-threeway-benchmark-nclients8/**/SC-USFL/snr_10/compress_1352/channel_type_rayleigh/seed_*.npz"
            ),
            "CA-SSFL (Ours)": load_npz_group(
                "/home/sunmin/SFL_Semantic/tmp/2026-04-15/2026-04-15-cifar100-rayleigh-ca-ssfl-channel-specific-rerun/**/SSFLv6/snr_10/compress_4096/channel_type_rayleigh/seed_*.npz"
            ),
        },
    }


def normalize_metrics(metrics):
    awgn_max_acc = max(metrics["awgn"][method]["final_acc_mean"] for method in METHOD_STYLES)
    rayleigh_max_acc = max(metrics["rayleigh"][method]["final_acc_mean"] for method in METHOD_STYLES)

    avg_comm = {}
    for method in METHOD_STYLES:
        avg_comm[method] = 0.5 * (
            metrics["awgn"][method]["comm_mb_mean"] + metrics["rayleigh"][method]["comm_mb_mean"]
        )

    min_avg_comm = min(avg_comm.values())
    min_model_size = min(TOTAL_MODEL_SIZE_MB.values())

    normalized = {"title": metrics["title"], "methods": {}}
    for method in METHOD_STYLES:
        normalized["methods"][method] = {
            "inv_total_model_size": min_model_size / TOTAL_MODEL_SIZE_MB[method],
            "inv_avg_comm_overhead": min_avg_comm / avg_comm[method],
            "awgn_accuracy": metrics["awgn"][method]["final_acc_mean"] / awgn_max_acc,
            "rayleigh_accuracy": metrics["rayleigh"][method]["final_acc_mean"] / rayleigh_max_acc,
            "raw": {
                "total_model_size_mb": TOTAL_MODEL_SIZE_MB[method],
                "awgn_final_acc_mean": metrics["awgn"][method]["final_acc_mean"],
                "rayleigh_final_acc_mean": metrics["rayleigh"][method]["final_acc_mean"],
                "awgn_comm_gb_mean": metrics["awgn"][method]["comm_mb_mean"] / 1024.0,
                "rayleigh_comm_gb_mean": metrics["rayleigh"][method]["comm_mb_mean"] / 1024.0,
                "avg_comm_gb_mean": avg_comm[method] / 1024.0,
            },
        }
    return normalized


def draw_radar(ax, title, method_summary):
    angles = np.linspace(0, 2 * math.pi, len(AXES), endpoint=False).tolist()
    angles += angles[:1]

    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(AXES, fontsize=28, fontweight="bold")
    ax.tick_params(axis="x", pad=20)

    ax.set_ylim(0, 1.0)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(
        ["0.2", "0.4", "0.6", "0.8", "1.0"],
        fontsize=18
    )
    ax.set_rlabel_position(45)
    ax.grid(color="#bdbdbd", alpha=0.8, linewidth=0.8)
    ax.spines["polar"].set_color("#666666")
    ax.spines["polar"].set_linewidth(1.0)

    if title:
        ax.set_title(title, fontsize=26, fontweight="bold", pad=2)

    for method, style in METHOD_STYLES.items():
        vals = method_summary[method]
        data = [
            vals["inv_avg_comm_overhead"],   # 12시
            vals["rayleigh_accuracy"],      # 3시
            vals["inv_total_model_size"],  # 6시
            vals["awgn_accuracy"],          # 9시
        ]
        data += data[:1]

        ax.plot(
            angles,
            data,
            color=style["color"],
            linewidth=1.8,
            linestyle=style["linestyle"],
            marker=style["marker"],
            markersize=4.5,
            label=method,
        )
        ax.fill(angles, data, color=style["color"], alpha=0.08)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    metrics = build_metrics()
    normalized = normalize_metrics(metrics)

    fig, ax = plt.subplots(figsize=(8.8, 7.6), subplot_kw={"polar": True})
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    draw_radar(ax, normalized["title"], normalized["methods"])

    legend = ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        frameon=True,
        fontsize=21,
    )
    legend.get_frame().set_alpha(0.95)
    legend.get_frame().set_edgecolor("#cccccc")
    legend.get_frame().set_linewidth(1.0)

    fig.subplots_adjust(top=0.90, bottom=0.24, left=0.08, right=0.92)

    png_path = os.path.join(OUTPUT_DIR, "cifar100_modelsize_comm_accuracy_radar.png")
    pdf_path = os.path.join(OUTPUT_DIR, "cifar100_modelsize_comm_accuracy_radar.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    payload = {
        "axes": {
            "axis1": "1 / Avg. Comm. Overhead",
            "axis2": "Rayleigh Accuracy",
            "axis3": "1 / Total Model Size",
            "axis4": "AWGN Accuracy",
        },
        "summary": normalized,
    }

    with open(
        os.path.join(OUTPUT_DIR, "cifar100_modelsize_comm_accuracy_radar_summary.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()