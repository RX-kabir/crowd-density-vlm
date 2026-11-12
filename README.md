# crowd-density-vlm

**Can vision-language models count a crowd and judge how dense it is — and does a YOLO count, a few labelled examples, or a written definition of "density" help?**

This repository benchmarks vision-language models (VLMs) on two tasks over the **1,600-image JHU-CROWD++ test set**:

1. **Crowd counting** — predict the exact number of people (metrics: MAE, RMSE, MAPE).
2. **Crowd-density classification** — predict Low / Medium / High (0 / 1 / 2) (metrics: accuracy, weighted precision / recall / F1).

Every model is tested under the same six conditions (3 prompting strategies × with / without an auxiliary YOLO count), against a YOLO-only counting baseline. Planned next: more closed models and a **fine-tuned VLM** for density estimation (see [docs/ROADMAP.md](docs/ROADMAP.md)).

---

## Experiment matrix

| Prompting strategy | Experiment A (image only) | Experiment B (image + YOLO-predicted count) |
|---|---|---|
| **5-shot** — five labelled support examples, then the test image | ✔ | ✔ |
| **Zero-shot** — no examples; density labels are bare ("0 = Low …") | ✔ | ✔ |
| **Zero-shot + density definition** — no examples; Low / Medium / High defined visually in the prompt | ✔ | ✔ |

| Model | Type | Status |
|---|---|---|
| Qwen2.5-VL-3B | open-source, greedy decoding | all 6 conditions done |
| LLaVA-Interleave-0.5B | open-source, greedy decoding | all 6 conditions done |
| Gemma 3 (4B) | open-source, greedy decoding | all 6 conditions done |
| GPT-6.1 Terra | closed, OpenAI Batch API, medium reasoning effort (non-deterministic) | all 6 conditions done |
| Claude Haiku 5.5 | closed | planned |
| Gemini 3.8 | closed | planned |
| Fine-tuned VLM | to be fine-tuned for density estimation | planned |

The exact prompt text of each condition is in [`prompts/`](prompts/). Full protocol: [docs/experiment_design.md](docs/experiment_design.md).

---

## Headline results

All numbers are recomputed from the saved CSVs by [`scripts/summarize_results.py`](scripts/summarize_results.py) (table also in [`Final_Comparison/all_conditions_summary.csv`](Final_Comparison/all_conditions_summary.csv)). Lower is better for MAE / RMSE / MAPE; higher is better for density metrics. "Valid counts" is the number of the 1,600 responses with a parseable count.

| Model | Condition | Exp. | MAE | RMSE | MAPE % | Density acc. % | Density F1 % | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 5-shot | A | 404.15 | 1203.67 | 329.41 | 67.50 | 63.25 | 1600 |
| Qwen2.5-VL-3B | 5-shot | B | 259.16 | 884.06 | 133.52 | 57.94 | 58.73 | 1600 |
| Qwen2.5-VL-3B | Zero-shot | A | 725.92 | 2469.95 | 194.24 | 66.75 | 54.85 | 1600 |
| Qwen2.5-VL-3B | Zero-shot | B | 262.36 | 922.89 | 67.82 | 65.81 | 55.71 | 1600 |
| Qwen2.5-VL-3B | Zero-shot + density definition | A | 694.18 | 2692.04 | 174.09 | 68.00 | 58.02 | 1600 |
| Qwen2.5-VL-3B | Zero-shot + density definition | B | 258.27 | 909.44 | 66.70 | 66.69 | 58.40 | 1600 |
| LLaVA-Interleave-0.5B | 5-shot | A | 503.34 | 1184.49 | 1013.03 | 47.96 | 49.51 | 1577 |
| LLaVA-Interleave-0.5B | 5-shot | B | 321.11 | 784.55 | 524.81 | 37.75 | 41.40 | 1597 |
| LLaVA-Interleave-0.5B | Zero-shot | A | 380.67 | 683.61 | 216.31 | 12.71 | 2.90 | 617 |
| LLaVA-Interleave-0.5B | Zero-shot | B | 233.86 | 679.08 | 53.29 | 14.56 | 4.65 | 1599 |
| LLaVA-Interleave-0.5B | Zero-shot + density definition | A | 411.84 | 747.17 | 269.81 | 14.52 | 3.68 | 361 |
| LLaVA-Interleave-0.5B | Zero-shot + density definition | B | 235.07 | 680.04 | 55.71 | 14.20 | 4.01 | 1598 |
| Gemma 3 (4B) | 5-shot | A | 264.87 | 950.48 | 104.21 | 69.00 | 67.15 | 1600 |
| Gemma 3 (4B) | 5-shot | B | 240.83 | 881.38 | 89.76 | 66.44 | 62.25 | 1600 |
| Gemma 3 (4B) | Zero-shot | A | 332.24 | 2687.40 | 61.82 | 64.69 | 63.17 | 1599 |
| Gemma 3 (4B) | Zero-shot | B | 234.54 | 882.49 | 56.67 | 64.69 | 63.28 | 1600 |
| Gemma 3 (4B) | Zero-shot + density definition | A | 326.50 | 2397.06 | 66.12 | 42.50 | 42.85 | 1599 |
| Gemma 3 (4B) | Zero-shot + density definition | B | 245.46 | 926.05 | 58.98 | 37.44 | 36.35 | 1600 |
| GPT-6.1 Terra | 5-shot | A | 140.21 | 599.80 | 50.17 | 77.81 | 77.25 | 1600 |
| GPT-6.1 Terra | 5-shot | B | 138.11 | 494.14 | 29.97 | 77.81 | 77.52 | 1600 |
| GPT-6.1 Terra | Zero-shot | A | 198.45 | 773.75 | 54.86 | 75.19 | 71.00 | 1600 |
| GPT-6.1 Terra | Zero-shot | B | 133.87 | 490.77 | 45.64 | 76.25 | 72.77 | 1600 |
| GPT-6.1 Terra | Zero-shot + density definition | A | 169.95 | 607.96 | 55.27 | 78.88 | 76.68 | 1600 |
| GPT-6.1 Terra | Zero-shot + density definition | B | 137.52 | 558.98 | 36.19 | 79.69 | 77.73 | 1600 |
| *YOLO baseline (count only)* | — | — | 241.87 | 737.65 | 50.64 | — | — | 1600 |

