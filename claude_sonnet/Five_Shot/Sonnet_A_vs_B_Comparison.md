# Claude Sonnet 5.5 — 5-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both 5-shot experiments complete on the full 1600-image JHU-CROWD++ test set. Both use the same five labelled support examples per test image; Experiment B differs from A only by the extra line giving the YOLO-predicted count (identical wording to the other models' 5-shot B prompts). `claude-sonnet-5-5`, Anthropic Messages API, adaptive thinking, effort **medium**, images resized to 512 px, Message Batches API. Sampling parameters cannot be set on this model, so each condition is a single non-deterministic run. Per-experiment detail: `Sonnet_ExperimentA_Findings.md` and `Sonnet_ExperimentB_Findings.md`.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 149.97 | **141.44** |
| RMSE | 465.97 | **458.14** |
| MAPE | **62.15%** | 65.76% |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **77.94%** | 77.44% |
| Precision | **79.93%** | 79.34% |
| Recall | **77.94%** | 77.44% |
| F1-score | **78.48%** | 78.05% |

**Correlation with ground truth**

| | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.797 | 0.932 |
| Experiment B | 0.793 | 0.941 |

The YOLO count gives Sonnet **a small counting gain (MAE −5.7%, RMSE −1.7%) and no density gain** (−0.5 points, not significant). MAPE is slightly worse (+3.6 points), because of one image (2269: true count 5, answered 1,500 in A and 2,500 in B, adding about 19 and 31 MAPE points respectively). Against the YOLO baseline (MAE 241.87, RMSE 737.65, MAPE 50.64%) both A and B are better on MAE and RMSE and worse on MAPE; in paired comparison of absolute error, B is closer to the truth than YOLO on 1249 images (YOLO: 314; ties: 37) and A on 1039 (YOLO: 510).

**Effect of the YOLO count in 5-shot, all models (A → B)**

| Model | MAE (A → B) | Density accuracy (A → B) |
|---|---|---|
| Qwen2.5-VL-3B | 404.15 → 259.16 | 67.5% → 57.9% |
| LLaVA-Interleave-0.5B | 503.34 → 321.11 | 48.0% → 37.8% |
| Gemma 3 (4B) | 264.87 → 240.83 | 69.0% → 66.4% |
| GPT-6.1 Terra | 140.21 → 138.11 | 77.8% → 77.8% |
| Claude Haiku 5.5 | 341.74 → 220.92 | 74.7% → 71.3% |
| **Claude Sonnet 5.5** | 149.97 → **141.44** | 77.9% → **77.4%** |

Sonnet behaves like GPT-6.1 Terra: a model whose five-shot answers are already good gains little from the extra number and loses no density accuracy, whereas the weaker models (Qwen, LLaVA, Haiku) gain a third to a half of their MAE and lose 3–10 points of density accuracy.

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 352,255, p = 8.7×10⁻⁹; paired t-test t = −2.00, p = 0.046.** B has the lower error on 780 images, A on 533, with 287 ties. The count improvement is significant on both tests, though the t-test only marginally (as the large errors, which dominate the mean, hardly change) while the rank test shows a clear shift on typical images: the median absolute error falls from 28.0 to 22.0 and the share of predictions within ±10% of the truth rises from 21.9% to 27.6%.

Density change (accuracy 77.94% → 77.44%): 100 density predictions changed between the two conditions, **42 from wrong to right and 50 from right to wrong** — exact McNemar p = 0.47: no detectable change.

---

## 3. Where the Change Comes From

**By ground-truth count**

| True count | n | MAE — A | MAE — B | Mean bias — A | Mean bias — B | YOLO's own bias |
|---|---|---|---|---|---|---|
| 0–10 | 58 | 28.2 | 44.7 | +27.8 | +44.5 | −1.5 |
| 11–50 | 378 | 10.8 | **7.5** | +7.0 | +2.3 | −11.4 |
| 51–100 | 301 | 35.0 | **25.7** | +19.2 | +6.0 | −33.2 |
| 101–500 | 625 | 108.1 | **85.6** | +44.2 | +1.8 | −122.3 |
| 501–1,000 | 126 | 365.5 | 369.7 | +139.8 | +10.3 | −486.9 |
| 1,001+ | 112 | 982.9 | 1,009.5 | −212.8 | −340.7 | −2,091.1 |

The improvement is in the middle bands (11–500 people), where the YOLO count removes the over-count of Experiment A (bias +44 → +2 for 101–500) — exactly the range in which YOLO's own count is reliable. It does **not** help for the largest crowds (above 500 people the MAE is unchanged and the under-count above 1,000 deepens from −213 to −341), where the capped YOLO count is far too low, and the 0–10 band is worse because of image 2269 alone (answered 1,500 in A and 2,500 in B). Mean signed error over all images changes from **+19.6 to −19.1**; over-counts fall from 834 to 603, under-counts rise from 703 to 913 (exact: 63 → 84).

**By density class** (MAE / RMSE / mean bias)

| Density | n | Exp. A | Exp. B |
|---|---|---|---|
| Low (0) | 222 | 17.1 / 83.3 / −6.2 | 16.9 / 84.4 / −9.1 |
| Medium (1) | 315 | 43.7 / 105.7 / −14.6 | 44.8 / 116.0 / −29.6 |
| High (2) | 1063 | 209.2 / 567.5 / +35.2 | 196.1 / 557.2 / −18.0 |

Only the High stratum improves (MAE −6%); Low and Medium are unchanged, and Medium acquires a slightly larger negative bias.

**Mechanism: use as a floor, not as an answer**

