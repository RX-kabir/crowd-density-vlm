# GPT-6.1 Terra — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and the zero-shot system prompt (identical text to the Qwen, LLaVA and Gemma zero-shot experiments, bare density labels). This is the first closed-model condition in the project.

**Setup:** `gpt-6.1-terra` through the OpenAI Responses API, reasoning effort **medium**, images resized with `thumbnail((512, 512))` exactly as in the open-source runs, run through the Batch API. `temperature` is not sent (not allowed while reasoning is on), so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 198.45 |
| RMSE | 773.75 |
| MAPE | 54.86% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 75.19% |
| Precision | 73.50% |
| Recall | 75.19% |
| F1-score | 71.00% |
| Valid predictions | 1600 / 1600 |

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): GPT's MAE is lower, but its RMSE and MAPE are slightly *higher*. It is better than YOLO on typical error and marginally worse on extreme error — not uniformly better.

**Against the open-source zero-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 725.92 | 2469.95 | 194.24% | 66.75% | 54.85% | 0.563 | 0.794 | 1600 |
| LLaVA-Interleave-0.5B | 380.67 | 683.61 | 216.31% | 12.71% | 2.90% | 0.350 | 0.705 | 617 (38.6%) |
| Gemma 3 (4B) | 332.24 | 2687.40 | 61.82% | 64.69% | 63.17% | 0.379 | 0.854 | 1599 |
| **GPT-6.1 Terra** | **198.45** | 773.75 | **54.86%** | **75.19%** | **71.00%** | **0.869** | **0.961** | 1600 |

GPT's MAE is the lowest of any of the 12 open-source conditions in the project (previous best: ≈234 for LLaVA and Gemma zero-shot B, both of which were *given* the YOLO count). Caveat for interpreting this: GPT-6.1 Terra differs from the open models in scale, architecture, API serving **and** in running with medium-effort reasoning enabled; this experiment cannot attribute the gap to any one of those factors.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses returning status `completed` | 1600 / 1600 |
| Truncated / incomplete responses | 0 |
| API errors | 0 |
| Count parsed | 1600 / 1600 |
| Density parsed | 1600 / 1600 |
| Longest response | 24 characters |

Every response followed the required `Count: <n> / Density: <0/1/2>` format with no explanations — in sharp contrast to LLaVA's zero-shot Experiment A, where only 38.6% of responses were usable. Reliability is not a limiting factor for this model, as for Qwen and Gemma.

---

## 3. Density: Real Signal, but Still Biased Toward "High"

A trivial classifier that always predicts "High" scores **66.44%** (1063 of 1600). GPT's 75.19% (1203 / 1600 correct) is **above that baseline** (one-sided binomial test, p ≈ 1.8×10⁻¹⁴) — unlike Qwen's zero-shot Experiment A, whose accuracy was statistically indistinguishable from it.

