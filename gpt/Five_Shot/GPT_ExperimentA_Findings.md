# GPT-6.1 Terra — 5-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image per prediction, no YOLO count). Experiment B (adding the YOLO count) is analysed in `GPT_ExperimentB_Findings.md`.

**Setup:** `gpt-6.1-terra` through the OpenAI Responses API, reasoning effort **medium**, images resized with `thumbnail((512, 512))` exactly as in the open-source runs, run through the Batch API (12 batch files). The prompt text is identical to the Qwen, LLaVA and Gemma 5-shot Experiment A prompt. `temperature` is not sent (not allowed while reasoning is on), so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 140.21 |
| RMSE | 599.80 |
| MAPE | 50.17% |
| n (valid) | 1600 / 1600 — zero parse failures |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 77.81% |
| Precision | 77.24% |
| Recall | 77.81% |
| F1-score | 77.25% |

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): GPT with five labelled examples and *no* YOLO input beats it on all three counting metrics, although the MAPE margin is small (50.17% vs 50.64%). In the zero-shot version of this experiment GPT beat YOLO on MAE only; the five examples are what bring RMSE and MAPE below the baseline.

**Against the open-source 5-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 404.15 | 1203.67 | 329.41% | 67.5% | 63.2% | 0.243 | 0.491 | 1600 |
| LLaVA-Interleave-0.5B | 503.34 | 1184.49 | 1013.03% | 48.0% | 49.5% | −0.011 | 0.043 | 1577 |
| Gemma 3 (4B) | 264.87 | 950.48 | 104.21% | 69.0% | 67.1% | 0.225 | 0.777 | 1600 |
| **GPT-6.1 Terra** | **140.21** | **599.80** | **50.17%** | **77.8%** | **77.2%** | **0.774** | **0.956** | 1600 |

(Open-source figures recomputed from the saved `*_experiment_A_evaluated.csv` files.) GPT's MAE is about half of Gemma's, the best open-source 5-shot A run, and its density accuracy is above the 69.00% that the cross-model report lists as the highest of the 12 open-source conditions. Caveat: GPT-6.1 Terra differs from the open models in scale, architecture, API serving **and** in running with medium-effort reasoning enabled; this experiment cannot attribute the gap to any one of those factors.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses returning status `completed` | 1600 / 1600 |
| Truncated / incomplete responses | 0 |
| API errors | 0 |
| Count parsed | 1600 / 1600 |
| Density parsed | 1600 / 1600 |
| Longest response | 23 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1566 with a single line break between them, 34 with a blank line — both parse correctly). No explanations, no bracketed density words, no degenerate placeholder strings, whereas LLaVA's 5-shot Experiment A produced only 1577 of 1600 valid counts (98.6%).

---

## 3. Almost No Support-Example Echoing

**25 of 1600 predictions (1.6%) exactly equal one of the five support counts shown in the prompt.** This is not zero (Gemma: 0 of 1600), but it is small and mostly consistent with coincidence on low-count scenes: the *true* count of the test image itself equals a support count in 26 images, echoed answers have a mean absolute error of only 15.2 (against 142.2 for the rest), and the typical echoed values are small numbers (15, 21, 30, 47, 67, 84, 231). A rank correlation between the prediction and the mean of the five support counts is ρ = 0.05 (the correlation between the *true* count and that mean is 0.02), so the answers do not drift towards the examples. The model estimates from the image rather than copying from its examples.

**No round-number fallback.** Only 4 predictions are exact multiples of 1000 (at or above 1000); 11.2% of predictions are multiples of 10 against 10.4% of true counts, i.e. no preference for round values. The largest prediction in the run is **18,472**; only 3 predictions exceed 10,000; there is no 50,000 or 75,000 style placeholder (Qwen reached 10,000 in 5-shot and 50,000–75,000 in zero-shot).

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 18.8 | 147.0 | −12.6 |
| Medium (1) | 315 | 40.4 | 99.7 | −2.6 |
| High (2) | 1063 | 195.1 | 730.8 | +81.4 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)*

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 20.1 | +19.8 |
| 11–50 | 378 | 10.8 | +7.9 |
| 51–100 | 301 | 30.3 | +25.2 |
| 101–500 | 625 | 77.6 | +43.8 |
| 501–1,000 | 126 | 275.6 | +107.6 |
| 1,001+ | 112 | 1,131.4 | +269.8 |

