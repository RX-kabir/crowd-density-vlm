# Claude Sonnet 5.5 — 5-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image per prediction, no YOLO count). Experiment B (adding the YOLO count) is analysed in `Sonnet_ExperimentB_Findings.md` and `Sonnet_A_vs_B_Comparison.md`.

**Setup:** `claude-sonnet-5-5` through the Anthropic Messages API, adaptive thinking, effort **medium** (set explicitly; the model's own default is `high`), images resized with `thumbnail((512, 512))` exactly as in the open-source runs, run through the Message Batches API. The prompt text is identical to the Qwen, LLaVA, Gemma, GPT and Claude Haiku 5-shot Experiment A prompt. `temperature` is not sent (Claude Sonnet 5.5 rejects non-default sampling parameters), so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once. The server-side refusal fallback was not used.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 149.97 |
| RMSE | 465.97 |
| MAPE | 62.15% |
| n (valid) | 1600 / 1600 — zero parse failures |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 77.94% |
| Precision | 79.93% |
| Recall | 77.94% |
| F1-score | 78.48% |

**Correlation with ground truth:** Pearson r = **0.797**, Spearman ρ = **0.932**.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): Sonnet beats it on **MAE (−38%) and RMSE (−37%)** but not on MAPE (62.15%), which a single image inflates (Section 6).

**Against the other models' 5-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 404.15 | 1203.67 | 329.41% | 67.5% | 63.2% | 0.243 | 0.491 | 1600 |
| LLaVA-Interleave-0.5B | 503.34 | 1184.49 | 1013.03% | 48.0% | 49.5% | −0.011 | 0.043 | 1577 |
| Gemma 3 (4B) | 264.87 | 950.48 | 104.21% | 69.0% | 67.1% | 0.225 | 0.777 | 1600 |
| GPT-6.1 Terra | **140.21** | 599.80 | **50.17%** | 77.8% | 77.2% | 0.774 | **0.956** | 1600 |
| Claude Haiku 5.5 | 341.74 | 2024.21 | 91.64% | 74.7% | 73.4% | 0.520 | 0.871 | 1600 |
| **Claude Sonnet 5.5** | 149.97 | **465.97** | 62.15% | **77.9%** | **78.5%** | **0.797** | 0.932 | 1600 |

Sonnet is **best of the six on RMSE, density accuracy, density F1 and Pearson correlation**, and second on MAE, MAPE and Spearman, behind GPT-6.1 Terra. On density accuracy the difference to GPT is nil (1247 vs 1245 correct images). Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture and API serving, and from GPT in running without any visible thinking (Section 3); this experiment cannot attribute differences to any single factor.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses with stop reason `end_turn` | 1600 / 1600 |
| Truncated (`max_tokens`) / refused responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 23 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1599 with a single line break, 1 with a blank line). No explanations, no bracketed density words, no degenerate strings.

---

## 3. "Medium Effort" Meant No Thinking at All

The API reports thinking tokens inside `output_tokens`, and a bare answer (`Count: N` + `Density: D`) is 13 output tokens. **All 1600 requests used exactly 13 or 14 output tokens** (mean 13.1, total 20,940): at effort `medium` Claude Sonnet 5.5 answered **directly, without visible reasoning, on every image**. (Claude Haiku 5.5 did so on 94.3% of its 5-shot A requests; GPT-6.1 Terra reasoned for a mean of 335 tokens.) This run is therefore effectively a non-reasoning evaluation, and its good results are not a product of long deliberation. Whether higher effort levels would change the behaviour or the results is untested. Because the output length is constant, no analysis of thinking length against accuracy is possible here.

---

## 4. Repertoire of Stock Numbers: Smaller Than Haiku's

| Most frequent predictions | Times |
|---|---|
| 62 | 83 |
| 230 | 66 |
| 150 | 57 |
| 38 | 54 |
| 45 | 52 |
| 112 | 47 |
| 420 | 46 |

- **Rounding:** 44.9% of predictions are multiples of 10 (truth: 10.4%), but only **3.9% are multiples of 100** (Haiku: 15.9%; truth: 0.9%), and the Haiku default "1200 for very dense" appears 14 times (Haiku: 70; true median of those images 1,009).
- **No copying from the examples:** only 8 of 1600 predictions (0.5%) equal one of the five support counts, and the rank correlation between the prediction and the mean support count is ρ = 0.06 (truth: 0.02).
- **No placeholder explosions:** the maximum prediction is **14,500** (true count 9,059); one prediction exceeds 10,000 and seven are 5,000 or more. Haiku's maximum was 60,000, Qwen's and Gemma's reached 50,000–75,000 in zero-shot, and GPT's 5-shot A maximum was 18,472.

