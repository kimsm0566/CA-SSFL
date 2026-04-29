import glob
import json
import os
from pathlib import Path

import numpy as np


RESULT_ROOT = "/workspace/tmp/2026-04-14/2026-04-14-table1-blockB-channel-specific-rerun"
OUT_DIR = "/workspace/docs/experiments/2026-04-14/2026-04-14_23-32_v01_table1-blockB-channel-specific-rerun"

FILM_PAIRS = [
    (0.7, 0.2),
    (0.7, 0.3),
    (0.7, 0.4),
    (0.8, 0.2),
    (0.8, 0.3),
    (0.8, 0.4),
    (0.9, 0.2),
    (0.9, 0.3),
    (0.9, 0.4),
]

CHANNELS = {
    "awgn": {"beta": 0.05, "pruning_threshold": 1.0},
    "rayleigh": {"beta": 0.1, "pruning_threshold": 1.0},
}


def find_npz(channel: str, beta: float, threshold: float, fmax: float, fmin: float, seed: int) -> str:
    pattern = os.path.join(
        RESULT_ROOT,
        "**",
        f"beta_{beta:g}",
        "pruning_threshold_*",
        f"film_max_t_{fmax:g}",
        f"film_min_t_{fmin:g}",
        "**",
        f"channel_type_{channel}",
        f"seed_{seed}.npz",
    )
    hits = glob.glob(pattern, recursive=True)
    if len(hits) != 1:
        raise RuntimeError(
            f"Expected 1 artifact for channel={channel}, beta={beta}, threshold={threshold}, "
            f"fmax={fmax}, fmin={fmin}, seed={seed}, got {len(hits)}"
        )
    return hits[0]


def metric_bundle(npz_path: str) -> dict:
    d = np.load(npz_path, allow_pickle=True)
    train_acc = float(np.asarray(d["train_acc"])[-1])
    comm_gb = float(np.asarray(d["comm"])[-1]) / 1024.0
    snrs = np.asarray(d["test_snrs"])
    accs = np.asarray(d["snr_accs"])
    minus6 = float(accs[np.where(snrs == -6)[0][0]])
    plus12 = float(accs[np.where(snrs == 12)[0][0]])
    return {
        "final_acc": train_acc,
        "comm_gb": comm_gb,
        "minus6_acc": minus6,
        "plus12_acc": plus12,
    }


def aggregate_channel(channel: str, beta: float, threshold: float) -> list[dict]:
    rows = []
    for fmax, fmin in FILM_PAIRS:
        bundles = [
            metric_bundle(find_npz(channel, beta, threshold, fmax, fmin, seed))
            for seed in [1, 2, 3, 4]
        ]
        rows.append(
            {
                "film_max_t": fmax,
                "film_min_t": fmin,
                "final_acc": float(np.mean([b["final_acc"] for b in bundles])),
                "comm_gb": float(np.mean([b["comm_gb"] for b in bundles])),
                "minus6_acc": float(np.mean([b["minus6_acc"] for b in bundles])),
                "plus12_acc": float(np.mean([b["plus12_acc"] for b in bundles])),
            }
        )
    return rows


def best_summary(rows: list[dict]) -> dict:
    best_final = max(rows, key=lambda r: r["final_acc"])
    best_minus6 = max(rows, key=lambda r: r["minus6_acc"])
    lowest_comm = min(rows, key=lambda r: r["comm_gb"])
    return {
        "best_final": best_final,
        "best_minus6": best_minus6,
        "lowest_comm": lowest_comm,
    }


