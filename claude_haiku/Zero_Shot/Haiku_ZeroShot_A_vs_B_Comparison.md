# Claude Haiku 5.5 — Zero-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both zero-shot experiments complete on the full 1600-image JHU-CROWD++ test set. Neither uses support examples; Experiment B differs from A only by the extra two-line statement giving the YOLO-predicted count (identical wording to the other models' zero-shot B prompts). `claude-haiku-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, images resized to 512 px. Sampling parameters cannot be set on this model, so each condition is a single non-deterministic run. Per-experiment detail: `Haiku_ZeroShot_A_Findings.md` and `Haiku_ZeroShot_B_Findings.md`.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 482.64 | **237.11** |
| RMSE | 3396.90 | **1384.49** |
| MAPE | 69.81% | **43.01%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **71.62%** | 70.31% |
| Precision | **71.33%** | 70.04% |
| Recall | **71.62%** | 70.31% |
| F1-score | **67.09%** | 65.97% |

**Correlation with ground truth**

| | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.580 | 0.899 |
| Experiment B | 0.590 | 0.899 |

The YOLO count halves the counting error (MAE −50.9%, RMSE −59.2%, MAPE −38.4%) but leaves the ranking of scenes unchanged and **slightly lowers density accuracy (−1.3 points)**. For GPT-6.1 Terra the same comparison was −32.5% MAE and +1.1 points of density accuracy.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): B beats it on MAE (barely) and MAPE but not on RMSE; A was worse on all three. In a paired comparison of absolute error, B is closer to the truth than YOLO on 1090 images (YOLO: 273; ties: 237), A on 960 (YOLO: 586).

**Effect of the YOLO count in zero-shot, all models (A → B)**

| Model | MAE (A → B) | Density accuracy (A → B) |
|---|---|---|
| Qwen2.5-VL-3B | 725.92 → 262.36 | 66.8% → 65.8% |
| LLaVA-Interleave-0.5B | 380.67 (617 valid) → 233.86 | 12.7% → 14.6% |
| Gemma 3 (4B) | 332.24 → 234.54 | 64.7% → 64.7% |
| GPT-6.1 Terra | 198.45 → 133.87 | 75.2% → 76.3% |
| **Claude Haiku 5.5** | 482.64 → **237.11** | 71.6% → **70.3%** |

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 461,874, p = 4.1×10⁻⁵; paired t-test t = −3.45, p = 5.8×10⁻⁴.** B has the lower error on 761 images, A on 691, with 148 ties. Both tests are significant, but the margin on the typical image is slim (a 52% to 48% split among untied images): most of the aggregate improvement comes from the large errors, not from a broad shift. The median absolute error moves only from 32.0 to 28.0 and the share within ±10% of the truth is unchanged (19.1% → 19.2%).

Density change (accuracy 71.62% → 70.31%): 120 density predictions changed, **37 from wrong to right and 58 from right to wrong** — exact McNemar p = 0.040. The decline is only marginally significant, and within the model's own sampling noise (not measured) it should not be over-read.

---

## 3. Where the Change Comes From

**By ground-truth count**

| True count | n | MAE — A | MAE — B | Mean bias — A | Mean bias — B | YOLO's own bias |
|---|---|---|---|---|---|---|
| 0–10 | 58 | 1.7 | **1.4** | +1.2 | +0.9 | −1.5 |
| 11–50 | 378 | 12.3 | **8.3** | +4.6 | −3.9 | −11.4 |
| 51–100 | 301 | 40.9 | **28.5** | +22.5 | −1.7 | −33.2 |
| 101–500 | 625 | 166.5 | **102.2** | +97.0 | −13.8 | −122.3 |
| 501–1,000 | 126 | 1,047.3 | **562.1** | +745.2 | +33.9 | −486.9 |
| 1,001+ | 112 | 4,635.4 | **2,079.3** | +3,811.3 | +413.9 | −2,091.1 |