Across all images, 1010 are over-counted, 510 under-counted and 80 exact; the median absolute error is 28, and 27.2% of predictions are within ±10% of the true count. The error is concentrated in the High stratum and the densest scenes: removing the 5 worst predictions lowers MAE from 140.21 to 115.33. The overall bias is mild and positive (+51.8 per image), mostly from High-density scenes; Low and Medium scenes are close to unbiased.

---

## 5. Density Classification: A Real Gain Over the Majority Baseline, With Better Balance Than Zero-Shot

A classifier that always predicts "High" scores **66.44%** (1063 of 1600). GPT's 77.81% (1245 / 1600 correct) is clearly above it (one-sided binomial test, p ≈ 1.3×10⁻²³).

| Density | n | Recall |
|---|---|---|
| Low | 222 | 60.4% (134 / 222) |
| Medium | 315 | 44.4% (140 / 315) |
| High | 1063 | 91.3% (971 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 134 | 73 | 15 |
| **True Medium** | 25 | 140 | 150 |
| **True High** | 7 | 85 | 971 |

Predictions are distributed as Low 10.4% / Medium 18.6% / High 71.0% against a truth of 13.9% / 19.7% / 66.4% — much closer to the real class mix than GPT's own zero-shot run (4.8% / 11.6% / 83.6%). The remaining weakness is Medium: 150 of 315 Medium images (47.6%) are called High, and 85 High images are called Medium. Errors still lean denser (238 predictions denser than the truth, 117 sparser), but far less than in zero-shot.

Comparison of per-class recall (Low / Medium / High) with the open-source 5-shot A runs: Qwen 15.3 / 22.9 / 91.6, LLaVA 20.7 / 25.6 / 60.3, Gemma 6.8 / 60.3 / 84.6, **GPT 60.4 / 44.4 / 91.3**. GPT is the only model with substantial recall on Low-density scenes; Gemma recovers more of the Medium class.

---

## 6. Correlation With Ground Truth

- **Pearson r = 0.774**
- **Spearman ρ = 0.956**

Both far exceed any open-source 5-shot A run (best Pearson 0.243 for Qwen, best Spearman 0.777 for Gemma). The gap between Spearman and Pearson is the usual signature of a few large outliers (Section 7), but here it is narrow: GPT is both a good ranker and a reasonable absolute estimator, unlike Gemma (Pearson 0.225 vs Spearman 0.777).

---

## 7. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 2203 | 4,622 | 18,472 | 13,850 |
| 814 | 8,994 | **142** | 8,852 |
| 1343 | 3,428 | 12,276 | 8,848 |
| 3015 | 895 | 5,400 | 4,505 |
| 4159 | 6,210 | 10,542 | 4,332 |
| 3658 | 1,993 | 6,321 | 4,328 |

Two failure types: **over-shoots** on mid-sized crowds (2203, 1343, 3015, 4159, 3658) and a single severe **under-count** on the very densest image (814, true count 8,994, answered 142 — in the zero-shot run the same image was answered 18,000). A handful of images produce a disproportionate share of the squared error, consistent with the RMSE being four times the MAE.

**Test image 3411 (true count 105)** — which produced the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **134**; the anomaly does not reproduce (as in GPT zero-shot, where it was 186).

**The images that triggered extreme hallucinations in other models are mostly answered sensibly:**

| Image | True | Earlier extreme prediction | GPT 5-shot A |
|---|---|---|---|
| 4056 | 6,660 | Gemma 75,000 | **7,254** |
| 2542 | 4,113 | Qwen 50,000 | **5,100** |
| 3334 | 1,026 | Gemma 8,000 | **673** |
| 212 | 9,059 | Qwen 50,000 | **6,824** |
| 2592 | 2,069 | Gemma 12,000 | 2,436 |
| 4159 | 6,210 | Gemma 75,000 (12.1×) | 10,542 (1.7×) |
| 2070 | 6,073 | Qwen 50,000 (8.2×) | 8,500 (1.4×) |
| 2203 | 4,622 | Gemma 35,000 (7.6×) | 18,472 (4.0×) — the run's worst case |

---

## 8. Against GPT Zero-Shot Experiment A: What Five Labelled Examples Add

Same model, same images, same prompt apart from the support examples (paired comparison):

| Metric | Zero-shot A | **5-shot A** |
|---|---|---|
| MAE | 198.45 | **140.21** |
| RMSE | 773.75 | **599.80** |
| MAPE | 54.86% | **50.17%** |
| Density accuracy | 75.19% | **77.81%** |
| Density F1 | 71.00% | **77.25%** |
| Recall Low / Medium / High | 33.3 / 22.2 / 99.6 | **60.4 / 44.4** / 91.3 |
| Mean signed error | +162.5 | **+51.8** |
| Pearson r | **0.869** | 0.774 |
| Spearman ρ | **0.961** | 0.956 |
| Mean reasoning tokens / request | 646 | **335** |

- **Counting error falls significantly.** Absolute error is lower in 842 images and higher in 626 (132 ties); Wilcoxon signed-rank p = 4.1×10⁻¹⁵, paired t-test p = 1.1×10⁻⁵.
- **The gain is the removal of zero-shot over-estimation.** The mean bias on High scenes drops from +240.7 to +81.4, and on scenes above 1,000 people from +1,308 to +270. By contrast, on Low-density scenes the examples make counting slightly *worse* (MAE 11.5 → 18.8, bias −4.2 → −12.6); Medium is unchanged (40.6 → 40.4).
- **Density labelling improves, mostly through balance.** The examples teach the model where the dataset puts its Low/Medium/High boundaries: Low recall almost doubles and Medium doubles, at the price of High recall (99.6% → 91.3%). The accuracy gain is modest but significant: 157 images become correct and 115 become incorrect (McNemar p = 0.013). The weighted F1 jumps from 71.0% to 77.2%.
- **Pearson r falls (0.869 → 0.774)** while RMSE improves; image 814 (an under-count to 142) and image 2203 (an over-count to 18,472) alone account for a lot of this, so the Pearson comparison should be read with that in mind. Spearman is essentially unchanged.
- **The model reasons about half as long** with examples (335 vs 646 tokens), though the input is nearly five times longer (1,525 vs 317 tokens).

---

## 9. Reasoning Effort and Cost

| Quantity | Value |
|---|---|
| Mean input tokens / request | 1,525 |
| Mean output tokens / request | 350 (of which reasoning: 335; median 297) |
| Longest output | 1,908 tokens |
| Total input / output tokens | 2,439,799 / 560,211 |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported prices) | ≈ **$2.62** |