def latex_block(rows: list[dict]) -> str:
    parts = []
    grouped = {
        0.7: rows[0:3],
        0.8: rows[3:6],
        0.9: rows[6:9],
    }
    all_accs = [r["final_acc"] for r in rows]
    all_comms = [r["comm_gb"] for r in rows]
    top_acc = sorted(set(round(v, 2) for v in all_accs), reverse=True)[:2]
    low_comm = sorted(set(round(v, 2) for v in all_comms))[:2]

    for idx, fmax in enumerate([0.7, 0.8, 0.9]):
        grp = grouped[fmax]
        for j, row in enumerate(grp):
            acc = round(row["final_acc"], 2)
            comm = round(row["comm_gb"], 2)
            acc_str = f"{acc:.2f}"
            comm_str = f"{comm:.2f}"
            if acc == top_acc[0]:
                acc_str = f"\\textbf{{{acc_str}}}"
            elif len(top_acc) > 1 and acc == top_acc[1]:
                acc_str = f"\\underline{{{acc_str}}}"

            if comm == low_comm[0]:
                comm_str = f"\\textbf{{{comm_str}}}"
            elif len(low_comm) > 1 and comm == low_comm[1]:
                comm_str = f"\\underline{{{comm_str}}}"

            if j == 0:
                line = (
                    f"    \\multirow{{3}}{{*}}{{{fmax:.1f}}}\n"
                    f"        & {row['film_min_t']:.1f} & {acc_str} & {comm_str} \\\\"
                )
            else:
                line = f"        & {row['film_min_t']:.1f} & {acc_str} & {comm_str} \\\\"
            parts.append(line)
        if idx < 2:
            parts.append("    \\cmidrule(lr){1-4}")
    return "\n".join(parts)


def write_result_md(summary: dict) -> None:
    out = Path(OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    awgn = summary["awgn"]
    ray = summary["rayleigh"]
    text = f"""# Table I Block B 채널별 재실험 결과

## 설정

- `AWGN`: `beta=0.05`, `tau_VIB=1.0`
- `Rayleigh`: `beta=0.1`, `tau_VIB=1.0`
- seeds: `1,2,3,4`

## AWGN

- 최고 final acc: `film_max_t={awgn['best']['best_final']['film_max_t']:.1f}`, `film_min_t={awgn['best']['best_final']['film_min_t']:.1f}` -> `Acc {awgn['best']['best_final']['final_acc']:.2f}`, `Comm {awgn['best']['best_final']['comm_gb']:.2f} GB`
- 최고 `-6 dB`: `film_max_t={awgn['best']['best_minus6']['film_max_t']:.1f}`, `film_min_t={awgn['best']['best_minus6']['film_min_t']:.1f}` -> `-6 dB {awgn['best']['best_minus6']['minus6_acc']:.2f}`
- 최저 comm: `film_max_t={awgn['best']['lowest_comm']['film_max_t']:.1f}`, `film_min_t={awgn['best']['lowest_comm']['film_min_t']:.1f}` -> `Comm {awgn['best']['lowest_comm']['comm_gb']:.2f} GB`

## Rayleigh

- 최고 final acc: `film_max_t={ray['best']['best_final']['film_max_t']:.1f}`, `film_min_t={ray['best']['best_final']['film_min_t']:.1f}` -> `Acc {ray['best']['best_final']['final_acc']:.2f}`, `Comm {ray['best']['best_final']['comm_gb']:.2f} GB`
- 최고 `-6 dB`: `film_max_t={ray['best']['best_minus6']['film_max_t']:.1f}`, `film_min_t={ray['best']['best_minus6']['film_min_t']:.1f}` -> `-6 dB {ray['best']['best_minus6']['minus6_acc']:.2f}`
- 최저 comm: `film_max_t={ray['best']['lowest_comm']['film_max_t']:.1f}`, `film_min_t={ray['best']['lowest_comm']['film_min_t']:.1f}` -> `Comm {ray['best']['lowest_comm']['comm_gb']:.2f} GB`
"""
    (out / "RESULT.md").write_text(text, encoding="utf-8")


def main() -> None:
    summary = {}
    for channel, cfg in CHANNELS.items():
        rows = aggregate_channel(channel, cfg["beta"], cfg["pruning_threshold"])
        summary[channel] = {
            "fixed": cfg,
            "rows": rows,
            "best": best_summary(rows),
            "latex_block": latex_block(rows),
        }
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(OUT_DIR, "summary_blockB_channel_specific.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    write_result_md(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
