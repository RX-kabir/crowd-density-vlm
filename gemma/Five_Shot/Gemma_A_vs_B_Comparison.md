# Gemma 3 (4B) — Experiment A vs. Experiment B: Findings & Comparison

**Status:** Both experiments complete on the full 1600-image JHU-CROWD++ test set. Experiment B uses the identical prompt as Experiment A, with one addition — a two-line statement giving the YOLO-predicted count for the test image.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 264.87 | **240.83** |
| RMSE | 950.48 | **881.38** |
| MAPE | 104.21% | **89.76%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **69.00%** | 66.44% |
| Precision | **76.27%** | 71.79% |
| Recall | **69.00%** | 66.44% |
| F1-score | **67.15%** | 62.25% |

---

## 2. Density-Stratified Counting Error

| Density | Exp. A — MAE / Bias | Exp. B — MAE / Bias |
|---|---|---|
| Low (0) | 29.0 / −2.3 | 35.5 / −1.4 |
| Medium (1) | 69.8 / −18.4 | 73.2 / −41.4 |
| High (2) | 371.9 / −79.4 | **333.4 / −233.9** |

*(bias = mean signed error, predicted − ground truth; negative = undercounts.)*

The improvement from A to B is not uniform — it is concentrated almost entirely in the High-density stratum, where MAE drops from 371.9 to 333.4. Low and Medium-density accuracy both get slightly *worse* with the YOLO count added (Low: 29.0 → 35.5; Medium: 69.8 → 73.2).

---

## 3. Statistical Significance

Paired comparison of absolute error on all 1600 images: Wilcoxon signed-rank W = 445,928.5, **p = 0.0096**; paired t-test t = 2.35, **p = 0.0187**. The improvement from A to B is statistically significant, but the effect is far more marginal than similar comparisons elsewhere in this project — a difference of degree, not the dramatic, highly significant shifts seen with substantially different prompt conditions in other models tested.

---

## 4. Source of the Predicted Count in Experiment B

| Source | % of predictions |
|---|---|
| Echoes the YOLO count exactly | 1.1% |
| Echoes a support-example count exactly | 0.2% |
| Independent answer (matches neither) | **98.8%** |

This is the central finding of this comparison. Unlike a pattern of heavy reliance on an external anchor, Gemma's Experiment B predictions are overwhelmingly its own independent answers — only 17 of 1600 images received an exact copy of the YOLO number, and only 3 exactly matched a support example. The YOLO count appears to function as genuine auxiliary *information* that shifts Gemma's own estimate, rather than a value it defers to wholesale.

This directly explains the pattern in Section 2: the benefit shows up specifically where auxiliary detection information is most likely to be genuinely useful (severely occluded, very dense scenes), while Gemma's own independent judgment — already reasonably good in Experiment A — is mildly disrupted rather than helped on sparser scenes where it didn't need the assistance.

---

## 5. A Recurring Cross-Condition Anomaly

Test image 3411 (true count 105) received an identical, extreme prediction of **21,482** in both Experiment A and Experiment B — despite Experiment B being given an accurate YOLO count (110) for that same image, and despite the "echoes neither" analysis above confirming Gemma does not typically ignore its own judgment. This specific failure appears to be a fixed property of this particular image rather than a property of the experimental condition — worth flagging explicitly when the final cross-model comparison is assembled, as this exact value has now recurred across multiple experimental conditions in this project.

---

## 6. Worst-Case Examples (Experiment B)

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 3411 | 105 | 21,482 | 110 | 21,377 |
| 814 | 8,994 | 185 | 6 | 8,809 |
| 212 | 9,059 | 850 | 1 | 8,209 |
| 3178 | 7,560 | 650 | 9 | 6,910 |
| 4056 | 6,660 | 500 | 10 | 6,160 |

Aside from the 3411 anomaly, the remaining largest errors are all severe undercounts on extremely dense scenes (6,000–9,000 true count) where YOLO's own count was also drastically wrong (single digits in most cases). Notably, Gemma's predictions in these cases are consistently *higher* than the YOLO count it was given — evidence it is partially, but not fully, correcting for an obviously implausible detection result rather than accepting it outright.

---

## 7. Interpretation

Gemma 3 (4B) shows a qualitatively different relationship to the YOLO auxiliary input than other models tested in this project. Rather than a large shift toward copying an external anchor, Gemma's behavior changes only marginally between conditions, and the aggregate improvement is both statistically modest and concentrated specifically in the scenario (severe occlusion) where auxiliary detection input is genuinely informative. This is consistent with Gemma using the YOLO count as one input among several to its own reasoning, rather than as a replacement for it — at some cost to accuracy in the (majority) cases where its own unaided judgment was already reasonably reliable.

---

## 8. Status

Gemma 3 (4B) Experiments A and B are both complete. All three models (Qwen2.5-VL-3B, LLaVA-Interleave-0.5B, Gemma 3 4B) now have complete A/B results. The final three-way cross-model comparison, including the YOLO baseline, can now be assembled.
