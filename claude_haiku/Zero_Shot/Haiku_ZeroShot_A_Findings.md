# Claude Haiku 5.5 — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and the zero-shot system prompt (identical text to the Qwen, LLaVA, Gemma and GPT zero-shot experiments, bare density labels).

**Setup:** `claude-haiku-5-5` through the Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, images resized to 512 px as in the other runs. Sampling parameters (`temperature` etc.) cannot be set on this model, so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 482.64 |
| RMSE | 3396.90 |
| MAPE | 69.81% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 71.62% |
| Precision | 71.33% |
| Recall | 71.62% |
| F1-score | 67.09% |
| Valid predictions | 1600 / 1600 |

**Correlation with ground truth:** Pearson r = **0.580**, Spearman ρ = **0.899**.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): Claude is worse on all three aggregate metrics — and RMSE by a factor of 4.6. Yet in a paired comparison of absolute error Claude is closer to the truth than YOLO on **960 images**, YOLO on 586 (54 ties; Wilcoxon p = 1×10⁻¹³). The aggregates are therefore driven by a small number of extreme over-counts (Section 6), not by typical performance.

**Against the other zero-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 725.92 | 2469.95 | 194.24% | 66.75% | 54.85% | 0.563 | 0.794 | 1600 |
| LLaVA-Interleave-0.5B | 380.67 | 683.61 | 216.31% | 12.71% | 2.90% | 0.350 | 0.705 | 617 (38.6%) |
| Gemma 3 (4B) | 332.24 | 2687.40 | 61.82% | 64.69% | 63.17% | 0.379 | 0.854 | 1599 |
| GPT-6.1 Terra | **198.45** | 773.75 | **54.86%** | **75.19%** | **71.00%** | **0.869** | **0.961** | 1600 |
| **Claude Haiku 5.5** | 482.64 | 3396.90 | 69.81% | 71.62% | 67.09% | 0.580 | 0.899 | 1600 |

