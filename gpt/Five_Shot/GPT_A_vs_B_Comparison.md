# GPT-6.1 Terra — 5-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both 5-shot experiments complete on the full 1600-image JHU-CROWD++ test set. Both use the same five labelled support examples per test image; Experiment B differs from A only by the extra line giving the YOLO-predicted count (identical wording to the Qwen, LLaVA and Gemma 5-shot B prompts). `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, images resized to 512 px, run through the Batch API. `temperature` is not settable in reasoning mode, so each condition is a single non-deterministic run. Per-experiment detail: `GPT_ExperimentA_Findings.md` and `GPT_ExperimentB_Findings.md`.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 140.21 | **138.11** |
| RMSE | 599.80 | **494.14** |
| MAPE | 50.17% | **29.97%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | 77.81% | 77.81% |
| Precision | 77.24% | 77.67% |
| Recall | 77.81% | 77.81% |
| F1-score | 77.25% | 77.52% |

**Correlation with ground truth**

| | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | **0.774** | **0.956** |
| Experiment B | 0.753 | 0.936 |

The YOLO count barely changes mean absolute error (−1.5%), cuts RMSE by 17.6% and MAPE by 40%, leaves density accuracy unchanged to the digit, and slightly lowers both correlations. This is a much smaller effect than in zero-shot, where the YOLO count cut MAE by 32.5% (198.45 → 133.87).

**All four GPT conditions so far**

| Condition | MAE | RMSE | MAPE | Density acc. | Density F1 |
|---|---|---|---|---|---|
| Zero-shot A | 198.45 | 773.75 | 54.86% | 75.19% | 71.00% |
| Zero-shot B | **133.87** | **490.77** | 45.64% | 76.25% | 72.77% |
| 5-shot A | 140.21 | 599.80 | 50.17% | **77.81%** | 77.25% |
| 5-shot B | 138.11 | 494.14 | **29.97%** | **77.81%** | **77.52%** |

Zero-shot B has the lowest MAE and RMSE (by a small margin over 5-shot B); 5-shot B has the lowest MAPE by a wide margin and, together with 5-shot A, the best density scores. With the YOLO count already in the prompt, five labelled examples add little to counting error but sharply improve MAPE and density labelling.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): Experiment B beats it on all three metrics. Experiment A also beats it on all three, although only narrowly on MAPE (50.17%); this is a change from zero-shot A, which beat it on MAE only. In a paired comparison of absolute error, B is closer to the truth than YOLO on 1123 images (YOLO: 185; ties: 292) and A is closer on 1089 (YOLO: 451).

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 504,612.5, p = 0.046; paired t-test t = −0.24, p = 0.81.** B has the lower error on 794 images, A on 671, with 135 ties. The MAE improvement is therefore **marginal and not robust**: the rank-based test is borderline-significant and the mean-based test shows nothing. Alongside Gemma's non-significant zero-shot Experiment B, this is the weakest MAE effect of the YOLO count documented in this project (GPT zero-shot, by contrast: Wilcoxon p = 5.0×10⁻²⁸).

Density change (accuracy 77.81% in both): 75 density predictions changed between conditions, **33 from wrong to right and 33 from right to wrong** — an exact tie; McNemar p = 1.0.

The RMSE and MAPE changes are descriptive: they were not tested separately. Both are driven by specific subsets of images (Section 3), not by a broad shift.

---

## 3. Where the Change Comes From

**By ground-truth count: the gain is on sparse scenes, the loss on dense ones**

| True count | n | MAE — A | MAE — B | Mean bias — A | Mean bias — B | YOLO's own bias |
|---|---|---|---|---|---|---|
| 0–10 | 58 | 20.1 | **1.5** | +19.8 | +1.0 | −1.5 |
| 11–50 | 378 | 10.8 | **8.2** | +7.9 | +3.3 | −11.4 |
| 51–100 | 301 | 30.3 | **21.9** | +25.2 | +8.4 | −33.2 |
| 101–500 | 625 | 77.6 | **66.2** | +43.8 | −15.3 | −122.3 |
| 501–1,000 | 126 | **275.6** | 323.5 | +107.6 | −88.1 | −486.9 |
| 1,001+ | 112 | **1,131.4** | 1,152.3 | +269.8 | −519.8 | −2,091.1 |

On scenes of up to 500 people the YOLO count tightens the estimate (the YOLO count is accurate there, and the five examples alone leave a small positive bias). Above 500 people, B is slightly *worse* than A: the +270 over-count of A on the densest scenes is replaced by a −520 under-count, pulled towards YOLO's own severe under-count (−2,091 on those scenes). Because most of the 1600 images are sparse or moderate, the MAPE (which weights errors relative to the true count) falls sharply; the MAE (dominated by the densest scenes) barely moves; and the RMSE falls because the A over-shoots on dense images (up to 18,472 for image 2203) are removed.

**By density class** (MAE / RMSE / mean bias)

| Density | n | Exp. A | Exp. B |
|---|---|---|---|
| Low (0) | 222 | 18.8 / 147.0 / −12.6 | 21.7 / 165.7 / −17.9 |
| Medium (1) | 315 | 40.4 / 99.7 / −2.6 | 43.7 / 116.1 / −27.0 |
| High (2) | 1063 | 195.1 / 730.8 / +81.4 | 190.4 / 598.2 / −58.8 |

Only the High stratum improves (RMSE 730.8 → 598.2); Low and Medium get marginally worse in MAE and RMSE, with a more negative bias — a pull toward YOLO's under-counting. The mean signed error over all images flips from **+51.8 (A) to −46.9 (B)**: over-counts fall from 1010 to 632 and under-counts rise from 510 to 894 (exact: 80 → 74). The median absolute error falls from 28 to 21; the share of predictions within ±10% of the truth is essentially unchanged (27.2% → 27.6%).

