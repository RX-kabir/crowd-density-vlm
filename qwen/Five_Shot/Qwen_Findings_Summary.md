# Crowd Density Estimation with YOLO-Assisted VLMs — Findings Summary (Qwen2.5-VL)

**Status:** Qwen2.5-VL-3B-Instruct, Experiments A and B, complete on the full 1600-image JHU-CROWD++ test set. LLaVA and Gemma (Phases 6–7 for those models) and the Phase 9 cross-model comparison are not yet started.

---

## 1. Setup

- **Dataset:** JHU-CROWD++ (2272 train / 500 val / 1600 test images).
- **Method:** Fixed 5-shot support set (same 5 labelled examples for every test image, drawn once from the training set).
- **Experiment A:** 5 support images + counts/densities + 1 test image. Model predicts count and density (Low/Medium/High) from the image alone.
- **Experiment B:** Identical prompt to Experiment A, with one addition — a two-line statement in the test-image turn giving a YOLOv8s-predicted crowd count for that image as auxiliary information.
- **Model:** Qwen2.5-VL-3B-Instruct, float16, greedy decoding (`do_sample=False`), 16 max new tokens.

---

## 2. Headline Results

| Method | MAE | RMSE | MAPE | Density Accuracy |
|---|---|---|---|---|
| YOLOv8s baseline | 241.87 | 737.65 | 50.64% | — |
| Qwen Experiment A (no YOLO count) | 404.15 | 1203.67 | 329.41% | 67.50% |
| Qwen Experiment B (with YOLO count) | 259.16 | 884.06 | 133.52% | 57.94% |

Density classification (Experiment B): Precision 60.02%, Recall 57.94%, F1-score 58.73%.

---

## 3. Density-Stratified Error

| Density class | n | YOLO MAE / bias | Exp A MAE / bias | Exp B MAE / bias |
|---|---|---|---|---|
| Low (0) | 222 | 34.5 / −34.1 | 69.6 / +26.6 | 65.7 / +11.0 |
| Medium (1) | 315 | 83.2 / −82.7 | 142.3 / +47.8 | 89.5 / −54.9 |
| High (2) | 1063 | 332.2 / −331.9 | 551.6 / +145.7 | 349.9 / −268.0 |

*(bias = mean signed error, predicted − ground truth; positive = overcounts, negative = undercounts. High-density images are 66% of the test set and dominate the aggregate MAE for every method.)*

**Statistical significance** (paired on all 1600 images, B vs. A): Wilcoxon signed-rank W = 287,459, p = 1.7×10⁻⁴⁶; paired t-test t = 6.66, p = 3.6×10⁻¹¹. Experiment B's counting error is significantly lower than Experiment A's.

---

## 4. Key Findings

**4.1 — Adding the YOLO count significantly reduces counting error but does not improve density classification.** MAE drops from 404.15 (A) to 259.16 (B), a statistically significant reduction (p < 10⁻¹⁰). Density accuracy, however, is slightly lower in B (57.94%) than A (67.50%) — since both tasks draw on the same underlying scene understanding, this suggests the YOLO count helps the model anchor a numeric estimate without improving (and possibly mildly interfering with) its broader scene judgment.

**4.2 — Error scales sharply with crowd density in every method.** High-density images (66% of the test set) dominate the aggregate MAE across YOLO, A, and B alike. Experiment A shows a strong overcounting bias that grows with density (+145.7 at High); Experiment B shows an undercounting bias that also grows with density (−268.0 at High) — the two methods err in opposite directions rather than one being a strict improvement across the board.

**4.3 — A specific hallucination case illustrates a model-intrinsic failure mode.** Test image 3411 (true count 105) received an identical, extreme predicted count of 21,482 in both Experiment A (no auxiliary input) and Experiment B — where the YOLO count supplied for that same image was 110, i.e. accurate. The model produced the same extreme error regardless of whether it had good auxiliary information, suggesting this specific failure originates in the model/image pair itself rather than in how auxiliary information was used.

**4.4 — Output-format compliance was reliable.** Across all 3,200 generations (1600 images × Experiments A and B), 0 responses used hedging or range language (e.g. "approximately", numeric ranges), and 0 exceeded a terse `Count:`/`Density:` reply — the model consistently followed the required output format even when its underlying numeric estimates were unreliable.

---

## 5. Limitations

- The `distractor` metadata field is confounded with ground-truth density (distractor-flagged images skew heavily toward low crowd counts) and should not be reported as an independent effect without controlling for density.
- `scene_type` has ~58 categories, many with only 1–2 images — too sparse for reliable per-category claims without grouping into broader buckets (e.g., large public events vs. small gatherings).
- These findings are specific to Qwen2.5-VL-3B-Instruct under this fixed 5-shot setup; whether the same pattern holds for LLaVA or Gemma is an open question for the remaining experiments.

---

## 6. Status Against Roadmap Questions (Qwen only)

1. **Can the VLM estimate crowd count accurately?** Not reliably at high density unaided — Experiment A's MAPE (329%) and outliers up to 21,482 on a 105-person image show this.
2. **Can the VLM estimate crowd density accurately?** Moderately (67.5% accuracy in A), but driven largely by the majority High-density class.
3. **Does the YOLO count improve counting?** Yes, significantly (p < 10⁻¹⁰) — MAE and RMSE both improve substantially, though MAPE remains well above the YOLO baseline alone.
4. **Does the YOLO count improve density classification?** No — accuracy is modestly lower in Experiment B than in Experiment A.
5. **Which VLM performs best?** Not yet answerable — pending LLaVA and Gemma.

---

## 7. Next Steps

- Run Experiment A and B for LLaVA (checkpoint and GPU tier still to be decided).
- Run Experiment A and B for Gemma.
- Phase 9: final cross-model comparison (YOLO baseline vs. A vs. B, across Qwen/LLaVA/Gemma).

---

*Accompanying figures (generated separately): predicted-vs-actual scatter plots, MAE-by-density-class bar chart, and density confusion matrices, for Experiment A and Experiment B.*
