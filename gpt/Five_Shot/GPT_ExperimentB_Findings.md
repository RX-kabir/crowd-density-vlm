# GPT-6.1 Terra — 5-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. Five labelled support examples + the test image, plus a two-line statement giving the YOLO-predicted count for the test image (identical wording to the other models' 5-shot Experiment B). `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, 512 px images, Batch API. `temperature` is not settable in reasoning mode, so this is a single non-deterministic run. The paired comparison with Experiment A is in `GPT_A_vs_B_Comparison.md`.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 138.11 |
| RMSE | 494.14 |
| MAPE | 29.97% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 77.81% |
| Precision | 77.67% |
| Recall | 77.81% |
| F1-score | 77.52% |
| Valid predictions | 1600 / 1600 |

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same images): Experiment B beats it on all three metrics, and by a wide margin on MAPE (29.97% vs 50.64%). In a paired comparison of absolute error, B is closer to the truth than YOLO on 1123 images versus 185 for YOLO (292 ties; Wilcoxon p ≈ 4×10⁻¹³⁴).

**Against the open-source 5-shot Experiment B runs** (recomputed from the saved `*_experiment_B_evaluated.csv` files):

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Exact YOLO echo |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 259.16 | 884.06 | 133.52% | 57.9% | 58.7% | 0.112 | 0.645 | 64.6% |
| LLaVA-Interleave-0.5B | 321.11 | 784.55 | 524.81% | 37.8% | 41.4% | 0.070 | 0.402 | 62.4% |
| Gemma 3 (4B) | 240.83 | 881.38 | 89.76% | 66.4% | 62.2% | 0.107 | 0.761 | 1.1% |
| **GPT-6.1 Terra** | **138.11** | **494.14** | **29.97%** | **77.8%** | **77.5%** | **0.753** | **0.936** | **17.7%** |

GPT's MAE is about 43% below Gemma's, the best open-source 5-shot B. Caveat: GPT-6.1 Terra differs from the open models in scale, architecture, API serving **and** in running with medium-effort reasoning enabled; this experiment cannot attribute the gap to any one of those factors.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses with status `completed` | 1600 / 1600 |
| Truncated / incomplete responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 23 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1559 with a single line break, 41 with a blank line — both parse correctly). No bracketed density words, no explanations and no placeholder strings, unlike LLaVA's 5-shot Experiment B. Cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported): ≈ **$2.33**, with a mean of 257 reasoning tokens (median 235) per request.

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of 1600 | MAE | Bias |
|---|---|---|---|---|
| Echoes the YOLO count exactly | 283 | 17.7% | 110.2 | −108.7 |
| Within 10% of YOLO, not exact | 54 | 3.4% | 31.6 | — |
| More than 10% **above** YOLO | 1259 | 78.7% | 149.4 | −33.9 |
| More than 10% **below** YOLO | 4 | 0.3% | 1.0 | — |

**The answer is almost never below the YOLO count:** 1595 of 1600 predictions (99.7%) are equal to or above it, with a typical answer of **1.76× the YOLO count** (median ratio; quartiles 1.16× and 3.63×). As in the zero-shot run, the model treats the YOLO number as a floor to be revised upward, not as an answer to be copied.

**Only 17.7% are exact echoes** — far below Qwen (64.6%) and LLaVA (62.4%), above Gemma (1.1%). The echo rate falls with density: 26.6% on Low, 19.0% on Medium and 15.4% on High images. Unlike zero-shot, echoed rows are not "easy": their mean absolute error is 110.2, because 30 of them copy a YOLO count of exactly 300 (see below). Separately, 28 predictions (1.8%) match one of the five support counts, 24 of them not also a YOLO echo — no systematic copying of the support examples.

**How the model treats a plausible versus an implausible YOLO count** (groups are defined with the ground truth, which the model does not see — this describes behaviour, not a rule the model is known to follow):

| Subset | n | Exact echo of YOLO | MAE: B | MAE: A | MAE: YOLO itself |
|---|---|---|---|---|---|
| YOLO is at least 75% of the true count | 404 | **45.3%** | 15.4 | 25.9 | 12.4 |
| YOLO is below 25% of the true count | 402 | **3.5%** | 407.6 | 405.1 | 728.7 |

When the YOLO count is reasonable the model adopts it in nearly half the cases and its error falls; when the count is wildly low the model almost never copies it — but, unlike zero-shot, its error is no better than in Experiment A (407.6 vs 405.1).

**A property of the YOLO input itself.** The YOLO counts never exceed 300: 135 images (8.4%) have a count of exactly 300 and none has more; 99.3% of those images have a true count above 300 (median 759). This is consistent with a detection-count cap in the YOLO inference run (such as the default maximum of 300 detections in common YOLO toolkits) — an inference from the data, worth verifying in the script that produced `yolo_predictions.csv`. How GPT treats the saturated value:

| Images with YOLO = 300 (n = 135) | |
|---|---|
| Predicts more than 300 | 77.8% |
| Echoes 300 exactly | 22.2% |
| MAE — Experiment B / Experiment A / YOLO itself | 406.1 / 378.5 / 803.0 |

GPT mostly does not accept 300 — but it accepts it more often than in zero-shot (22.2% vs 12.6% echo), and on these images B is slightly *worse* than A. The 135 capped images (8.4% of the data) contribute **24.8%** of B's total absolute error. Across the other 1,465 images the MAE is 113.4 for B, 118.2 for A and 190.2 for YOLO.