Short reading of the table (details in the findings documents below):

- **GPT-6.1 Terra has the lowest MAE and MAPE and the highest density accuracy in every one of the six conditions** (RMSE too, except zero-shot A, where LLaVA's 617 valid counts give a lower RMSE). But it differs from the open models in scale, architecture, serving *and* reasoning, so the gap cannot be attributed to one factor; it is also non-deterministic and was run once per condition.
- **The YOLO count's value depends on the model and the prompt.** For GPT it cuts MAE by 32.5% in zero-shot but only 1.5% with five labelled examples. Models use it differently: LLaVA and Qwen largely copy it, Gemma barely uses it, GPT treats it as a floor and revises upward.
- **A written density definition is not a free win:** a small gain for Qwen, a moderate gain for GPT, a reliability backfire for LLaVA and a severe accuracy drop for Gemma (64.69% → 42.50%).
- **Always predicting "High" already scores 66.44%** on density, so density accuracy has to be read against that baseline.

---

## Repository map

```
crowd-density-vlm/
├── README.md                 this file
├── docs/                     experiment design, how to reproduce, roadmap
├── prompts/                  exact prompt text for each of the six conditions
├── data/                     README (how to obtain the data) + test_labels.csv (ground truth + YOLO count, 1,600 rows)
├── support_mapping/          support_mapping.csv: the five support examples used for every test image
├── yolo/                     YOLO baseline predictions / evaluation (+ README with a known issue)
├── pipeline/                 notebooks that produced the YOLO predictions and the support mapping
├── qwen/  llava/  gemma/  gpt/
│   ├── Five_Shot/            notebooks, raw + evaluated CSVs, figures, findings (.md)
│   ├── Zero_Shot/
│   └── Zero_Shot_Density/
├── Final_Comparison/         cross-model report (open-source models) + all_conditions_summary.csv/.md
└── scripts/                  summarize_results.py, extract_prompts.py, gpt_analysis/ (figure + statistics scripts)
```

**File naming:** `{model}_experiment_{A|B}[_zeroshot[_densitydef]].csv` holds the raw responses; the same name with `_evaluated.csv` adds the ground truth (`total_count`, `crowd_density`). Findings documents are named `<Model>_<Condition>_Findings.md`; `*_A_vs_B_Comparison.md` compares the two experiments.

---

## Findings documents

| Model | 5-shot | Zero-shot | Zero-shot + density definition |
|---|---|---|---|
| Qwen2.5-VL-3B | [summary](qwen/Five_Shot/Qwen_Findings_Summary.md) | [A](qwen/Zero_Shot/Qwen_ZeroShot_A_Findings.md), [A vs B](qwen/Zero_Shot/Qwen_ZeroShot_A_vs_B_Comparison.md) | [A](qwen/Zero_Shot_Density/Qwen_DensityDef_ZeroShotA_Findings.md), [B](qwen/Zero_Shot_Density/Qwen_DensityDef_ZeroShotB_Findings.md) |
| LLaVA-Interleave-0.5B | [A](llava/Five_Shot/LLaVA_ExperimentA_Findings.md), [B](llava/Five_Shot/LLaVA_ExperimentB_Findings.md), [A vs B](llava/Five_Shot/LLaVA_A_vs_B_Comparison.md) | [A](llava/Zero_shot/) | [A](llava/Zero_Shot_Density/LLaVA_DensityDef_ZeroShotA_Findings.md), [B](llava/Zero_Shot_Density/LLaVA_DensityDef_ZeroShotB_Findings.md) |
| Gemma 3 (4B) | [A](gemma/Five_Shot/Gemma_ExperimentA_Findings.md), [A vs B](gemma/Five_Shot/Gemma_A_vs_B_Comparison.md) | [A](gemma/Zero_Shot/Gemma_ZeroShot_A_Findings.md), [A vs B](gemma/Zero_Shot/Gemma_ZeroShot_A_vs_B_Comparison.md) | [A](gemma/Zero_Shot_Density/Gemma_DensityDef_ZeroShotA_Findings.md), [B](gemma/Zero_Shot_Density/Gemma_DensityDef_ZeroShotB_Findings.md) |
| GPT-6.1 Terra | [A](gpt/Five_Shot/GPT_ExperimentA_Findings.md), [B](gpt/Five_Shot/GPT_ExperimentB_Findings.md), [A vs B](gpt/Five_Shot/GPT_A_vs_B_Comparison.md) | [A](gpt/Zero_Shot/GPT_ZeroShot_A_Findings.md), [B](gpt/Zero_Shot/GPT_ZeroShot_B_Findings.md), [A vs B](gpt/Zero_Shot/GPT_ZeroShot_A_vs_B_Comparison.md) | [A](gpt/Zero_Shot_Density/GPT_DensityDef_ZeroShotA_Findings.md), [B](gpt/Zero_Shot_Density/GPT_DensityDef_ZeroShotB_Findings.md) |

Cross-model reports: [Final_Comparison/Final_CrossModel_AllConditions_Findings.md](Final_Comparison/Final_CrossModel_AllConditions_Findings.md) (Qwen / LLaVA / Gemma, 12 conditions) and [Final_Comparison/DensityDef_CrossModel_Synthesis.md](Final_Comparison/DensityDef_CrossModel_Synthesis.md). **These two reports have not yet been updated to include GPT-6.1 Terra**; the table above already does.

---

## Reproducing

See [docs/reproducing.md](docs/reproducing.md). In short: obtain JHU-CROWD++ ([data/README.md](data/README.md)), build `Phase5_Input` with the notebooks in [`pipeline/`](pipeline/), then run the notebook of the condition you want in Colab / Kaggle. API keys (OpenAI) are read from Colab Secrets and are never stored in the repository.

---

## Known issues

1. **The YOLO count appears to be capped at 300.** No test image has a YOLO count above 300, 135 images are at exactly 300, and 99.3% of those have a true count above 300 (median 759). The inference notebook ([`pipeline/Phase4_YOLO_Inference.ipynb`](pipeline/Phase4_YOLO_Inference.ipynb)) calls `model.predict(..., conf=0.25)` without `max_det`, and the Ultralytics default is 300 detections per image — the likely cause (see [yolo/README.md](yolo/README.md)). This affects the YOLO baseline and **every Experiment B**. It has not been fixed or re-run.
2. **GPT-6.1 Terra is not deterministic** (no `temperature` in reasoning mode) and each condition was run once; run-to-run variance is unmeasured. This matters most for small differences, e.g. the GPT density-definition counting change.
3. **Token prices** used for GPT cost figures are third-party-reported and unverified.
4. `qwen/Zero_Shot_Density/` has no `*_evaluated.csv` for Experiment A (`summarize_results.py` recomputes it from the raw CSV).
5. Some notebooks (Qwen and Gemma 5-shot / zero-shot, LLaVA 5-shot B) are not in this repository yet; they live in the author's original `notebooks/` folder.

---

## Data and licence

The images and annotations come from **JHU-CROWD++** (Sindagi, Yasarla and Patel, IEEE TPAMI 2020); they are **not** included here — see [data/README.md](data/README.md) for how to obtain them under the dataset's own terms. This repository contains only code, prompts, model outputs, derived labels and write-ups. No licence has been chosen for the repository yet.