---

## 5. Density Classification: Best Balanced Profile of the Closed Models

Always predicting "High" scores **66.44%**; Sonnet's 77.94% (1247 / 1600) is far above it (one-sided binomial p = 4×10⁻²⁴).

| Density | n | Recall |
|---|---|---|
| Low | 222 | **59.0%** (131 / 222) |
| Medium | 315 | **59.7%** (188 / 315) |
| High | 1063 | 87.3% (928 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 131 | 84 | 7 |
| **True Medium** | 17 | 188 | 110 |
| **True High** | 8 | 127 | 928 |

Predicted shares are Low 9.8% / Medium 24.9% / High 65.3% (truth: 13.9% / 19.7% / 66.4%) — the closest match to the true distribution of any model so far. Errors are almost balanced (201 predictions denser than the truth, 152 sparser; Haiku 315 / 90). Per-class recall (Low / Medium / High) of the 5-shot A runs: Qwen 15.3 / 22.9 / 91.6, LLaVA 20.7 / 25.6 / 60.3, Gemma 6.8 / 60.3 / 84.6, GPT 60.4 / 44.4 / 91.3, Haiku 31.5 / 45.4 / 92.4, **Sonnet 59.0 / 59.7 / 87.3**. Sonnet matches GPT on Low recall and exceeds every model on Medium recall; it pays for it on High (87.3%, the lowest of the closed models), where 127 images are called Medium. Overall accuracy equals GPT's.

---

## 6. Counting Error: Small Tail, Under-Counting of the Largest Crowds

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 17.1 | 83.3 | −6.2 |
| Medium (1) | 315 | 43.7 | 105.7 | −14.6 |
| High (2) | 1063 | 209.2 | 567.5 | +35.2 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)*

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 28.2 | +27.8 |
| 11–50 | 378 | 10.8 | +7.0 |
| 51–100 | 301 | 35.0 | +19.2 |
| 101–500 | 625 | 108.1 | +44.2 |
| 501–1,000 | 126 | 365.5 | +139.8 |
| 1,001+ | 112 | 982.9 | **−212.8** |

The systematic, size-growing over-count of Haiku (+1,359 above 1,000 people) is gone: the bias is moderate up to 1,000 people and turns negative above it. Over-counts and under-counts are balanced (834 vs 703, 63 exact), the mean signed error is **+19.6** per image (Haiku: +213.7; GPT: +51.8), the median absolute error is 28.0 (Haiku: 47.0) and 21.9% of predictions are within ±10% of the truth (GPT: 27.2%). The sparsest band looks worse than Haiku's (MAE 28.2 against 7.9 for 0–10 people), but this is a **single image**: image 2269 (true count 5) is answered **1,500**, contributing about 26 of the band's 28.2 (the median absolute error in the band is 1.0, and 1.25 without the three worst). The same image alone adds 18.7 points to MAPE: without it MAPE would be 43.4%, below YOLO's 50.64% and GPT's 50.17%. The reported MAPE (62.15%) is therefore a statement about one placeholder-style outlier on a near-empty scene, not about small scenes in general.

The tail is light: **the 10 worst predictions account for 17.6% of the total absolute error** (Haiku: 33%), and removing the 5 worst lowers MAE only from 149.97 to 133.78.

**Worst cases**

| test_filename | true count | predicted | error |
|---|---|---|---|
| 814 | 8,994 | 1,200 | −7,794 |
| 212 | 9,059 | 14,500 | +5,441 |
| 3178 | 7,560 | 2,450 | −5,110 |
| 3539 | 6,757 | 2,450 | −4,307 |
| 4056 | 6,660 | 2,750 | −3,910 |
| 2203 | 4,622 | 8,500 | +3,878 |
| 4304 | 839 | 4,200 | +3,361 |
| 3968 | 4,218 | 1,150 | −3,068 |

