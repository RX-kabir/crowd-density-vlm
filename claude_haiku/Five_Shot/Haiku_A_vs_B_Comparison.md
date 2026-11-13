# Claude Haiku 5.5 — 5-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both 5-shot experiments complete on the full 1600-image JHU-CROWD++ test set. Both use the same five labelled support examples per test image; Experiment B differs from A only by the extra line giving the YOLO-predicted count (identical wording to the other models' 5-shot B prompts). `claude-haiku-5-5`, Anthropic Messages API, adaptive thinking, effort **medium**, images resized to 512 px, Message Batches API. Sampling parameters cannot be set on this model, so each condition is a single non-deterministic run. Per-experiment detail: `Haiku_ExperimentA_Findings.md` and `Haiku_ExperimentB_Findings.md`.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 341.74 | **220.92** |
| RMSE | 2024.21 | **1100.55** |
| MAPE | 91.64% | **44.26%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **74.69%** | 71.31% |
| Precision | 75.87% | 76.33% |
| Recall | **74.69%** | 71.31% |
| F1-score | **73.41%** | 72.41% |

**Correlation with ground truth**

| | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.520 | 0.871 |
| Experiment B | 0.541 | 0.879 |

The YOLO count improves counting substantially — MAE −35.4%, RMSE −45.6%, MAPE −51.7% — and slightly raises both correlations, but it **lowers density accuracy by 3.4 points**. For GPT-6.1 Terra the same comparison was −1.5% MAE and no change in density; Claude gains much more from the extra number.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): Experiment B beats it on MAE and MAPE but not on RMSE. Experiment A was worse than the baseline on all three metrics. In a paired comparison of absolute error, B is closer to the truth than YOLO on 1130 images (YOLO: 269; ties: 201) whereas A is closer on 792 and YOLO on 768.

**Effect of the YOLO count in 5-shot, all models (A → B)**

| Model | MAE (A → B) | Density accuracy (A → B) |
|---|---|---|
| Qwen2.5-VL-3B | 404.15 → 259.16 | 67.5% → 57.9% |
| LLaVA-Interleave-0.5B | 503.34 → 321.11 | 48.0% → 37.8% |
| Gemma 3 (4B) | 264.87 → 240.83 | 69.0% → 66.4% |
| GPT-6.1 Terra | 140.21 → 138.11 | 77.8% → 77.8% |
| **Claude Haiku 5.5** | 341.74 → **220.92** | 74.7% → **71.3%** |

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 454,056, p = 8.4×10⁻¹⁴; paired t-test t = −3.11, p = 0.0019.** B has the lower error on 877 images, A on 649, with 74 ties. The counting improvement is significant on both tests, though the t-test is far less extreme than the rank test — the shift is broad across many images and the largest errors move less than the typical ones.

Density change (accuracy 74.69% → 71.31%): 271 density predictions changed between the two conditions, **99 from wrong to right and 153 from right to wrong** — exact McNemar p = 8.1×10⁻⁴. The decline is statistically significant (as always, within the limits of a non-deterministic model).

---

## 3. Where the Change Comes From

**By ground-truth count**

| True count | n | MAE — A | MAE — B | Mean bias — A | Mean bias — B | YOLO's own bias |
|---|---|---|---|---|---|---|
| 0–10 | 58 | 7.9 | **3.8** | +7.6 | +3.1 | −1.5 |
| 11–50 | 378 | 23.4 | **8.3** | +20.8 | −1.9 | −11.4 |
| 51–100 | 301 | 64.5 | **26.8** | +56.1 | −6.4 | −33.2 |
| 101–500 | 625 | 200.2 | **106.5** | +150.0 | −38.1 | −122.3 |
| 501–1,000 | 126 | 819.9 | **505.4** | +561.6 | −136.5 | −486.9 |
| 1,001+ | 112 | 2,585.7 | **1,891.2** | +1,359.4 | −551.4 | −2,091.1 |

Unlike in the GPT 5-shot comparison (where the YOLO count helped only up to about 500 people), Claude's error falls in **every** count band: the systematic, size-growing over-count of Experiment A (+1,359 above 1,000 people) is replaced by a milder under-count (−551), pulled toward YOLO's own (much larger) under-count. Mean signed error over all images changes from **+213.7 to −65.8**; over-counts fall from 1095 to 373, under-counts rise from 462 to 1159 (exact: 43 → 68); the median absolute error falls from 47.0 to 28.0 and the share of predictions within ±10% of the truth rises from 15.4% to 18.9%.

**By density class** (MAE / RMSE / mean bias)

| Density | n | Exp. A | Exp. B |
|---|---|---|---|
| Low (0) | 222 | 22.5 / 116.1 / −10.0 | 17.8 / 61.1 / −10.3 |
| Medium (1) | 315 | 69.5 / 268.4 / −1.6 | 61.9 / 188.4 / −57.8 |
| High (2) | 1063 | 489.1 / 2478.5 / +324.2 | 310.5 / 1346.0 / −79.7 |

The improvement is largest on the High stratum (MAE 489 → 311, RMSE 2,479 → 1,346); Medium scenes acquire a negative bias (−57.8) they did not have.

**Mechanism: partial engagement with the YOLO count**

