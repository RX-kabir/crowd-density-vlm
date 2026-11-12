# GPT-6.1 Terra — Zero-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both zero-shot experiments complete on the full 1600-image JHU-CROWD++ test set. No support examples in either condition; Experiment B differs from A only by the extra line giving the YOLO-predicted count (identical wording to the Qwen, LLaVA and Gemma zero-shot B prompts). `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, images resized to 512 px, run through the Batch API. `temperature` is not settable in reasoning mode, so each condition is a single non-deterministic run.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 198.45 | **133.87** |
| RMSE | 773.75 | **490.77** |
| MAPE | 54.86% | **45.64%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | 75.19% | 76.25% |
| Precision | 73.50% | 75.62% |
| Recall | 75.19% | 76.25% |
| F1-score | 71.00% | 72.77% |

Counting improves substantially (MAE −32.5%, RMSE −36.6%); density changes only slightly.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same images): Experiment B beats it on **all three** counting metrics. Experiment A beat it on MAE only (its RMSE and MAPE were slightly worse). In a paired comparison of absolute error, B is closer to the truth than YOLO on 1149 images versus 222 for YOLO (229 ties; Wilcoxon p ≈ 2×10⁻¹¹⁸).

**Zero-shot Experiment B across all four models**

| Model | MAE (B) | Density acc. (B) | Exact YOLO echo (B) | A→B significance |
|---|---|---|---|---|
| Qwen2.5-VL-3B | ≈262 | 65.81% | 46.2% | p = 9.1×10⁻⁴⁴ |
| LLaVA-Interleave-0.5B | ≈234 | 14.56% | 95.8% | p = 7.7×10⁻²² |
| Gemma 3 (4B) | 234.54 | 64.69% | 1.3% | p = 0.216 (not significant) |
| **GPT-6.1 Terra** | **133.87** | **76.25%** | **13.4%** | **p = 5.0×10⁻²⁸** |

GPT's B result is the lowest MAE of any zero-shot condition so far, and it combines a **highly significant** A→B improvement with a **low** exact-echo rate — a combination none of the open-source models showed (Qwen and LLaVA: significant but with high echo; Gemma: low echo and no significant effect). See Section 3.

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 357,535.5, p = 5.0×10⁻²⁸; paired t-test t = 5.86, p = 5.7×10⁻⁹.** B has the lower error on 913 images, A on 549, with 138 ties. The counting improvement is overwhelmingly significant — though the t-test is far less extreme than the Wilcoxon, a sign that the shift is broad across many images rather than driven by a few.

Density change (accuracy 75.19% → 76.25%): 81 density predictions changed between conditions, 38 from wrong to right and 21 from right to wrong; exact McNemar test p = 0.036 — a small but nominally significant gain, not a robust one.

---

## 3. Mechanism: Partial, Selective Engagement With the YOLO Count — Not Substitution

**Only 215 of 1600 predictions (13.4%) exactly match the YOLO count**, and only 18.2% fall within 10% of it. This is far below LLaVA (95.8%) and Qwen (46.2%), above Gemma (1.3%). The substitution explanation that accounted for the A→B gains in LLaVA and Qwen therefore does not account for GPT's gain.

Yet GPT does not ignore the number either: its B prediction is **closer to the YOLO count than its own A prediction in 82.4% of images**, and 92.1% of count predictions differ from A's. How it uses the count depends on how plausible the count is (the groups below are defined with the ground truth, which the model does not see — this describes behaviour, not a rule the model is known to follow):

| Subset | n | Exact echo of YOLO | MAE: B | MAE: A | MAE: YOLO itself |
|---|---|---|---|---|---|
| YOLO is within 25% of the truth or higher (≥ 75% of true count) | 404 | **40.8%** | 15.6 | 32.8 | 12.4 |
| YOLO severely under-counts (< 25% of true count) | 402 | **1.7%** | 401.3 | 590.0 | 728.7 |