| Density | n | Recall |
|---|---|---|
| Low | 222 | 33.3% (74 / 222) |
| Medium | 315 | 22.2% (70 / 315) |
| High | 1063 | **99.6%** (1059 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 74 | 112 | 36 |
| **True Medium** | 2 | 70 | 243 |
| **True High** | 0 | 4 | 1059 |

The model predicts "High" for **83.6%** of images (truth: 66.4%), "Medium" for 11.6% (truth: 19.7%) and "Low" for 4.8% (truth: 13.9%). The overall accuracy is therefore carried almost entirely by High recall: 243 of 315 Medium images (77%) are called High, and 112 of 222 Low images (50%) are called Medium. The errors are strongly *directional* — the model almost never calls a scene sparser than the truth (only 6 images: 2 Medium called Low and 4 High called Medium), but regularly calls it denser. This is a partial version of the majority-class pull seen in Qwen, far weaker than Qwen's (97.6% "High"), and unlike Gemma's pattern the model does *not* confuse High with Medium.

The pilot run (25 images) pointed the same way: Medium images were called High in all 6 pilot cases.

---

## 4. Counting Is Strong but Systematically Over-Estimates, and the Bias Grows With Crowd Size

**By density class**

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 11.5 | 49.0 | −4.2 |
| Medium (1) | 315 | 40.6 | 82.1 | +16.1 |
| High (2) | 1063 | 284.3 | 948.0 | **+240.7** |

*(bias = mean signed error, predicted − ground truth; positive = overcounts.)* Counting error on Low and Medium scenes is small and close to unbiased. The High stratum carries nearly all the error — and its bias (+240.7) is almost as large as its MAE, i.e. the error is mostly one-directional overcounting rather than noise.

**By ground-truth count**

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 14.6 | +14.2 |
| 11–50 | 378 | 11.1 | +7.4 |
| 51–100 | 301 | 34.2 | +28.9 |
| 101–500 | 625 | 108.3 | +92.1 |
| 501–1,000 | 126 | 411.5 | +345.6 |
| 1,001+ | 112 | 1,630.8 | +1,308.1 |

Across all images, 1131 are over-counted, 403 under-counted and 66 are exact; the median absolute error is 33, and 24.0% of predictions are within ±10% of the true count. The mean is pulled up by the densest scenes: removing the 5 worst predictions lowers MAE from 198.45 to 170.35.

---

## 5. Correlation With Ground Truth — Much Higher Than Any Other Zero-Shot A Run

- **Pearson r = 0.869**
- **Spearman ρ = 0.961**

Both are higher than every other zero-shot Experiment A result (best of the others: Spearman 0.854 for Gemma, Pearson 0.563 for Qwen), and the Spearman value exceeds the project-wide figure of 0.854 documented for Gemma. (Pearson was not compared across the B conditions here.) In the open-source models, removing support examples *raised* rank-correlation while *damaging* Pearson and raw error, because a few extreme hallucinations dominated. That trade-off is largely absent here: GPT's rank sense and its absolute scale are both good, and the log-log scatter (Figure 1) hugs the diagonal across four orders of magnitude, with a consistent upward offset at high counts rather than the horizontal "plateaus" at round values that Gemma and Qwen show.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 4159 | 6,210 | 19,847 | 13,637 |
| 814 | 8,994 | 18,000 | 9,006 |
| 1510 | 3,641 | 12,004 | 8,363 |
| 2203 | 4,622 | 12,248 | 7,626 |
| 2354 | 1,019 | 8,200 | 7,181 |
| 2580 | 990 | 7,624 | 6,634 |

**No placeholder hallucinations.** The largest prediction in the entire run is 19,847; only 8 predictions exceed 10,000; there is no 50,000 or 75,000 style "fallback" value. Open-source models produced values up to 75,000 on single images.

**Test image 3411 (true count 105) does not reproduce the anomaly.** The identical prediction 21,482 appeared in eight Qwen and Gemma conditions; GPT predicts **186** (density 2). As with LLaVA, this image does not trigger the effect — so the effect is not a property of the image alone; it depends on the model that sees it.

**The same hard images still cause overshoot — but a much smaller one.** Images that produced extreme hallucinations in other models are mostly answered accurately by GPT, and where they are not, the error is a few-fold, not a ten-fold:

| Image | True | Earlier extreme prediction | GPT |
|---|---|---|---|
| 4056 | 6,660 | Gemma 75,000 | **6,500** |
| 2542 | 4,113 | Qwen 50,000 | **4,386** |
| 3334 | 1,026 | Gemma 8,000 | **1,076** |
| 212 | 9,059 | Qwen 50,000 | **8,124** |
| 2592 | 2,069 | Gemma 12,000 | 2,800 |
| 4159 | 6,210 | Gemma 75,000 (12.1×) | 19,847 (3.2×) |
| 2203 | 4,622 | Gemma 35,000 (7.6×) | 12,248 (2.7×) |
| 2070 | 6,073 | Qwen 50,000 (8.2×) | 12,483 (2.1×) |

---

## 7. Reasoning Effort and Cost

| Quantity | Value |
|---|---|
| Mean input tokens / request | 317 |
| Mean output tokens / request | 662 (of which reasoning: 646; median 557) |
| Longest output | 2,942 tokens |
| Total input / output tokens | 507,848 / 1,058,406 |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported prices) | ≈ **$2.90** |

Almost the entire cost is reasoning tokens: the model's reasoning (646 tokens per request on average) is about twice the size of the whole input (317). Two observations (not causal claims): reasoning effort does **not** concentrate on the hardest images — reasoning length correlates *negatively* with the true count (Spearman ρ = −0.23) and with absolute error (ρ = −0.29) — and it is highest on Medium-density images (mean 802 tokens vs 554 for Low and 620 for High).

---

## 8. Interpretation

GPT-6.1 Terra is the strongest model tested so far on zero-shot counting: lowest MAE and MAPE of the zero-shot A runs, the highest rank and linear correlation among them, perfect format reliability, and no extreme hallucinations — a different regime from the open models, whose zero-shot behaviour was dominated by collapse, hallucinated placeholders, or broken formatting. Two weaknesses remain. First, a **systematic overcount** that grows with crowd size (+1,308 mean bias above 1,000 people), which is why its RMSE is slightly worse than YOLO's despite better MAE. Second, **density labelling lags counting**: with bare labels and no examples, the model has no way of knowing where the dataset draws the Low / Medium / High boundaries, so it places the boundary too low and over-predicts "High" (83.6% of predictions), recovering only 22% of Medium and 33% of Low images — even while its counts for those same images are accurate (Low MAE 11.5, Medium MAE 40.6). This makes the density-definition prompt study (zero-shot, with explicit Low/Medium/High descriptions) the natural next comparison for this model.

---

## 9. Limitations

- One run, not deterministic (no temperature control in reasoning mode); run-to-run variation was not measured.
- Compared with open models that differ in scale, architecture and decoding; reasoning-enabled inference is a further confound.
- Token prices used for the cost figure are third-party-reported and should be checked against OpenAI's pricing page.

---

## 10. Status

Zero-shot Experiment A is complete for GPT-6.1 Terra. Zero-shot Experiment B is also complete — see `GPT_ZeroShot_A_vs_B_Comparison.md`. The 5-shot experiments are also complete (see `../Five_Shot/`); the density-definition experiments have not yet been run for this model.
