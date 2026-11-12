"""Recompute the headline metrics of every experiment from the saved result CSVs.

Reads the `*_evaluated.csv` files in <repo>/<model>/<condition>/ and writes
  Final_Comparison/all_conditions_summary.csv   (machine-readable)
  Final_Comparison/all_conditions_summary.md    (table used in the README)

Metrics (same definitions as in the notebooks):
  MAE / RMSE / MAPE   on rows with a parseable predicted count (MAPE only where true count > 0)
  accuracy / precision / recall / F1   on rows with a parseable predicted density (weighted averages)

Where a model has no *_evaluated.csv for a condition, the raw result CSV is merged with the ground
truth taken from another evaluated file (all experiments use the same 1600 test images).

Usage:  python scripts/summarize_results.py        (run from anywhere; needs pandas, numpy, scikit-learn)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]

MODELS = {            # display name -> folder
    "Qwen2.5-VL-3B": "qwen",
    "LLaVA-Interleave-0.5B": "llava",
    "Gemma 3 (4B)": "gemma",
    "GPT-6.1 Terra": "gpt",
}
CONDITIONS = [        # (label, folder candidates, A file, B file)
    ("5-shot", ["Five_Shot"], "{m}_experiment_{x}", "{m}_experiment_{x}"),
    ("Zero-shot", ["Zero_Shot", "Zero_shot"], "{m}_experiment_{x}_zeroshot", None),
    ("Zero-shot + density definition", ["Zero_Shot_Density"], "{m}_experiment_{x}_zeroshot_densitydef", None),
]


def find(folder_names, model_dir, stem):
    """Locate <model>/<folder>/<stem>_evaluated.csv (or the raw csv if no evaluated file exists)."""
    for fn in folder_names:
        base = ROOT / model_dir / fn
        for suffix, evaluated in (("_evaluated.csv", True), (".csv", False)):
            p = base / (stem + suffix)
            if p.exists():
                return p, evaluated
    return None, False


def ground_truth():
    gt = pd.read_csv(ROOT / "gemma" / "Five_Shot" / "gemma_experiment_A_evaluated.csv")
    return gt[["test_filename", "total_count", "crowd_density"]]


def metrics(df):
    v = df.dropna(subset=["predicted_count"])
    err = v.predicted_count - v.total_count
    nz = v.total_count > 0
    out = dict(
        n_valid_counts=len(v),
        MAE=err.abs().mean(),
        RMSE=float(np.sqrt((err ** 2).mean())),
        MAPE_pct=(err[nz].abs() / v.total_count[nz]).mean() * 100,
    )
    d = df.dropna(subset=["predicted_density"])
    y, p = d.crowd_density.astype(int), d.predicted_density.astype(int)
    out.update(
        n_valid_density=len(d),
        density_accuracy_pct=accuracy_score(y, p) * 100,
        density_precision_pct=precision_score(y, p, average="weighted", zero_division=0) * 100,
        density_recall_pct=recall_score(y, p, average="weighted", zero_division=0) * 100,
        density_f1_pct=f1_score(y, p, average="weighted", zero_division=0) * 100,
    )
    return out


def main():
    gt = ground_truth()
    rows = []
    for model_name, model_dir in MODELS.items():
        for cond_label, folders, stem_tpl, _ in CONDITIONS:
            for exp in ("A", "B"):
                stem = stem_tpl.format(m=model_dir, x=exp)
                path, evaluated = find(folders, model_dir, stem)
                if path is None and cond_label == "5-shot" and exp == "B" and model_dir == "qwen":
                    path, evaluated = ROOT / "qwen" / "Five_Shot" / "qwen_experiment_B_evaluated.csv", True
                if path is None:
                    continue
                df = pd.read_csv(path)
                if not evaluated:
                    df = df.merge(gt, on="test_filename", how="left")
                rows.append(dict(model=model_name, condition=cond_label, experiment=exp,
                                 yolo_count_in_prompt="yes" if exp == "B" else "no",
                                 source=str(path.relative_to(ROOT)).replace("\\", "/"),
                                 from_raw_csv=not evaluated, **metrics(df)))
    out = pd.DataFrame(rows)

    # YOLO baseline (the count shown to the model in every Experiment B)
    yolo = pd.read_csv(ROOT / "yolo" / "yolo_predictions.csv").rename(columns={"image_id": "test_filename"})
    y = yolo.merge(gt, on="test_filename")
    e = y.predicted_count - y.total_count
    yolo_row = dict(MAE=e.abs().mean(), RMSE=float(np.sqrt((e ** 2).mean())),
                    MAPE_pct=(e.abs()[y.total_count > 0] / y.total_count[y.total_count > 0]).mean() * 100)

    dest = ROOT / "Final_Comparison"
    dest.mkdir(exist_ok=True)
    out.round(2).to_csv(dest / "all_conditions_summary.csv", index=False)

    lines = ["| Model | Condition | Exp. | MAE | RMSE | MAPE % | Density acc. % | Density F1 % | Valid counts |",
             "|---|---|---|---|---|---|---|---|---|"]
    for _, r in out.iterrows():
        lines.append(f"| {r.model} | {r.condition} | {r.experiment} | {r.MAE:.2f} | {r.RMSE:.2f} | {r.MAPE_pct:.2f} | "
                     f"{r.density_accuracy_pct:.2f} | {r.density_f1_pct:.2f} | {int(r.n_valid_counts)} |")
    lines.append(f"| *YOLO baseline (count only)* | — | — | {yolo_row['MAE']:.2f} | {yolo_row['RMSE']:.2f} | "
                 f"{yolo_row['MAPE_pct']:.2f} | — | — | 1600 |")
    (dest / "all_conditions_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print("\nrows from raw csv (no *_evaluated.csv present):")
    print(out[out.from_raw_csv][["model", "condition", "experiment"]].to_string(index=False))


if __name__ == "__main__":
    main()