- Only 23 of 1600 B predictions (1.4%) exactly match the YOLO count, but 95.6% are at or above it; the typical answer is 1.69× the YOLO count. B's answer is closer to the YOLO count than A's in 70% of images; 1328 of the 1600 count predictions differ from A's.
- **When the YOLO count is at least 75% of the true count (404 images):** echo rate 5.7%, MAE falls from 29.0 (A) to 18.2 (B); YOLO itself has 12.4.
- **When it is below 25% of the true count (402 images):** echo rate 0.0%, **MAE unchanged** (392.2 in A, 394.3 in B; YOLO's own: 728.7). Sonnet's own estimate was already about twice as accurate as the detector's, and it ignores the number. (For Haiku the same subset fell from 935.3 to 656.7.)
- **The 300 cap:** the YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300). On those images B has an MAE of 412.6 against 437.5 for A and 803.0 for YOLO; B answers above 300 in 95.6% of them and never echoes 300. They carry 24.6% of B's total absolute error. Consistent with a detection cap in the YOLO inference script (not verified).
- **Stock numbers:** multiples of 10 rise from 44.9% to 51.4% and multiples of 100 from 3.9% to 6.0%; the A favourite 62 (83 times) is replaced by 45 (70 times).

---

## 4. Density: The YOLO Count Does Not Matter

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 59.0% | **60.8%** |
| Medium | **59.7%** | 58.4% |
| High | **87.3%** | 86.5% |

Predicted-class shares: A — Low 9.8%, Medium 24.9%, High 65.3%; B — 10.4%, 24.8%, 64.8% (truth: 13.9% / 19.7% / 66.4%). Medium images called High: 110 → 109; Low called Medium: 84 → 80. The count says nothing about where the dataset draws the class boundaries, and for Sonnet — unlike Haiku (High recall 92.4% → 81.3%) or Qwen and LLaVA — it does not shift the label distribution at all.

---

## 5. Worst-Case Examples

| test_filename | true | YOLO | A prediction | B prediction |
|---|---|---|---|---|
| 814 | 8,994 | 6 | 1,200 | 1,200 |
| 4304 | 839 | 0 | 4,200 | **6,200** |
| 2203 | 4,622 | 201 | 8,500 | 9,000 |
| 3178 | 7,560 | 9 | 2,450 | 4,200 |
| 212 | 9,059 | 1 | 14,500 | 12,000 |
| 2269 | 5 | 1 | 1,500 | **2,500** |

The images with absurdly low YOLO counts (814, 4304, 212, 2269) remain the worst errors in both experiments, as for the other models, and the YOLO number does not rescue them — in two cases (4304, 2269) the answer gets larger. The 10 worst predictions' share of the total absolute error is 17.6% in A and 17.9% in B; predictions above 10,000: 1 in each. **Image 3411** (true 105; YOLO 110) is answered 112 in A and 118 in B: the 21,482 anomaly occurs in neither.

---

## 6. Reliability, Thinking and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `end_turn` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Requests with more than a bare answer (output > 15 tokens) | **0** | 9 (0.6%) |
| Mean output tokens / request | 13.1 | 14.1 |
| Mean input tokens / request | 1,858 | 1,897 |
| Cost at Batch prices ($1 / $5 per million tokens; verify) | ≈ $3.08 | ≈ $3.15 |

Reliability is perfect in both. Sonnet answers directly on every A request and on 99.4% of B requests; the nine B requests with visible counting out loud are small crowds (true count 7–17, YOLO count 6–23), answered with an MAE of 1.7 — the YOLO line is the only difference that could have triggered them.

---

## 7. Against Claude Haiku 5.5 and GPT-6.1 Terra, 5-Shot Experiment B (Paired)

**Haiku:** Sonnet's MAE is 141.44 against 220.92 (RMSE 458.14 vs 1100.55); its absolute error is lower on 986 images, Haiku's on 475 (139 ties; Wilcoxon p = 5×10⁻³⁸). On density Sonnet alone is right on 200 images and Haiku alone on 102 (McNemar p = 2×10⁻⁸); identical density labels on 1269 of 1600. Haiku echoes the YOLO count in 11.5% of cases, Sonnet in 1.4%.

**GPT:** MAE 141.44 against 138.11; GPT's absolute error is lower on 767 images, Sonnet's on 727 (106 ties; Wilcoxon p = 0.024). On density the two are indistinguishable (GPT alone right on 104 images, Sonnet alone on 98; McNemar p = 0.73). GPT echoes the YOLO count more often (17.7% vs 1.4%). Sonnet has the better RMSE (458 vs 494) and correlations, GPT the much better MAPE (30.0% vs 65.8%).

---

## 8. Interpretation

For Claude Sonnet 5.5 the YOLO count is a **modest, mid-range scale correction**: it removes the moderate over-count of Experiment A on scenes of 11–500 people, leaves the model's already-better-than-YOLO estimates for large crowds untouched, and has no effect on the density labels. It is used selectively — as a floor, taken into account when it is close to the truth and ignored when it is far too low — never copied. Because the examples-only answers were already close to the truth (MAE 150, RMSE 466, density accuracy 77.9%), the net benefit (−5.7% MAE) is much smaller than for the weaker models (Haiku −35%, Qwen −36%, LLaVA −36%), and about the same as for GPT (−1.5%). Neither prompt makes Sonnet think; for density and for MAE it is statistically level with GPT-6.1 Terra.

---

## 9. Limitations

- Each condition is a single non-deterministic run; variance was not measured, so the small differences (A vs B in density; Sonnet vs GPT) should be read with the model's own sampling noise in mind — the McNemar and Wilcoxon p-values do not include it.
- Only effort `medium` was tested; thinking is practically absent at that setting.
- The subset analyses use the ground truth to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

5-shot experiments A and B are complete for Claude Sonnet 5.5. The zero-shot and zero-shot density-definition experiments have not yet been run for this model.