As in zero-shot, reasoning length correlates negatively with both the true count (Spearman ρ = −0.18) and absolute error (ρ = −0.21) — effort is not concentrated on the hardest images — and is highest on Medium-density images (mean 410 tokens vs 310 for Low and 318 for High).

---

## 10. Interpretation

With five labelled examples and no YOLO count, GPT-6.1 Terra is the strongest 5-shot Experiment A result in the project on every metric: MAE 140.21 (Gemma 264.87), density accuracy 77.81% (best open-source 69.00%), Spearman 0.956, perfect format reliability, no support-example copying to speak of, and no placeholder hallucinations. Relative to its own zero-shot run, the examples do two things: they calibrate scale (the systematic zero-shot over-estimate on dense scenes largely disappears) and they calibrate the density labels (the model stops defaulting to "High"). They do not help everywhere — Low-density counting is slightly worse, and Medium-density images are still called High almost half the time.

---

## 11. Limitations

- One run, not deterministic (no temperature control in reasoning mode); run-to-run variation was not measured.
- Compared with open models that differ in scale, architecture and decoding; reasoning-enabled inference is a further confound.
- The support examples were drawn from `support_mapping.csv` and are the same ones used for the open-source models; the effect of a different choice of examples was not tested.
- Token prices used for the cost figure are third-party-reported and should be checked against OpenAI's pricing page.

---

## 12. Status

5-shot Experiment A is complete for GPT-6.1 Terra. Experiment B is also complete — see `GPT_ExperimentB_Findings.md` and `GPT_A_vs_B_Comparison.md`.
