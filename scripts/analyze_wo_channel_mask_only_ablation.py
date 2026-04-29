import glob
import json
import os
from pathlib import Path

import numpy as np


BASELINE_ROOT = "/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun"
PROXY_ROOT = "/workspace/tmp/2026-04-15/2026-04-15-cifar10-channel-specific-ablation"
EXACT_ROOT = "/workspace/tmp/2026-04-15/2026-04-15-cifar10-wo-channel-mask-only-ablation"
DOC_DIR = Path(
    "/workspace/docs/experiments/2026-04-15/2026-04-15_18-15_v01_wo-channel-mask-only-ablation-plan"
)

CHANNELS = {
    "awgn": {
        "beta": 0.05,
        "film_max_t": 0.7,
        "film_min_t": 0.2,
    },
    "rayleigh": {
        "beta": 0.1,
        "film_max_t": 0.7,
        "film_min_t": 0.4,
    },
}

VARIANTS = {
    "baseline": {
        "root": BASELINE_ROOT,
        "algorithm": "SSFLv6",
        "require_channel_allpass": False,
    },
    "proxy_wo_film": {
        "root": PROXY_ROOT,
        "algorithm": "SSFLv6_w_o_film",
        "require_channel_allpass": False,
    },
    "exact_wo_channel_mask": {
        "root": EXACT_ROOT,
        "algorithm": "SSFLv6",
        "require_channel_allpass": True,
    },
}

SEEDS = [1, 2, 3, 4]


def find_npz(root: str, algorithm: str, channel: str, beta: float, film_max_t: float, film_min_t: float, seed: int, require_channel_allpass: bool) -> str:
    pattern = os.path.join(
        root,
        "**",
        f"beta_{beta:g}",
        "pruning_threshold_1.0",
        f"film_max_t_{film_max_t:g}",
        f"film_min_t_{film_min_t:g}",
        "**",
        algorithm,
        "snr_10",
        "compress_4096",
        f"channel_type_{channel}",
        f"seed_{seed}.npz",
    )
    hits = sorted(glob.glob(pattern, recursive=True))
    if require_channel_allpass:
        hits = [p for p in hits if "channel_mask_allpass_1" in p]
    else:
        hits = [p for p in hits if "channel_mask_allpass_1" not in p]
    if len(hits) != 1:
        raise RuntimeError(
            "Expected 1 artifact, got "
            f"{len(hits)} for root={root}, algorithm={algorithm}, channel={channel}, "
            f"beta={beta}, film_max_t={film_max_t}, film_min_t={film_min_t}, seed={seed}"
        )
    return hits[0]


def metric_bundle(npz_path: str) -> dict:
    data = np.load(npz_path, allow_pickle=True)
    train_acc = np.asarray(data["train_acc"], dtype=float).reshape(-1)
    comm_mb = np.asarray(data["comm"], dtype=float).reshape(-1)
    snrs = np.asarray(data["test_snrs"], dtype=float).reshape(-1)
    snr_accs = np.asarray(data["snr_accs"], dtype=float).reshape(-1)
    snr_map = {int(round(snr)): float(acc) for snr, acc in zip(snrs, snr_accs)}
    return {
        "final_acc": float(train_acc[-1]),
        "best_acc": float(np.max(train_acc)),
        "comm_mb": float(comm_mb[-1]),
        "comm_gb": float(comm_mb[-1] / 1024.0),
        "minus6_acc": float(snr_map[-6]),
        "plus12_acc": float(snr_map[12]),
    }


def aggregate_variant(channel: str, variant_key: str) -> dict:
    channel_cfg = CHANNELS[channel]
    variant_cfg = VARIANTS[variant_key]
    seed_rows = []
    for seed in SEEDS:
        npz_path = find_npz(
            root=variant_cfg["root"],
            algorithm=variant_cfg["algorithm"],
            channel=channel,
            beta=channel_cfg["beta"],
            film_max_t=channel_cfg["film_max_t"],
            film_min_t=channel_cfg["film_min_t"],
            seed=seed,
            require_channel_allpass=variant_cfg["require_channel_allpass"],
        )
        metrics = metric_bundle(npz_path)
        metrics["seed"] = seed
        metrics["npz_path"] = npz_path
        seed_rows.append(metrics)

    def mean_std(key: str) -> tuple[float, float]:
        arr = np.asarray([row[key] for row in seed_rows], dtype=float)
        return float(np.mean(arr)), float(np.std(arr, ddof=0))

    final_acc_mean, final_acc_std = mean_std("final_acc")
    best_acc_mean, best_acc_std = mean_std("best_acc")
    comm_mb_mean, comm_mb_std = mean_std("comm_mb")
    comm_gb_mean, comm_gb_std = mean_std("comm_gb")
    minus6_mean, minus6_std = mean_std("minus6_acc")
    plus12_mean, plus12_std = mean_std("plus12_acc")

    return {
        "seeds": seed_rows,
        "summary": {
            "final_acc_mean": final_acc_mean,
            "final_acc_std": final_acc_std,
            "best_acc_mean": best_acc_mean,
            "best_acc_std": best_acc_std,
            "comm_mb_mean": comm_mb_mean,
            "comm_mb_std": comm_mb_std,
            "comm_gb_mean": comm_gb_mean,
            "comm_gb_std": comm_gb_std,
            "minus6_mean": minus6_mean,
            "minus6_std": minus6_std,
            "plus12_mean": plus12_mean,
            "plus12_std": plus12_std,
        },
    }


def delta_summary(new_summary: dict, base_summary: dict) -> dict:
    return {
        "final_acc_delta": float(new_summary["final_acc_mean"] - base_summary["final_acc_mean"]),
        "comm_mb_delta": float(new_summary["comm_mb_mean"] - base_summary["comm_mb_mean"]),
        "comm_gb_delta": float(new_summary["comm_gb_mean"] - base_summary["comm_gb_mean"]),
        "minus6_delta": float(new_summary["minus6_mean"] - base_summary["minus6_mean"]),
        "plus12_delta": float(new_summary["plus12_mean"] - base_summary["plus12_mean"]),
        "best_acc_delta": float(new_summary["best_acc_mean"] - base_summary["best_acc_mean"]),
    }


def main() -> None:
    output = {}
    for channel in CHANNELS:
        output[channel] = {}
        for variant_key in VARIANTS:
            output[channel][variant_key] = aggregate_variant(channel, variant_key)
        baseline_summary = output[channel]["baseline"]["summary"]
        output[channel]["exact_vs_baseline"] = delta_summary(
            output[channel]["exact_wo_channel_mask"]["summary"],
            baseline_summary,
        )
        output[channel]["proxy_vs_baseline"] = delta_summary(
            output[channel]["proxy_wo_film"]["summary"],
            baseline_summary,
        )
        output[channel]["exact_vs_proxy"] = delta_summary(
            output[channel]["exact_wo_channel_mask"]["summary"],
            output[channel]["proxy_wo_film"]["summary"],
        )

    DOC_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOC_DIR / "summary.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