When the YOLO count is reasonable the model often adopts it (and roughly halves its own error); when the YOLO count is wildly low the model almost never copies it, yet its error still falls from 590 to 401 — better than either A or YOLO alone. Exact echoes are also concentrated on easy images: echo rate 25.2% for Low-density, 15.2% for Medium and 10.4% for High images, and echoed rows have a mean absolute error of 47.8 versus 147.2 for the rest.

**A property of the YOLO input worth knowing:** the YOLO counts supplied in this experiment never exceed 300 — 135 images have a count of exactly 300, and 99.3% of those have a true count above 300 (median 759). GPT answers above 300 on 87.4% of them (see `GPT_ZeroShot_B_Findings.md`, Section 3).

**The one clear failure of this strategy** is test image 3178 (true count 7,560; YOLO count 9): in Experiment B the model answers **14**, essentially adopting an obviously-too-small YOLO number, where in Experiment A it had overshot to 12,000. It is the single largest error in the B run (Section 7).

---

## 4. Counting Error: the Systematic Over-Count Disappears

**By density class** (MAE / mean signed bias; positive = over-count)

| Density | n | Exp. A — MAE / Bias | Exp. B — MAE / Bias |
|---|---|---|---|
| Low (0) | 222 | 11.5 / −4.2 | 15.9 / −11.2 |
| Medium (1) | 315 | 40.6 / +16.1 | 36.8 / −8.0 |
| High (2) | 1063 | 284.3 / **+240.7** | 187.3 / **+28.6** |

(RMSE for the High stratum falls from 948.0 to 598.9.) The entire improvement is in the High stratum; Low-density counting gets slightly *worse* in B (MAE 11.5 → 15.9) and its bias becomes more negative, a small pull toward YOLO's own under-counting tendency.

**By ground-truth count** — mean signed error (predicted − true)

| True count | A | B |
|---|---|---|
| 0–10 | +14.2 | +19.8 |
| 11–50 | +7.4 | +3.4 |
| 51–100 | +28.9 | +13.0 |
| 101–500 | +92.1 | +14.7 |
| 501–1,000 | +345.6 | +54.2 |
| 1,001+ | +1,308.1 | +27.0 |

Experiment A over-counts by an amount that grows steeply with crowd size; the YOLO count — which under-counts by a mean of 241.5 and by far more on dense scenes — appears to anchor Experiment B back to roughly the right scale (Figure 4). The error is also more balanced in sign: 730 over-counts, 787 under-counts and 83 exact in B, versus 1131 / 403 / 66 in A. Median absolute error falls from 33 to 20.5 and the share of predictions within ±10% of the truth rises from 24.0% to 29.0%.

---

## 5. Density: A Small Gain, the Same Weakness

A trivial classifier that always predicts "High" scores 66.44%. Both conditions are above it (A: 75.19%, B: 76.25%).

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 33.3% | 33.8% |
| Medium | 22.2% | 28.6% |
| High | 99.6% | 99.3% |

Predicted-class shares in B: Low 4.7%, Medium 13.4%, High 81.9% (truth: 13.9% / 19.7% / 66.4%; A: 4.8% / 11.6% / 83.6%). The main weakness is unchanged: **225 of 315 Medium images (71%) are still called High** (243 in A), and 117 of 222 Low images are still called Medium. The YOLO count is a statement about *scale*, not about where the dataset draws the Low / Medium / High boundary, so — as for Qwen — a single auxiliary count cannot substitute for density calibration. The small Medium gain (22.2% → 28.6%) is the only visible effect.

---

## 6. Correlation With Ground Truth

| Condition | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.869 | 0.961 |
| Experiment B | 0.805 | 0.944 |

Both correlations are slightly *lower* in B even though absolute error is much better. Counting error falls because the over-count is corrected, but pulling predictions toward the (compressed, under-counting) YOLO scale slightly weakens the model's own near-perfect rank ordering of crowd sizes. Both remain far above every open-source zero-shot correlation.

---