In contrast to Haiku (almost all over-counts) the largest errors are mostly **under-counts of very large crowds** (five of the eight). **Test image 3411 (true 105)**, the source of the identical value 21,482 in eight Qwen and Gemma conditions, is answered **112**: the anomaly does not reproduce. Images that triggered extreme hallucinations elsewhere are handled well: 2542 (true 4,113) → 2,450 (Qwen 50,000; Haiku 25,000), 4056 (true 6,660) → 2,750, 1510 (true 3,641) → 5,000 (Haiku 60,000), 3334 (true 1,026) → 850.

---

## 7. Against Claude Haiku 5.5, 5-Shot Experiment A (Paired)

Same prompt, same images: Sonnet's MAE is 149.97 against Haiku's 341.74 (RMSE 465.97 vs 2024.21). Sonnet's absolute error is lower on **992 images**, Haiku's on 475 (133 ties; Wilcoxon p = 2×10⁻⁴⁶). On density Sonnet alone is right on 173 images, Haiku alone on 121 (McNemar p = 0.003). The two models' count predictions are strongly rank-correlated (ρ = 0.92) but agree exactly on only 117 images, and give the same density label on 1280 of 1600. Predictions above 10,000: 1 for Sonnet, 5 for Haiku. Both models answer (almost) without visible thinking and receive exactly the same input (1,858 tokens on average), so the gap lies in the model, not the effort setting or the prompt.

---

## 8. Against GPT-6.1 Terra, 5-Shot Experiment A (Paired)

| Metric | GPT-6.1 Terra | Claude Sonnet 5.5 |
|---|---|---|
| MAE | **140.21** | 149.97 |
| RMSE | 599.80 | **465.97** |
| MAPE | **50.17%** | 62.15% |
| Density accuracy | 77.81% | **77.94%** |
| Density F1 | 77.25% | **78.48%** |
| Pearson r / Spearman ρ | 0.774 / **0.956** | **0.797** / 0.932 |
| Mean output tokens / request | 350 (reasoning 335) | 13 |
| Mean input tokens / request | 1,525 | 1,858 |
| Actual cost at Batch prices | ≈ $2.62 | ≈ **$3.08** |

GPT's absolute error is lower on 854 images, Sonnet's on 664 (82 ties; Wilcoxon p = 5×10⁻⁸) — GPT is the better typical counter, Sonnet the one with fewer large errors. On density the two models are tied: GPT alone is right on 102 images, Sonnet alone on 104 (McNemar p = 0.94); they give identical labels on 1379 images (86%). Rank correlation of their count predictions: ρ = 0.96, with identical counts on only 68 images. Costs are similar in magnitude even though Sonnet produces no reasoning tokens: it is paid per input token, and the six images per request dominate. Cost uses Anthropic's published prices for Claude Sonnet 5.5 ($2 / $10 per million input / output tokens, 50% Batch discount; verify) on 2,972,151 input and 20,940 output tokens.

---

## 9. Interpretation

Claude Sonnet 5.5 at medium effort is a non-reasoning estimator that, given five labelled examples, performs at GPT-6.1 Terra's level: better RMSE and density F1, the same density accuracy, slightly worse MAE and MAPE and a lower rank correlation. It is a very different model from Claude Haiku 5.5 in this setting — the same prompt and the same lack of visible thinking produce less than half the MAE and under a quarter of the RMSE, with almost twice the Low-density recall (59.0% vs 31.5%) and a better Medium recall (59.7% vs 45.4%) — which indicates that the capability gap, not effort or format, drives Haiku's heavy tail. Its remaining weaknesses are an occasional placeholder-like answer on a near-empty scene (image 2269: 5 people, answered 1,500), an under-estimate of the very largest crowds, and a High-class recall (87.3%) lower than the other closed models'. At the same time it needs no reasoning budget and a single answer line, at a cost comparable to GPT's.

---

## 10. Limitations

- One run, not deterministic (no temperature control); run-to-run variation was not measured, so differences of a point or two (e.g. density accuracy against GPT) are not meaningful.
- Only effort `medium` was tested, and at that setting the model produced no visible reasoning on any request. Whether higher effort would change the results is untested.
- Compared with open models that differ in scale, architecture and decoding.
- Thinking tokens are not reported separately by the API; "no thinking" is inferred from the constant output length of 13–14 tokens.
- Prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 11. Status

5-shot Experiment A is complete for Claude Sonnet 5.5. Experiment B is also complete (see `Sonnet_ExperimentB_Findings.md` and `Sonnet_A_vs_B_Comparison.md`); the zero-shot and density-definition conditions have not yet been run for this model.