- 184 of 1600 B predictions (11.5%) exactly match the YOLO count and 92.4% are at or above it; the typical answer is 1.26× the YOLO count. The model treats the number as a floor to be revised upward.
- B's answer is closer to the YOLO count than A's in 92.8% of images; 96.3% of count predictions differ from A's.
- **When the YOLO count is at least 75% of the true count (404 images):** echo rate 24.5%, MAE falls from 59.4 (A) to 18.7 (B); YOLO itself has 12.4.
- **When it is below 25% of the true count (402 images):** echo rate 5.2%, MAE falls from 935.3 to 656.7 — below YOLO's own 728.7. (For GPT the corresponding change was nil.)
- **The 300 cap:** the YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300). On those images B has an MAE of 670.8 against 1125.3 for A and 803.0 for YOLO; B answers above 300 in 84.4% of them. They carry 25.6% of B's total absolute error. This is consistent with a detection cap in the YOLO inference script (not verified), which affects every Experiment B.
- **Stock numbers:** the Experiment A default answer of 1200 (70 times) disappears in B (multiples of 100: 15.9% → 5.2%); the answer 412 persists (73 → 71 times).

---

## 4. Density: the YOLO Count Does Not Help — and Slightly Hurts

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 31.5% | **39.6%** |
| Medium | 45.4% | **60.0%** |
| High | **92.4%** | 81.3% |

Predicted-class shares: A — Low 5.1%, Medium 22.2%, High 72.7%; B — 7.1%, 31.2%, 61.7% (truth: 13.9% / 19.7% / 66.4%). Medium images called High fall from 163 to 109, and Low called Medium from 134 to 120 — but High images called Medium rise from 78 to 190. The YOLO count is a statement about scale, not about where the dataset draws the class boundaries; here it appears to push some dense scenes toward lower classes, plausibly because YOLO's capped counts make crowded scenes look less crowded. Recall on the two sparser classes improves, on the largest class it falls, and overall accuracy drops by 3.4 points.

---

## 5. Worst-Case Examples

| test_filename | true | YOLO | A prediction | B prediction |
|---|---|---|---|---|
| 212 | 9,059 | 1 | 50,000 | **45,000** |
| 3015 | 895 | 11 | 15,000 | 11,000 |
| 814 | 8,994 | 6 | 610 | 38 |
| 1510 | 3,641 | 41 | **60,000** | 41 |
| 2542 | 4,113 | 300 | 25,000 | 5,000 |
| 2203 | 4,622 | 201 | 4,000 | 487 |

Two of the placeholder-style errors of Experiment A (60,000 on image 1510 and 25,000 on 2542) are removed — the largest prediction falls from 60,000 to 45,000, and the 10 worst predictions' share of the total error from 33% to 24% — but the most extreme case (image 212, YOLO count 1) remains, and the images with absurdly low YOLO counts (3015, 814) are still wrong in either direction. **Image 3411** (true 105; YOLO 110) is answered 100 in A and 110 in B: the 21,482 anomaly does not occur.

---

## 6. Reliability, Thinking and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `end_turn` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Requests with more than a bare answer (output > 15 tokens) | 91 (5.7%) | 171 (10.7%) |
| Mean output tokens / request | 25.7 | 42.3 |
| Mean input tokens / request | 1,858 | 1,897 |
| Cost at Batch prices ($0.05 / $0.25 per million tokens; Anthropic's published rates, verify) | ≈ $0.16 | ≈ $0.17 |

Reliability is perfect in both. The model answers directly on nearly nine requests in ten in both conditions; the YOLO line roughly doubles the share of requests with visible extra output. (Thinking text is not returned, and the API does not report thinking tokens separately, so this is inferred from output length.)

---

## 7. Against GPT-6.1 Terra, 5-Shot Experiment B

Same prompt, same images (paired comparison): GPT's MAE is 138.11 against Claude's 220.92; GPT's absolute error is lower on 983 images, Claude's on 478 (139 ties; Wilcoxon p = 2×10⁻⁴⁵). On density, GPT alone is right on 211 images and Claude alone on 107 (McNemar p = 6×10⁻⁹). GPT echoes the YOLO count more often (17.7% vs 11.5%). Claude's total cost for the experiment is about 17 cents against GPT's $2.33.

---

## 8. Interpretation

For Claude Haiku 5.5 the YOLO count is a **scale correction that works**: it removes most of the over-count that dominates Experiment A, shrinks the worst errors, and lifts counting from worse-than-baseline (MAE 341.74) to better-than-baseline on MAE and MAPE (220.92, 44.26%) — a much larger benefit than GPT-6.1 Terra gets with five examples, because Claude's examples alone leave far more of the scale error uncorrected (a systematic over-count of +214 per image, against GPT's +52). The model uses the number selectively (it adopts credible counts, revises implausibly low ones upward) rather than copying it. The price is on the density side: the number carries no information about class boundaries and seems to bias the density label downward for dense scenes (High recall 92.4% → 81.3%), so accuracy falls by 3.4 points. Counting error and density accuracy therefore move in opposite directions. The direction matches that of every open-source model (Qwen, LLaVA and Gemma all improve their counting and lose density accuracy when given the YOLO count) but with a far smaller density loss than Qwen's or LLaVA's (−3.4 points against −9.6 and −10.2) and, unlike GPT-6.1 Terra's, with a clear counting gain.

---

## 9. Limitations

- Each condition is a single non-deterministic run; variance was not measured, so the 3.4-point density decline should be read with the model's own sampling noise in mind (the McNemar p-value does not include it).
- Only effort `medium` was tested; the model rarely produced visible extra output.
- The subset analyses use the ground truth to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- The repository copy of the B CSV had its YOLO column added after the run (see `Haiku_ExperimentB_Findings.md`).
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

5-shot experiments A and B are complete for Claude Haiku 5.5. The zero-shot and zero-shot density-definition experiments have not yet been run for this model.
