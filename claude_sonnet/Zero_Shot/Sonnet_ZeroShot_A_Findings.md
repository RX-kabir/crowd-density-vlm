# Claude Sonnet 5.5 — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and the zero-shot system prompt (identical text to the Qwen, LLaVA, Gemma, GPT and Claude Haiku zero-shot experiments, bare density labels).

**Setup:** `claude-sonnet-5-5` through the Anthropic Messages API (Message Batches), adaptive thinking, effort **medium** (set explicitly; the model's default is `high`), images resized to 512 px as in the other runs. Sampling parameters cannot be set on this model, so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once. The server-side refusal fallback was not used.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 252.51 |
| RMSE | 1626.03 |
| MAPE | 45.54% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 77.81% |
| Precision | 84.43% |
| Recall | 77.81% |
| F1-score | 78.22% |
| Valid predictions | 1600 / 1600 |

**Correlation with ground truth:** Pearson r = **0.685**, Spearman ρ = **0.938**.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): Sonnet beats it on **MAPE** (45.54%) and is slightly worse on MAE (252.51) and much worse on RMSE (1626.03, 2.2×). In a paired comparison of absolute error Sonnet is closer to the truth than YOLO on **1049 images**, YOLO on 500 (51 ties; Wilcoxon p = 1×10⁻³⁵). As with Claude Haiku, the aggregates are driven by a handful of extreme over-counts (Section 5).

**Against the other zero-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 725.92 | 2469.95 | 194.24% | 66.75% | 54.85% | 0.563 | 0.794 | 1600 |
| LLaVA-Interleave-0.5B | 380.67 | 683.61 | 216.31% | 12.71% | 2.90% | 0.350 | 0.705 | 617 (38.6%) |
| Gemma 3 (4B) | 332.24 | 2687.40 | 61.82% | 64.69% | 63.17% | 0.379 | 0.854 | 1599 |
| GPT-6.1 Terra | **198.45** | **773.75** | 54.86% | 75.19% | 71.00% | **0.869** | **0.961** | 1600 |
| Claude Haiku 5.5 | 482.64 | 3396.90 | 69.81% | 71.62% | 67.09% | 0.580 | 0.899 | 1600 |
| **Claude Sonnet 5.5** | 252.51 | 1626.03 | **45.54%** | **77.81%** | **78.22%** | 0.685 | 0.938 | 1600 |

Sonnet has the **best MAPE, density accuracy and density F1** of any zero-shot A run, and is second on MAE, RMSE and both correlations, behind GPT-6.1 Terra. Its RMSE is worse than GPT's (and LLaVA's, on 617 valid answers) because of six predictions above 10,000. Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture and API serving, and from GPT and Haiku in running without any visible thinking (Section 8); this experiment cannot attribute differences to any single factor.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count parsed | 1600 / 1600 |
| Density parsed | 1600 / 1600 |
| Longest response | 23 characters |

Every response is exactly `Count: <n>` followed by `Density: <d>` on the next line (all 1600 in the same layout).

---

## 3. Density: The Best Zero-Shot Medium Recall in the Project

A classifier that always predicts "High" scores **66.44%** (1063 of 1600). Sonnet's 77.81% (1245 / 1600 correct) is far above it (one-sided binomial p = 1×10⁻²³).