## 7. A Recurring Anomaly: Image 3411 Again Does Not Appear

Test image 3411 (true count 105), which produced the identical value 21,482 in eight Qwen and Gemma conditions, does **not** reproduce here. GPT predicts 186 in Experiment A and **110 in Experiment B — exactly the YOLO count (110)** — so on this image the model fully adopted an accurate auxiliary count. The 21,482 value has now been observed in 8 of 8 Qwen/Gemma conditions and in none of the LLaVA or GPT conditions.

**Worst-case examples (Experiment B)**

| test_filename | true count | B prediction | YOLO count | A prediction | abs. error (B) |
|---|---|---|---|---|---|
| 3178 | 7,560 | 14 | 9 | 12,000 | 7,546 |
| 4159 | 6,210 | 12,000 | 55 | 19,847 | 5,790 |
| 814 | 8,994 | 3,500 | 6 | 18,000 | 5,494 |
| 3697 | 2,447 | 7,500 | 77 | 8,500 | 5,053 |
| 2580 | 990 | 5,987 | 72 | 7,624 | 4,997 |
| 3015 | 895 | 5,284 | 11 | 3,865 | 4,389 |

The largest prediction in the whole B run is 12,000 (one prediction above 10,000, versus eight in A). The worst remaining errors are over-counts on scenes where the YOLO count is extremely low (all six YOLO counts above are ≤ 77, against true counts ranging from 895 to 8,994): the model rejects the implausibly low number but still lands too high, with several round-number answers (12,000, 3,500, 7,500). For image 3015 the answer is even worse than in A (5,284 vs. 3,865). The exception is image 3178, where it follows YOLO downwards.

---

## 8. Reliability, Reasoning and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `completed` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Incomplete / API errors | 0 / 0 | 0 / 0 |
| Mean reasoning tokens per request | 646 | **541** |
| Mean input tokens per request | 317 | 341 |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported) | ≈ $2.90 | ≈ $2.50 |

Reliability is perfect in both conditions. The model reasons less when given the YOLO count (paired Wilcoxon on reasoning tokens p ≈ 7×10⁻³⁴) — consistent with the count acting as a shortcut for part of the estimation — while producing more accurate answers.

---

## 9. Interpretation

GPT-6.1 Terra shows a third pattern of response to the auxiliary YOLO count, different from all three open-source models. LLaVA and Qwen gained mainly by copying the number; Gemma neither copied it nor benefited reliably. GPT gains significantly *without* copying it: only 13.4% of answers equal the YOLO count, yet counting error falls by about a third, and the improvement is concentrated in the one place where GPT's own judgement is weakest — its systematic over-estimation of large crowds, which falls from +1,308 to +27 per image above 1,000 people. The model also treats the number differently depending on how plausible it is, adopting reasonable counts (41% exact echo) and largely rejecting absurdly low ones (1.7%) — while its one clear failure (image 3178) is the case where it follows an absurdly low number anyway.

Two things are *not* improved: density classification, where the Medium → High confusion persists (71% of Medium images still called High), and rank correlation, which slips slightly. So the YOLO count helps GPT mainly as a **scale correction**, not as a source of category information.

---

## 10. Limitations

- Each condition is a single, non-deterministic run (no temperature control in reasoning mode); run-to-run variance was not measured, so small differences (such as the density gain, McNemar p = 0.036) should be treated cautiously.
- The subset analysis in Section 3 uses the ground truth to define the groups; it describes the model's behaviour and does not show that it applies an explicit plausibility rule.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning; the comparison cannot attribute differences to any single factor.
- Token prices are third-party-reported and should be checked against OpenAI's pricing page.

---

## 11. Status

**Zero-shot experiments A and B are complete for GPT-6.1 Terra.** The 5-shot experiments are also complete (see `../Five_Shot/GPT_A_vs_B_Comparison.md`); the zero-shot density-definition experiments have not yet been run for this model, and the final cross-model comparison cannot be updated to include GPT until they are.
