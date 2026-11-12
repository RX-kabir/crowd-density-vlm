# Gemma 3 (4B) — Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image per prediction, no YOLO count). Experiment B (adding the YOLO count) is not yet run.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 264.87 |
| RMSE | 950.48 |
| MAPE | 104.21% |
| n (valid) | 1600 / 1600 — zero parse failures |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 69.00% |
| Precision | 76.27% |
| Recall | 69.00% |
| F1-score | 67.15% |

---

## 2. Response Reliability

**Every single one of the 1600 responses parsed cleanly** — no degenerate placeholders, no truncated output, no unparseable responses of any kind. This is a clear reliability improvement over the smaller model tested earlier in this project, which had a small but real rate of degenerate outputs under the same prompting setup.

---

## 3. No Support-Example Echoing

**0 of 1600 predictions (0.0%) exactly match any of the 5 support-example counts** shown in the prompt. This is a meaningful behavioral difference from the smaller model tested earlier, whose Experiment A was dominated by copying a support example's count rather than estimating from the image. Gemma is not falling back to that shortcut here — whatever errors it makes, they are not simple copying.

A very small number of predictions (2 of 1600) were round multiples of 1000 (12,000 and 1,000) — too few to characterize as a systematic pattern, unlike the more frequent round-number fallback seen elsewhere in this project.

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 29.0 | 138.5 | −2.3 |
| Medium (1) | 315 | 69.8 | 190.2 | −18.4 |
| High (2) | 1063 | 371.9 | 1159.8 | −79.4 |

*(bias = mean signed error, predicted − ground truth; negative = undercounts.)*

Error grows with density, as usual, but the bias is consistently mild and undercounting-leaning across all three strata — a notably more contained bias pattern than the large systematic over/undercounting seen in smaller models under the same setup, especially given Experiment A has no YOLO input to anchor to.

---

## 5. Correlation With Ground Truth — Two Numbers Tell Different Parts of the Story

- **Pearson correlation: r = 0.225**
- **Spearman rank correlation: ρ = 0.777**

The large gap between these is itself the finding. Spearman (rank-based, robust to outliers) shows Gemma is actually quite good at *ordering* images from sparse to dense — a rank correlation of 0.78 is a substantial, genuine signal. Pearson (sensitive to absolute magnitude) is dragged down to 0.225 by a small number of catastrophic outliers described below. Reporting only one of these numbers would misrepresent the model: Gemma is not "barely better than random" (what Pearson alone might suggest) or "highly accurate" (what Spearman alone might suggest) — it has a real grasp of relative crowd size undermined by rare, extreme failures.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 3411 | 105 | 21,482 | 21,377 |
| 2565 | 354 | 12,000 | 11,646 |
| 814 | 8,994 | 125 | 8,869 |
| 212 | 9,059 | 687 | 8,372 |
| 1259 | 4,192 | 12,500 | 8,308 |
| 3178 | 7,560 | 850 | 6,710 |

Two distinct failure types are visible here:
- **Extreme overcounts on lower/moderate-true-count images** (3411, 2565, 1259) — including the single worst case in the dataset, a 21,482 prediction on an image with only 105 people.
- **Severe undercounts on the very densest images** (814, 212, 3178 — all true counts near or above 7,500) — consistent with the general difficulty of estimating extremely dense, heavily-occluded crowds without any external anchor.

A small number of these extreme cases account for a disproportionate share of the total MAE, consistent with the Pearson/Spearman gap noted above.

---

## 7. Interpretation

Experiment A results position Gemma 3 (4B) as meaningfully more reliable at the response level than the smaller model tested earlier — perfect output-format compliance and no support-example copying — while still facing the same fundamental challenge of extreme-density crowd estimation without auxiliary information. Its errors are better characterized as a strong general sense of relative crowd size (high Spearman correlation) undermined by rare but severe outlier failures, rather than a broadly poor or copying-based estimator.

---

## 8. Status

Experiment B (adding the YOLO count) has not yet been run for Gemma. Once complete, the full three-way comparison (Qwen vs. LLaVA vs. Gemma, plus the YOLO baseline) can proceed.