**Mechanism: partial engagement with the YOLO count**

- 283 of 1600 B predictions (17.7%) exactly match the YOLO count; 99.7% are at or above it, and the typical answer is 1.76× the YOLO count. The model uses the YOLO number as a floor to be revised upward.
- B's answer is closer to the YOLO count than A's own answer in 84.9% of images, and 92.6% of count predictions differ from A's.
- **When the YOLO count is at least 75% of the true count (404 images):** echo rate 45.3%, MAE falls from 25.9 (A) to 15.4 (B); YOLO itself has 12.4.
- **When the YOLO count is below 25% of the true count (402 images):** echo rate 3.5%, but MAE is essentially unchanged — 405.1 (A) vs 407.6 (B), against 728.7 for YOLO. In zero-shot the corresponding figures were 590 → 401; with five labelled examples the model already estimates those scenes as well as the YOLO-informed answer does, and the YOLO number does not help further.
- **The 300 cap:** the YOLO counts in this experiment never exceed 300 (135 images at exactly 300, 99.3% of them with a true count above 300). On those images B is slightly worse than A (MAE 406.1 vs 378.5; YOLO: 803.0) and B echoes the capped value on 22.2% of them. The 135 images carry 24.8% of B's total absolute error. This is consistent with a detection cap in the YOLO inference script, which should be verified.

---

## 4. Density: No Change

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 60.4% | 59.9% |
| Medium | 44.4% | 47.9% |
| High | 91.3% | 90.4% |

Predicted-class shares: A — Low 10.4%, Medium 18.6%, High 71.0%; B — 10.5%, 19.9%, 69.6% (truth: 13.9% / 19.7% / 66.4%). Medium images called High: 150 (A) vs 138 (B); Low images called Medium: 73 vs 75. The YOLO count is a statement about scale, not about where the dataset draws the Low / Medium / High boundary; the five labelled examples already supply that, so it adds nothing here. The accuracy tie, the 33 / 33 swap and McNemar p = 1.0 all point the same way.

---

## 5. Worst-Case Examples and Image 3411

| test_filename | true | YOLO | A prediction | B prediction |
|---|---|---|---|---|
| 814 | 8,994 | 6 | 142 | **96** |
| 4159 | 6,210 | 55 | 10,542 | 12,000 |
| 1343 | 3,428 | 26 | 12,276 | 7,924 |
| 2203 | 4,622 | 201 | **18,472** | 201 |
| 3015 | 895 | 11 | 5,400 | 3,562 |

Image 814 is an under-count in both conditions (and an 18,000 over-count in zero-shot A); image 2203, A's worst error, is fixed by B, which adopts the YOLO count. For images with an absurdly low YOLO count (4159, 1343, 3015) the model rejects it in both conditions but still lands too high. **Image 3411** (true 105, YOLO 110) is answered 134 in A and 139 in B: the 21,482 anomaly seen in eight Qwen and Gemma conditions does not reproduce, as in GPT zero-shot. The largest prediction is 18,472 in A and 12,000 in B (three predictions above 10,000 in A, one in B).

---

## 6. Reliability, Reasoning and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `completed` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Incomplete / API errors | 0 / 0 | 0 / 0 |
| Mean reasoning tokens per request | 335 | **257** |
| Mean input tokens per request | 1,525 | 1,549 |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported) | ≈ $2.62 | ≈ $2.33 |

Reliability is perfect in both. The model reasons less when given the YOLO count (paired Wilcoxon on reasoning tokens p ≈ 2×10⁻⁴⁹), as in zero-shot — consistent with the count acting as a shortcut for part of the estimate — but here without a corresponding gain in MAE.

---

## 7. Interpretation

In zero-shot the YOLO count was a large help to GPT: it corrected a systematic over-estimate of crowd size. With five labelled examples that over-estimate is already mostly gone (A's bias falls from +162.5 per image in zero-shot to +51.8), so the YOLO count has little left to correct. What it adds in 5-shot is two modest things: (1) accurate counts on sparse and moderate scenes, where YOLO is reliable (MAPE 50.17% → 29.97%, MAE on 0–10 people 20.1 → 1.5), and (2) removal of the largest A over-shoots (RMSE −17.6%). It takes away accuracy in two places: on the densest scenes, where the model now leans towards YOLO's under-counting, and on the 135 images where YOLO is capped at 300. Net effect on mean absolute error: about −1.5% (not robust), on density accuracy: none.

So the benefit of an auxiliary count is **condition-dependent**: large when the model has no calibration of its own (zero-shot, −32.5% MAE), nearly absent when five labelled examples already provide it (5-shot, −1.5%). This is a different outcome from LLaVA and Qwen (whose gains were large in both prompting conditions, largely through copying the YOLO number) and similar in spirit to Gemma's marginal 5-shot gain — although GPT's reason is not low engagement with the YOLO count (17.7% exact echo, 99.7% at or above it) but that the count carries little information beyond what the examples supply.

---

## 8. Limitations

- Each condition is a single, non-deterministic run (no temperature control in reasoning mode); run-to-run variance was not measured, so small differences (such as the borderline Wilcoxon p = 0.046) should be treated cautiously.
- The subset analyses use the ground truth to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the YOLO inference script. If it is a detection cap, it affects every Experiment B in the project, not just GPT's.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning; the comparison cannot attribute differences to any single factor.
- Token prices are third-party-reported and should be checked against OpenAI's pricing page.

---

## 9. Status

**5-shot experiments A and B are complete for GPT-6.1 Terra**, and zero-shot A and B are complete too. The zero-shot density-definition experiments (A and B) have not yet been run for this model; the final cross-model comparison cannot be updated to include GPT until they are.