Error falls in every band. The systematic, size-growing over-count of Experiment A (+3,811 above 1,000 people) is replaced by a bias close to zero up to 1,000 people and a +414 residual in the largest crowds. Mean signed error over all images changes from **+368.7 to +25.1**; over-counts fall from 796 to 419 and under-counts rise from 749 to 1115 (exact: 55 → 66). Predictions above 10,000 fall from 15 to 5 and those of 5,000 or more from 31 to 12.

**By density class** (MAE / RMSE / mean bias)

| Density | n | Exp. A | Exp. B |
|---|---|---|---|
| Low (0) | 222 | 21.4 / 135.8 / −0.3 | 21.7 / 117.6 / −20.5 |
| Medium (1) | 315 | 203.9 / 2685.2 / +131.4 | 102.4 / 888.0 / +2.9 |
| High (2) | 1063 | 661.6 / 3902.2 / +516.1 | 322.0 / 1627.4 / +41.2 |

Gains are on Medium and High; on Low scenes error is unchanged and the model acquires a small negative bias (−20.5), as it follows YOLO's under-count.

**Mechanism: partial engagement with the YOLO count**

- 225 of 1600 B predictions (14.1%) exactly match the YOLO count and 93.9% are at or above it; the typical answer is 1.37× the YOLO count. The model treats the number as a floor to be revised upward.
- B's answer is closer to the YOLO count than A's in 84.4% of images; 1470 of the 1600 count predictions (92%) differ from A's.
- **When the YOLO count is at least 75% of the true count (404 images):** echo rate 31.7%, MAE falls from 50.1 (A) to 19.0 (B); YOLO itself has 12.4.
- **When it is below 25% of the true count (402 images):** echo rate 4.5%, MAE falls from 1540.5 to 717.1, about YOLO's own 728.7.
- **The 300 cap:** the YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300). On those images B has an MAE of 620.2 against 1203.0 for A and 803.0 for YOLO; B answers above 300 in 95.6% of them. They carry 22.1% of B's total absolute error. This is consistent with a detection cap in the YOLO inference script (not verified).
- **Stock numbers:** the A default 180 (74 times) loses weight in B; multiples of 100 fall from 9.4% to 6.2% of predictions.

---

## 4. Density: the YOLO Count Does Not Help

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | **18.0%** | 15.8% |
| Medium | 23.2% | **23.8%** |
| High | **97.2%** | 95.5% |

Predicted-class shares: A — Low 2.6%, Medium 15.2%, High 82.1%; B — 2.4%, 16.5%, 81.1% (truth: 13.9% / 19.7% / 66.4%). The confusion matrices are nearly identical: Medium images called High go from 241 to 237 and Low called Medium stay at 142, while High images called Medium rise from 29 to 47. A count says nothing about where the dataset draws the class boundaries, so the model's heavy "High" bias is untouched; the slight decline is a few extra High → Medium errors. Unlike Claude's 5-shot B, where the number visibly shifted the label distribution (High recall 92.4% → 81.3%), the effect here is small.

---

## 5. Worst-Case Examples

| test_filename | true | YOLO | A prediction | B prediction |
|---|---|---|---|---|
| 4056 | 6,660 | 10 | 45,000 | **45,000** |
| 212 | 9,059 | 1 | 45,000 | 30,000 |
| 3281 | 2,397 | 5 | 50,000 | 18,000 |
| 4159 | 6,210 | 55 | 21,456 | 21,456 |
| 2203 | 4,622 | 201 | **87,412** | 2,500 |
| 814 | 8,994 | 6 | 1,200 | **16** |

The extreme placeholder outputs of A that came with moderate YOLO counts (2203, 1510, 2542) are removed, the largest prediction falls from 87,412 to 45,000 and the 10 worst predictions' share of the total error from 47.1% to 35.2%. The cases where YOLO is itself near zero (4056, 212, 4159) are still answered with five-digit values — and on 814 the model *adopts* the absurd count. **Image 3411** (true 105; YOLO 110) is answered 175 in A and 118 in B; the 21,482 anomaly does not occur in either.