**Zero YOLO counts.** 26 images have a YOLO count of 0; GPT's median answer on these is 40.5 (maximum 4,338), MAE 456.7.

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 21.7 | 165.7 | −17.9 |
| Medium (1) | 315 | 43.7 | 116.1 | −27.0 |
| High (2) | 1063 | 190.4 | 598.2 | −58.8 |

*(bias = mean signed error, predicted − ground truth; negative = under-counts.)*

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 1.5 | +1.0 |
| 11–50 | 378 | 8.2 | +3.3 |
| 51–100 | 301 | 21.9 | +8.4 |
| 101–500 | 625 | 66.2 | −15.3 |
| 501–1,000 | 126 | 323.5 | −88.1 |
| 1,001+ | 112 | 1,152.3 | −519.8 |

Counting is excellent on sparse scenes (MAE 1.5 on 0–10 people, 8.2 on 11–50) and degrades with crowd size; above 500 people the model under-counts, in the direction of YOLO's own bias (the YOLO count under-counts by 2,091 per image above 1,000). Overall: 632 over-counts, 894 under-counts, 74 exact; median absolute error 21.0; 27.6% of predictions within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 138.11 to 121.14.

---

## 5. Density Classification

Always predicting "High" scores 66.44%; GPT's 77.81% (1245 / 1600) is clearly above it (binomial p ≈ 1.3×10⁻²³).

| Density | n | Recall |
|---|---|---|
| Low | 222 | 59.9% (133 / 222) |
| Medium | 315 | 47.9% (151 / 315) |
| High | 1063 | 90.4% (961 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 133 | 75 | 14 |
| **True Medium** | 26 | 151 | 138 |
| **True High** | 9 | 93 | 961 |

Predicted shares are Low 10.5% / Medium 19.9% / High 69.6% (truth: 13.9% / 19.7% / 66.4%) — close to the real class mix. The weakness is the Medium class: 138 of 315 Medium images (43.8%) are called High and 93 High images are called Medium. Open-source 5-shot B accuracies for reference: Qwen 57.9%, LLaVA 37.8%, Gemma 66.4%.

---

## 6. Correlation With Ground Truth

- **Pearson r = 0.753**
- **Spearman ρ = 0.936**

Both far exceed every open-source 5-shot B correlation (best: Pearson 0.112 for Qwen, Spearman 0.761 for Gemma). The Pearson/Spearman gap is narrow, i.e. the model is both a good ranker and a reasonable absolute estimator, with a handful of large outliers (Section 7).

---

## 7. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 814 | 8,994 | **96** | 6 | 8,898 |
| 4159 | 6,210 | 12,000 | 55 | 5,790 |
| 1343 | 3,428 | 7,924 | 26 | 4,496 |
| 2203 | 4,622 | **201** | 201 | 4,421 |
| 3539 | 6,757 | 2,600 | 300 | 4,157 |
| 212 | 9,059 | 5,000 | 1 | 4,059 |

The largest error, image 814, is a clear case of following an absurdly low YOLO count (6) down to 96 for a crowd of 8,994. Image 2203 is an exact echo of the YOLO count (201) — in 5-shot Experiment A the same image was answered 18,472, the worst error of that run. The two over-shoots (4159, 1343) are on scenes where the YOLO count is far too low (55 and 26) and the model rejects it but lands too high. The largest prediction in the run is 12,000 (one above 10,000).

**Test image 3411 (true count 105)** — which produced the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **139** (YOLO count 110): the anomaly does not reproduce. **Image 3178** (true count 7,560, YOLO count 9), the failure case of zero-shot B (answered 14), is answered **7,500** here, so the model did not follow the tiny YOLO number this time.

---

## 8. Interpretation

With five labelled examples *and* a YOLO count, GPT-6.1 Terra is the strongest 5-shot Experiment B result in the project on every metric: MAE 138.11, MAPE 29.97%, density accuracy 77.81%, correlation far above the open models, and perfect format reliability. It uses the YOLO number in the same way as in zero-shot — as a floor, revised upward (99.7% of answers at or above it, median 1.76×) rather than copied (17.7%) — and its gains are concentrated where the YOLO number is credible: sparse scenes (MAE 1.5 for 0–10 people) and images where YOLO is within a quarter of the truth. Where the YOLO number is wildly low (below 25% of the truth) or saturated at 300, the added count does not help beyond what the five examples already give. The density classification is the same quality as Experiment A's (accuracy identical to the digit; see the comparison document), so the YOLO count adds scale information, not category information.

---

## 9. Limitations

- Single, non-deterministic run; variance between runs was not measured.
- The subset analysis in Section 3 uses the ground truth to define groups; it describes behaviour and does not show an explicit plausibility rule.
- The analysis of the 300-count wall is descriptive; the cause (a detection cap in the YOLO run) is an inference, not verified here.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning.
- Token prices are third-party-reported and should be checked against OpenAI's pricing page.

---

## 10. Status

5-shot Experiment B is complete for GPT-6.1 Terra (see also `GPT_ExperimentA_Findings.md` and `GPT_A_vs_B_Comparison.md`). The zero-shot density-definition experiments have not yet been run for this model.