Claude is second on density accuracy, F1 and both correlations, but its counting error is *worse* than Gemma's MAE and RMSE, and its RMSE is the largest of the five (LLaVA's figures cover only the 38.6% of its answers that could be parsed). The ranking depends on the metric: the model is a good ranker of scenes (Spearman 0.899, above Gemma's 0.854) with a handful of very large scale errors. As with every closed-model comparison, Claude Haiku 5.5 differs from the open models in scale, architecture, API serving and in running with adaptive thinking; the experiment cannot attribute any gap to one of those factors.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count parsed | 1600 / 1600 |
| Density parsed | 1600 / 1600 |
| Longest response | 24 characters |

Every response followed the `Count: <n> / Density: <0/1/2>` format with no explanation (1562 with a blank line between the two lines, 38 without). Reliability is not a limiting factor, as for GPT, Qwen and Gemma.

---

## 3. Density: Better Than the Majority Baseline, Carried by "High"

A classifier that always predicts "High" scores **66.44%** (1063 of 1600). Claude's 71.62% (1146 / 1600 correct) is above that baseline (one-sided binomial p = 4.8×10⁻⁶), but by less than GPT's 75.19%.

| Density | n | Recall |
|---|---|---|
| Low | 222 | 18.0% (40 / 222) |
| Medium | 315 | 23.2% (73 / 315) |
| High | 1063 | **97.2%** (1033 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 40 | 142 | 40 |
| **True Medium** | 1 | 73 | 241 |
| **True High** | 1 | 29 | 1033 |

The model predicts "High" for **82.1%** of images (truth: 66.4%), "Medium" for 15.2% (19.7%) and "Low" for only 2.6% (13.9%). Errors are strongly directional — 423 images are called denser than the truth and only 31 sparser. 241 of 315 Medium images (77%) are called High, and 142 of 222 Low images (64%) are called Medium. This is the same pattern as GPT (83.6% "High") with even lower Low recall (18.0% vs GPT's 33.3%); the model has no way of knowing where the dataset places the class boundaries when given bare labels.

---

## 4. Counting: Accurate in the Typical Case, Dominated by a Few Huge Over-Counts

**By density class**

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 21.4 | 135.8 | −0.3 |
| Medium (1) | 315 | 203.9 | 2685.2 | +131.4 |
| High (2) | 1063 | 661.6 | 3902.2 | **+516.1** |

**By ground-truth count**

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 1.7 | +1.2 |
| 11–50 | 378 | 12.3 | +4.6 |
| 51–100 | 301 | 40.9 | +22.5 |
| 101–500 | 625 | 166.5 | +97.0 |
| 501–1,000 | 126 | 1,047.3 | +745.2 |
| 1,001+ | 112 | 4,635.4 | +3,811.3 |

Counting is very good on small crowds (MAE 1.7 under 10 people against GPT's 14.6; 12.3 for 11–50 against GPT's 11.1) and degrades as the crowd grows; the bias is almost exactly the MAE above 500 people, i.e. the error there is one-directional over-counting (+3,811 mean above 1,000 people, against GPT's +1,308).

Over-counts and under-counts are nearly balanced (796 over, 749 under, 55 exact), the median absolute error is **32** (GPT: 33) and 19.1% of predictions fall within ±10% of the truth. The mean (MAE 482.64) is far above the median because of the tail: removing the 5 worst predictions lowers MAE from 482.64 to 326.77, and the 10 worst account for **47.1%** of the total absolute error.

**The tail in numbers.** 15 predictions (0.9%) exceed 10,000 (GPT: 8, maximum 19,847; Claude's maximum: 87,412). Together they contribute **55.6%** of the total absolute error. Excluding them (post hoc, defined by the model's own outputs, so only a description) leaves MAE 216.23 and RMSE 704.16 — comparable to YOLO's 241.87 / 737.65 and to GPT's figures. Thirteen predictions are more than ten times the truth. A single Medium-density image (3281, true 2,397, predicted 50,000) alone contributes about 151 of the 204 MAE of the Medium stratum and essentially all of its RMSE.

---

## 5. Correlation: Rank Sense Strong, Linear Fit Damaged

- **Pearson r = 0.580**
- **Spearman ρ = 0.899**

The rank correlation is higher than any open-source zero-shot A model (best: Gemma 0.854) and well below GPT (0.961); the linear correlation is only marginally above Qwen's 0.563 and far below GPT's 0.869, because Pearson is dominated by the extreme over-counts. The log-log scatter (Figure 1) follows the diagonal across four orders of magnitude, with a cloud of points far above it at high counts and horizontal rows at repeated values.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | abs. error | GPT zero-shot A |
|---|---|---|---|---|
| 2203 | 4,622 | 87,412 | 82,790 | 12,248 |
| 3281 | 2,397 | 50,000 | 47,603 | — |
| 1510 | 3,641 | 50,000 | 46,359 | 12,004 |
| 4056 | 6,660 | 45,000 | 38,340 | 6,500 |
| 212 | 9,059 | 45,000 | 35,941 | 8,124 |
| 2070 | 6,073 | 38,457 | 32,384 | 12,483 |

**Placeholder-style outputs do occur.** Round figures such as 50,000 (twice), 45,000 (twice), 28,000 (image 895) and 25,000 (image 1049) appear for scenes whose true counts are 1–9 thousand; the maximum, 87,412, exceeds the 75,000 maximum reported for the open-source models. GPT produced no such values. All 15 predictions above 10,000 came with fairly *short* output (110–228 tokens, against a mean of 199 and a maximum of 1,102), i.e. they look like quick estimates on dense scenes rather than the result of long counting.

**Test image 3411 (true count 105) does not reproduce the 21,482 anomaly** seen in eight Qwen and Gemma conditions: Claude predicts 175 (GPT: 186).

**The same hard images, compared with earlier extremes:**

| Image | True | Earlier extreme prediction | GPT | Claude |
|---|---|---|---|---|
| 4056 | 6,660 | Gemma 75,000 | 6,500 | 45,000 |
| 2542 | 4,113 | Qwen 50,000 | 4,386 | 20,000 |
| 3334 | 1,026 | Gemma 8,000 | 1,076 | 400 |
| 212 | 9,059 | Qwen 50,000 | 8,124 | 45,000 |
| 2592 | 2,069 | Gemma 12,000 | 2,800 | 2,500 |
| 4159 | 6,210 | Gemma 75,000 | 19,847 | 21,456 |
| 2203 | 4,622 | Gemma 35,000 | 12,248 | **87,412** |
| 2070 | 6,073 | Qwen 50,000 | 12,483 | 38,457 |

Claude is far less extreme than the open models on some of them (4056, 2542, 3334) but, unlike GPT, still overshoots by a factor of 5–19 on several — and on 2203 it is worse than any earlier run.

**Stock answers.** Claude's predictions are heavily rounded: 46.4% are multiples of 10 (truth: 10.4%), 20.7% multiples of 50 (1.4%), 9.4% multiples of 100 (0.9%); of the 154 predictions of 1,000 or more, 113 are multiples of 100. The most frequent answers are 180 (74 times; true median 160, MAE 92), 350 (59 times; true median 259, MAE 199), 120 (33) and 1200 (23; true median 649, MAE 893). In 5-shot A the stock answer was 1200 (70 times); here the model reverts to smaller "typical crowd" values.

---

## 7. Against GPT-6.1 Terra, Zero-Shot Experiment A (Paired)

Same prompt, same images: GPT's MAE is 198.45 against Claude's 482.64. GPT's absolute error is lower on **880** images, Claude's on 624 (96 ties; Wilcoxon p = 5×10⁻¹⁰). On density, GPT alone is correct on 91 images and Claude alone on 34 (exact McNemar p = 3.5×10⁻⁷). The two models are alike in structure — Spearman correlation between their predicted counts 0.928, identical density labels on 1,435 of 1,600 images (89.7%), identical counts on 79 — so the gap is a matter of scale errors and a weaker Low/Medium recall, not of a different way of working.

---

## 8. Zero-Shot vs. 5-Shot (Claude, Experiment A)

| | Zero-shot | 5-shot |
|---|---|---|
| MAE / RMSE / MAPE | 482.64 / 3396.90 / 69.81% | **341.74 / 2024.21 / 91.64%** |
| Median absolute error | **32** | 47 |
| Mean signed error | +368.7 | +213.7 |
| Over / under-counts | 796 / 749 | 1095 / 462 |
| Predictions > 10,000 | 15 | 5 |
| Density accuracy / F1 | 71.62% / 67.09% | **74.69% / 73.41%** |
| Pearson / Spearman | 0.580 / 0.899 | 0.520 / 0.871 |

Mixed. The five examples reduce the aggregate counting error (MAE −29%, RMSE −40%) and raise density accuracy by 3.1 points (exact McNemar: 130 images right only with examples, 81 only without; p = 9×10⁻⁴), but zero-shot is the better *typical* counter: its absolute error is lower on 892 images against 601 (107 ties; Wilcoxon p = 2×10⁻¹²), it has a lower median error and MAPE, a higher rank correlation, and is far more balanced between over- and under-counting. The examples seem to push the model's answers up systematically (1095 over-counts), which helps with the largest crowds but hurts the typical image — and, unlike zero-shot, curtails the extreme placeholders (5 vs 15 predictions above 10,000). For GPT-6.1 Terra the examples helped on every measure; for Claude the benefit is on the tail only.

---

## 9. Reasoning and Cost

The model chose to think on almost every request here, in sharp contrast to 5-shot A (5.7% of requests with more than a bare answer, mean 26 output tokens):

| Quantity | Value |
|---|---|
| Requests with more than a bare answer (output > 15 tokens) | 1575 of 1600 (98.4%) |
| Mean / median / max output tokens | 199 / 131 / 1,102 |
| Mean input tokens / request | 425 |
| Total input / output tokens | 679,327 / 318,520 |
| Cost at Batch prices ($0.05 / $0.25 per 1M tokens; Anthropic's published rates, to be verified) | ≈ **$0.11** |

Thinking is not reported separately by the API, so *output tokens (which include thinking) are used as a proxy*. Length is not concentrated on the hardest images: it correlates **negatively** with the true count (Spearman ρ = −0.44) and with absolute error (ρ = −0.36), and is highest on Low and Medium scenes (mean 328 and 270 tokens against 151 for High).

| Output-length quartile | n | MAE | Density accuracy | Median true count |
|---|---|---|---|---|
| ≤ 103 tokens | 411 | 152.4 | 88.1% | 171 |
| 104–131 | 393 | 882.6 | 84.2% | 193 |
| 132–240 | 398 | 864.0 | 73.6% | 129 |
| > 240 | 398 | **47.4** | 40.2% | 34 |

(Associations, not causal claims.) The longest answers are small crowds that the model appears to count one by one; counts there are accurate (MAE 47) but the density label is often wrong (40% accuracy), as sparse scenes tend to be Low/Medium, which the model labels "High" too readily. The large errors sit in the middle quartiles — short reasoning on dense scenes. For comparison, GPT-6.1 Terra's zero-shot A run cost about $2.90 and Claude's 5-shot A run about $0.16.

---

## 10. Interpretation

Claude Haiku 5.5 zero-shot is a competent but uneven counter: on typical images (median error 32, small-crowd MAE of a few units) it is as good as GPT-6.1 Terra and often closer to the truth than YOLO, but a small group of dense scenes receives wildly inflated answers (up to 87,412), so MAE, RMSE and MAPE end up *worse* than YOLO and than Gemma. Without any examples the density classification has the same weakness as GPT's — it labels 82% of scenes "High" and recovers only 18% of Low and 23% of Medium images — reflecting the lack of any definition of the class boundaries rather than an inability to estimate scale. Two things distinguish it from GPT: far less control of the extreme tail (placeholder-like values reappear) and a thinking pattern that is heavy on easy scenes and light on the dense ones where it matters. The result sets up the next comparisons: whether the YOLO count (zero-shot B) fixes the tail, and whether explicit density definitions fix the Low/Medium confusion.

---

## 11. Limitations

- One run, not deterministic (no sampling control on this model); run-to-run variation was not measured, so differences of a few points in density accuracy (e.g. against the 5-shot run) should be read with that noise in mind — the McNemar and Wilcoxon p-values do not include it.
- The tail analysis (e.g. MAE without predictions above 10,000) uses the model's own outputs to define groups and is descriptive only.
- Compared with open models that differ in scale, architecture and decoding; adaptive thinking is a further confound.
- Thinking effort is inferred from output length; token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 12. Status

Zero-shot Experiment A is complete for Claude Haiku 5.5, as are the 5-shot experiments A and B (see `../Five_Shot/`). Zero-shot B is also complete (see `Haiku_ZeroShot_B_Findings.md` and `Haiku_ZeroShot_A_vs_B_Comparison.md`); the density-definition experiments have not yet been run for this model.