| Density | n | Recall |
|---|---|---|
| Low | 222 | 35.1% (78 / 222) |
| Medium | 315 | **78.1%** (246 / 315) |
| High | 1063 | 86.6% (921 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 78 | 142 | 2 |
| **True Medium** | 1 | 246 | 68 |
| **True High** | 1 | 141 | 921 |

Predicted shares: Low 5.0%, Medium 33.1%, High 61.9% (truth: 13.9% / 19.7% / 66.4%). Unlike GPT (83.6% "High", Medium recall 22.2%) and Haiku (82.1% "High", 23.2%), **Sonnet does not default to "High"**: with the bare labels it recovers 78% of Medium images, and it calls High only 61.9% of the images (truth 66.4%). Its characteristic error is the opposite of the other models': it over-uses Medium — 142 of 222 Low images (64%) and 141 of 1063 High images are called Medium — so its predicted Medium share (33.1%) exceeds the true one (19.7%). 212 predictions are denser than the truth and 143 sparser. Low recall (35.1%) is no better than GPT's (33.3%).

---

## 4. Counting: Accurate in the Typical Case, a Few Large Over-Counts

**By density class**

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 65.2 | 784.1 | +49.9 |
| Medium (1) | 315 | 49.8 | 217.2 | −1.6 |
| High (2) | 1063 | 351.7 | 1958.9 | **+250.1** |

**By ground-truth count**

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 1.8 | +1.6 |
| 11–50 | 378 | 8.5 | +2.9 |
| 51–100 | 301 | 28.9 | +8.5 |
| 101–500 | 625 | 116.7 | +42.3 |
| 501–1,000 | 126 | 550.9 | +364.3 |
| 1,001+ | 112 | 2,229.2 | +1,789.1 |

Counting is excellent on small and medium crowds (MAE 1.8 for 0–10 people and 8.5 for 11–50, against GPT's 14.6 and 11.1) and degrades as the crowd grows, with a one-directional over-count above 500 people (+1,789 mean above 1,000). The Low stratum's apparently large RMSE (784) is a single image: **image 2740** — labelled Low-density although its true count is 2,842 — is answered 14,500, which accounts for about 52 of the stratum's 65.2 MAE.

Over- and under-counts are balanced (758 over, 777 under, 65 exact); the median absolute error is **26** (Haiku 32, GPT 33) and 23.4% of predictions are within ±10% of the truth (Haiku 19.1%, GPT 24.0%). The mean signed error is +172.8 (Haiku +368.7; GPT +162.5).

**The tail.** Six predictions (0.4%) exceed 10,000 (Haiku: 15; GPT: 8) and account for **31.7%** of the total absolute error; the 10 worst account for 37.8%. Excluding the six (post hoc, defined by the model's own outputs, so only a description) leaves MAE 173.03 and RMSE 547.34 — better than YOLO's 241.87 / 737.65 and close to GPT's. Removing the 5 worst predictions lowers MAE from 252.51 to 176.95. MAPE is not driven by any single image (the largest single contribution is 10 points; without it MAPE would be 44.9%).

---

## 5. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 2203 | 4,622 | **45,000** | 40,378 |
| 1510 | 3,641 | 40,000 | 36,359 |
| 3178 | 7,560 | 30,000 | 22,440 |
| 2740 | 2,842 | 14,500 | 11,658 |
| 212 | 9,059 | 20,000 | 10,941 |
| 2580 | 990 | 9,500 | 8,510 |

All are over-counts, on round values (45,000; 40,000; 30,000; 20,000) of the placeholder kind seen in Haiku and the open models. The maximum prediction is 45,000 (Haiku: 87,412; open models up to 75,000; GPT's maximum 19,847). **Test image 3411 (true count 105)**, which produced the identical value 21,482 in eight Qwen and Gemma conditions, is answered **85** (Haiku 175, GPT 186); the anomaly does not reproduce.

**The same hard images, compared with earlier models:**

| Image | True | GPT | Haiku | Sonnet |
|---|---|---|---|---|
| 2203 | 4,622 | 12,248 | 87,412 | **45,000** |
| 1510 | 3,641 | 12,004 | 50,000 | 40,000 |
| 212 | 9,059 | 8,124 | 45,000 | 20,000 |
| 4056 | 6,660 | 6,500 | 45,000 | 9,500 |
| 2542 | 4,113 | 4,386 | 20,000 | 6,500 |
| 4159 | 6,210 | 19,847 | 21,456 | 9,500 |
| 3334 | 1,026 | 1,076 | 400 | 850 |
| 814 | 8,994 | 18,000 | 1,200 | 6,000 |

Sonnet is closer to the truth than Haiku on all eight, but still over-counts 2203 and 1510 by about a factor of ten; compared with GPT it is closer only on 814 and 4159.

**Stock answers.** The most frequent predictions are 230 (114 times), 120 (70), 62 (69), 150 and 85 (68 each), 38 (63) and 420 (62). 53.2% of predictions are multiples of 10 (truth: 10.4%), 7.6% multiples of 100 (truth: 0.9%; Haiku 9.4%); of the 158 predictions of 1,000 or more, 103 are multiples of 100. The "1200" default appears 29 times (true median of those images 857, MAE 453).

---

## 6. Against GPT-6.1 Terra and Claude Haiku 5.5, Zero-Shot Experiment A (Paired)

**GPT-6.1 Terra:** GPT's MAE is 198.45 against Sonnet's 252.51, but the **typical** error does not differ: Sonnet's absolute error is lower on 751 images, GPT's on 745 (104 ties; Wilcoxon p = 0.96). The difference in MAE is the tail (GPT's maximum 19,847 against Sonnet's 45,000). On density Sonnet alone is correct on 191 images and GPT alone on 149 (McNemar p = 0.026). The models' count predictions are strongly rank-correlated (ρ = 0.959), with identical density labels on 1226 of 1600 images and identical counts on only 80.

**Claude Haiku 5.5:** Sonnet's absolute error is lower on 864 images, Haiku's on 609 (127 ties; Wilcoxon p = 4×10⁻¹⁴); MAE 252.51 vs 482.64 and RMSE 1626 vs 3397. On density, Sonnet alone is right on 223 images and Haiku alone on 124 (McNemar p = 1×10⁻⁷); count rank correlation ρ = 0.947; identical density labels on 1215 of 1600.

---

## 7. Zero-Shot vs. 5-Shot (Claude Sonnet, Experiment A)

| | Zero-shot | 5-shot |
|---|---|---|
| MAE / RMSE / MAPE | 252.51 / 1626.03 / **45.54%** | **149.97 / 465.97** / 62.15% |
| Median absolute error | 26 | 28 |
| Predictions > 10,000 | 6 | 1 |
| Density accuracy / F1 | 77.81% / 78.22% | 77.94% / 78.48% |
| Recall Low / Medium / High | 35.1 / **78.1** / 86.6 | **59.0** / 59.7 / 87.3 |
| Pearson / Spearman | 0.685 / 0.938 | **0.797** / 0.932 |

The five examples reduce the aggregate counting error (MAE −41%, RMSE −71%), but only through the tail: the typical error is indistinguishable (absolute error lower on 655 images in zero-shot, on 670 in 5-shot, 275 ties; Wilcoxon p = 0.16), and zero-shot has the lower MAPE. Density accuracy is the same (124 images right only in zero-shot, 126 only in 5-shot; p = 0.95), but through different profiles: the examples raise Low recall from 35.1% to 59.0% and lower Medium recall from 78.1% to 59.7%. For Sonnet the five examples are therefore worth a lighter tail and better Low-density recall, not a better typical count or a higher density accuracy. For Haiku they helped on the tail (MAE −29%) while hurting the typical image; for GPT they helped on every measure.

---

## 8. Reasoning and Cost

| Quantity | Value |
|---|---|
| Requests with more than a bare answer (output > 15 tokens) | **0 of 1600** |
| Mean / median / max output tokens | 13.1 / 13 / 14 |
| Mean input tokens / request | 425 |
| Total input / output tokens | 679,327 / 20,958 |
| Cost at Batch prices ($1 / $5 per 1M tokens; Anthropic's published rates, to be verified) | ≈ **$0.78** |

At effort `medium` Sonnet answered **directly, without visible reasoning, on every image** (13 or 14 output tokens, the length of the answer itself). This is the opposite of Claude Haiku 5.5 in the same condition, which produced extended output on 98.4% of requests (mean 199 tokens), and of GPT-6.1 Terra's mean of 662 tokens. Sonnet's results here are therefore those of a non-reasoning model, and the extra accuracy over Haiku comes from the model, not from deliberation. Whether effort `high` would change this was not tested.

---

## 9. Interpretation

Claude Sonnet 5.5 zero-shot is the best-balanced model of the study for density — the highest accuracy and F1 of any zero-shot A run, and the only one that recovers most Medium images (78.1%) with bare labels — and a good counter on typical images (median error 26, MAPE below YOLO's). Its weakness is the one shared with Haiku and the open models: a few dense scenes receive five-figure placeholders (up to 45,000), which pushes RMSE well above YOLO's and above GPT's, though it is a fraction of Haiku's tail. Its density behaviour differs from GPT's in kind: it places the class boundaries lower and over-uses Medium, instead of defaulting to High. Compared with its own 5-shot run it loses the Low-density recall and the light tail that labelled examples provide, but keeps the same density accuracy and a better MAPE. The result sets up the next comparisons: whether the YOLO count removes the tail (zero-shot B) and whether the written density definitions move the Medium/High boundary the right way (density-definition experiments).

---

## 10. Limitations

- One run, not deterministic (no sampling control on this model); run-to-run variation was not measured, so small differences (e.g. in density accuracy against GPT or against the 5-shot run) are not meaningful.
- The tail analysis (e.g. MAE without predictions above 10,000) uses the model's own outputs to define groups and is descriptive only.
- Only effort `medium` was tested, and at that setting no visible reasoning was produced.
- Compared with open models that differ in scale, architecture and decoding.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 11. Status

Zero-shot Experiment A is complete for Claude Sonnet 5.5, as are the 5-shot experiments A and B (see `../Five_Shot/`). Zero-shot B is also complete (see `Sonnet_ZeroShot_B_Findings.md` and `Sonnet_ZeroShot_A_vs_B_Comparison.md`); the density-definition experiments have not yet been run for this model.
