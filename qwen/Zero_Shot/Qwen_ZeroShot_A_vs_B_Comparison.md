# Qwen2.5-VL-3B — Zero-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both zero-shot experiments complete on the full 1600-image JHU-CROWD++ test set. No support examples in either condition — the model sees only the test image (Experiment A) or the test image plus a YOLO count (Experiment B). This is a new pair of conditions, additional to the existing 5-shot results, not a replacement.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 725.92 | **262.36** |
| RMSE | 2469.95 | **922.89** |
| MAPE | 194.24% | **67.82%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | 66.75% | 65.81% |
| Precision | 63.42% | 58.40% |
| Recall | 66.75% | 65.81% |
| F1-score | 54.85% | 55.71% |

---

## 2. Statistical Significance of the A→B Improvement

Paired comparison of absolute error on all 1600 images: Wilcoxon signed-rank W = 262,688, **p = 9.1×10⁻⁴⁴**; paired t-test t = 8.70, **p = 8.1×10⁻¹⁸**. Mean absolute error drops from 725.92 to 262.36; median drops from 76.0 to 37.0. This is a large, highly significant improvement — **proportionally larger than the ~36% MAE reduction seen in the 5-shot condition** (this run improves by ~64%). Without any support examples to calibrate against, the model appears to lean on the YOLO count considerably more than it does when support examples are also available.

---

## 3. Central Finding: Density Classification Has Collapsed to the Majority Class in Both Conditions

A trivial baseline that always predicts "High" density (the majority class — 1063 of 1600 images) would score **66.44% accuracy**. Both experiments sit at or below this trivial floor:

| Condition | Accuracy | vs. trivial baseline (66.44%) |
|---|---|---|
| Experiment A | 66.75% | +0.31 pts — statistically indistinguishable |
| Experiment B | 65.81% | **−0.63 pts — actually below the trivial baseline** |

Per-class recall confirms this is a real collapse, not a metric artifact:

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 1.8% | 2.3% |
| Medium | 2.5% | 6.0% |
| High | 99.3% | 96.8% |

Adding the YOLO count produces a small improvement in minority-class recall (Medium in particular: 2.5% → 6.0%) but does not meaningfully fix the collapse — the model is still predicting "High" for the large majority of images regardless of condition. This strongly suggests density calibration in this setup depends specifically on seeing labelled support examples; a single auxiliary count (which speaks to scale, not to the Low/Medium/High category boundary) is not a substitute for that.

---

## 4. Density-Stratified Counting Error

| Density | Exp. A — MAE / Bias | Exp. B — MAE / Bias |
|---|---|---|
| Low (0) | 27.6 / +1.4 | 33.8 / −27.9 |
| Medium (1) | 107.8 / +8.5 | 85.6 / −57.9 |
| High (2) | 1054.9 / +867.0 | **362.5 / −209.7** |

*(bias = mean signed error, predicted − ground truth; positive = overcounts, negative = undercounts.)*

The most dramatic improvement is on High-density images (MAE 1054.9 → 362.5), where Experiment A's catastrophic overcounting hallucinations are largely reined in by the YOLO anchor. Bias flips sign at every density level — Experiment A consistently overcounts (worse on denser scenes), Experiment B consistently undercounts (worse on denser scenes) — the same pattern seen in every other Experiment A/B pair in this project, consistent with the model inheriting YOLO's own tendency to undercount heavily occluded crowds.

---

## 5. Correlation With Ground Truth

| Condition | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.563 | 0.794 |
| Experiment B | 0.294 | 0.772 |

Spearman correlation (robust to outliers) stays roughly similar between conditions, while Pearson correlation actually *drops* from A to B despite B's much lower MAE. This isn't a contradiction — MAE improved because the model's typical error shrank substantially, but a few extreme outliers still exert outsized influence on the Pearson figure. Both statistics are reported together deliberately, for the same reason noted in other experiments in this project: reporting only one would misrepresent the result in one direction or the other.

Separately, correlation between Experiment B's predictions and the YOLO count itself is only **0.067** — surprisingly low given that 46.2% of predictions are an exact copy of the YOLO number (Section 6). This means the roughly half of predictions that *don't* copy YOLO exactly diverge from it substantially, pulling the aggregate correlation down.

---

## 6. Behavioral Note: Partial Reliance on the YOLO Count

**46.2% of Experiment B's predictions exactly match the YOLO count given.** This is a real substitution effect — noticeably higher than relying on independent estimation alone — but less extreme than the original 5-shot Qwen Experiment B (81.9% exact matches). With no support examples available as an alternative anchor, the model leans on YOLO more than in the 5-shot setting, but still produces a non-YOLO answer more than half the time.

---

## 7. A Recurring Anomaly, Now Confirmed Across Six Conditions

Test image 3411 (true count 105) again produced the identical extreme prediction of **21,482** — the same exact value seen in Qwen 5-shot Experiment A, Qwen 5-shot Experiment B, Gemma Experiment A, and Gemma Experiment B. This occurred here in Experiment B despite an accurate YOLO count (110) being provided and evidently ignored. This specific failure has now been observed in **six separate experimental conditions**, spanning two model families and both 5-shot and zero-shot prompting — very strong evidence this is a fixed, reproducible property of the image itself rather than of any particular model, prompt, or auxiliary input. This is one of the strongest pieces of qualitative evidence in the project and is worth a dedicated case-study figure.

**Other worst-case examples (Experiment B):**

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 3411 | 105 | 21,482 | 110 | 21,377 |
| 814 | 8,994 | 5 | 6 | 8,989 |
| 3178 | 7,560 | 10 | 9 | 7,550 |
| 3539 | 6,757 | 500 | 300 | 6,257 |
| 4159 | 6,210 | 55 | 55 | 6,155 |

Aside from the 3411 anomaly, the remaining largest errors are severe undercounts on extremely dense scenes, closely tracking the (also severely undercounting) YOLO input — consistent with the substitution behavior noted in Section 6.

---

## 8. Interpretation

Removing support examples changes the effect of the YOLO count substantially. In the 5-shot setting, the auxiliary count provides a meaningful but more modest improvement (~36% MAE reduction), because support examples already give the model some calibration signal on their own. In the zero-shot setting, where the model otherwise has no scale reference at all, the same auxiliary count becomes far more valuable (~64% MAE reduction) — but density classification remains fundamentally broken in both zero-shot conditions, collapsing to a majority-class guess regardless of whether the YOLO count is present. This indicates the YOLO count and support examples serve different, non-interchangeable roles: the YOLO count helps primarily with numeric scale calibration, while density-category calibration appears to depend specifically on seeing labelled examples.

---

## 9. Status

Qwen zero-shot Experiments A and B are both complete. LLaVA and Gemma zero-shot experiments (A and B each) have not yet started. The VisDrone-mismatched-YOLO robustness check remains pending for all three models under the 5-shot condition.