---

## 6. Reliability, Thinking and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `end_turn` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Requests with more than a bare answer (output > 15 tokens) | 1575 (98.4%) | 1536 (96.0%) |
| Mean output tokens / request | 199 | 244 |
| Mean input tokens / request | 425 | 464 |
| Cost at Batch prices ($0.05 / $0.25 per million tokens; verify) | ≈ $0.11 | ≈ $0.13 |

Reliability is perfect in both. The model thinks on almost every request in both conditions (unlike in 5-shot, where it mostly answered directly); the YOLO line adds about 22% to output length. Thinking text is not returned and not counted separately, so this is inferred from output length.

---

## 7. Against GPT-6.1 Terra, Zero-Shot Experiment B (Paired)

Same prompt, same images: GPT's MAE is 133.87 against Claude's 237.11; GPT's absolute error is lower on 929 images, Claude's on 520 (151 ties; Wilcoxon p = 3×10⁻²⁵). On density, GPT alone is right on 123 images and Claude alone on 28 (McNemar p = 2×10⁻¹⁵). Echo rates are similar (13.4% vs 14.1%), but GPT overshoots far less when it rejects an implausible YOLO count. Claude's lowest-of-all MAPE (43.01% against GPT's 45.64%) shows that it is proportionally accurate on typical scenes.

---

## 8. Zero-Shot B vs. 5-Shot B (Claude)

| | Zero-shot B | 5-shot B |
|---|---|---|
| MAE / RMSE / MAPE | 237.11 / 1384.49 / **43.01%** | **220.92 / 1100.55** / 44.26% |
| Density accuracy | 70.31% | **71.31%** |
| Exact YOLO echo | 14.1% | 11.5% |
| Cost | ≈ $0.13 | ≈ $0.17 |

Almost equivalent. The five examples reduce MAE by 6.8% and RMSE by 20% and add one point of density accuracy, but zero-shot B has the lower error on more images (755 against 642; Wilcoxon p = 7×10⁻⁶), the lowest MAPE of the two and a 25% lower cost. Once the YOLO count is in the prompt the examples add little for this model — in contrast with Experiment A, where they helped the tail more.

---

## 9. Interpretation

For Claude Haiku 5.5 the YOLO count is a **scale correction that works on counting but not on density**. It removes most of the over-count that dominates zero-shot A (bias +369 → +25), cuts the worst errors and lifts counting from clearly worse than the YOLO baseline to about equal on MAE and better on MAPE. What it does not remove is the tail created when YOLO itself is wildly low: the model recognises an implausible number and overshoots by an order of magnitude, which keeps RMSE well above YOLO's. Counting error and density accuracy again move in opposite directions (−51% MAE, −1.3 points of accuracy); the direction agrees with Qwen and with Claude's own 5-shot behaviour, the magnitude is small, while Gemma is flat and GPT's density accuracy rises slightly. The practical contrast with GPT-6.1 Terra — same prompts, same use of the number as a floor — is calibration: GPT's revisions land close to the truth, Claude's sometimes land at 15,000–45,000.

---

## 10. Limitations

- Each condition is a single non-deterministic run; variance was not measured, so the 1.3-point density decline (McNemar p = 0.040) should be read with the model's own sampling noise in mind.
- Only effort `medium` was tested.
- The subset analyses use the ground truth (or the model's own outputs) to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- The downloaded B CSV lacked the YOLO column; the repository copy has it added from `yolo/yolo_predictions.csv` (the baseline reproduces exactly).
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 11. Status

Zero-shot experiments A and B and 5-shot experiments A and B are complete for Claude Haiku 5.5. The zero-shot density-definition experiments have not yet been run for this model.
