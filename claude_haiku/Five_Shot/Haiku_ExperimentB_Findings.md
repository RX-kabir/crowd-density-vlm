# Claude Haiku 5.5 — 5-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. Five labelled support examples + the test image, plus a two-line statement giving the YOLO-predicted count for the test image (identical wording to the other models' 5-shot Experiment B). `claude-haiku-5-5`, Anthropic Messages API, adaptive thinking, effort **medium**, 512 px images, Message Batches API. Sampling parameters cannot be set on this model, so this is a single non-deterministic run. The paired comparison with Experiment A is in `Haiku_A_vs_B_Comparison.md`.

*Data note:* the first version of the Claude notebooks did not write the `yolo_predicted_count` column into the Experiment B CSV. The column was added to the copies in this repository by merging `yolo/yolo_predictions.csv` — the file the prompts were built from — on `test_filename`; the notebooks have been fixed for the remaining B runs.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 220.92 |
| RMSE | 1100.55 |
| MAPE | 44.26% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 71.31% |
| Precision | 76.33% |
| Recall | 71.31% |
| F1-score | 72.41% |
| Valid predictions | 1600 / 1600 |

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same images): Experiment B beats it on **MAE and MAPE** but **not on RMSE** (1100.55 vs 737.65) — a few very large errors remain (Section 7). In a paired comparison of absolute error, B is closer to the truth than YOLO on 1130 images versus 269 for YOLO (201 ties; Wilcoxon p ≈ 5×10⁻⁹⁹).

**Against the open-source 5-shot Experiment B runs** (recomputed from the saved `*_experiment_B_evaluated.csv` files):

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Exact YOLO echo |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 259.16 | 884.06 | 133.52% | 57.9% | 58.7% | 0.112 | 0.645 | 64.6% |
| LLaVA-Interleave-0.5B | 321.11 | 784.55 | 524.81% | 37.8% | 41.4% | 0.070 | 0.402 | 62.4% |
| Gemma 3 (4B) | 240.83 | 881.38 | 89.76% | 66.4% | 62.2% | 0.107 | 0.761 | 1.1% |
| GPT-6.1 Terra | **138.11** | **494.14** | **29.97%** | **77.8%** | **77.5%** | **0.753** | **0.936** | 17.7% |
| **Claude Haiku 5.5** | 220.92 | 1100.55 | 44.26% | 71.3% | 72.4% | 0.541 | 0.879 | 11.5% |

Claude beats every open-source run on MAE, MAPE, density accuracy and both correlations, but its RMSE is the worst of the five models. It is second to GPT-6.1 Terra everywhere except RMSE. Caveat: Claude Haiku 5.5 differs from the open models in scale, architecture and serving, and from GPT in running with little thinking (Section 3).

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses with stop reason `end_turn` | 1600 / 1600 |
| Truncated / refused responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 24 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1304 with a blank line between them, 296 with a single line break). No explanations and no placeholder strings. Cost at Batch prices ($0.05 / $0.25 per million input / output tokens, Anthropic's published rates for Claude Haiku 5.5; verify): ≈ **$0.17** (3,034,551 input and 67,711 output tokens).

---

## 3. Thinking: Still Rare, but Twice as Common as Without the YOLO Line

Output length shows when the model thought (a bare answer is about 13 tokens): **1429 of 1600 requests (89.3%) were answered directly**, 171 (10.7%) produced longer output (170 of them more than 100 tokens; maximum 716). In Experiment A the figure was 91 (5.7%). The requests with longer output have a similar MAE (233.1 against 219.5) but a lower density accuracy (59.6% against 72.7%); they are somewhat more likely on Low-density images (14.4% of Low, 11.1% of Medium, 9.8% of High). Thinking text is not returned by default, so its content is unknown, and the API does not report thinking tokens separately.

---

## 4. Where the Predicted Count Comes From

| Source | n | % of 1600 | MAE | Bias |
|---|---|---|---|---|
| Exact echo of the YOLO count | 184 | 11.5% | 176.4 | −175.8 |
| Within 10% of YOLO, not exact | 418 | 26.1% | 103.1 | — |
| More than 10% **above** YOLO | 983 | 61.4% | 280.8 | −28.9 |
| More than 10% **below** YOLO | 15 | 0.9% | 126.3 | — |

**The answer is usually at or above the YOLO count:** 1479 of 1600 (92.4%), with a typical answer of **1.26×** the YOLO count (median ratio; quartiles 1.04× and 2.56×) — a milder "floor and revise upward" than GPT's (99.7%, 1.76×). **Exact echoes are 11.5%**, between Gemma (1.1%) and GPT (17.7%) and far below Qwen (64.6%) and LLaVA (62.4%); the echo rate is 23.4% on Low-density images, 9.8% on Medium and 9.5% on High. Echoes are costly: they have an MAE of 176.4 and a mean bias of −175.8, because they include copies of the capped values described below. Only 17 predictions (1.1%) equal a support count (16 of them not also a YOLO echo), so the support examples are not being copied. B's answer is closer to the YOLO count than its own Experiment A answer in 92.8% of images, and 96.3% of count predictions differ from A's.

**How the model treats a plausible versus an implausible YOLO count** (groups defined with the ground truth, which the model does not see — this describes behaviour, not a rule the model is known to follow):

| Subset | n | Exact echo of YOLO | MAE: B | MAE: A | MAE: YOLO itself |
|---|---|---|---|---|---|
| YOLO is at least 75% of the true count | 404 | **24.5%** | 18.7 | 59.4 | 12.4 |
| YOLO is below 25% of the true count | 402 | **5.2%** | 656.7 | 935.3 | 728.7 |

When YOLO is credible the model adopts it in about a quarter of cases and its error falls to a third of what it had without it; when YOLO is wildly low it mostly does not copy it, and its error still falls (935 → 657, below YOLO's own 729).

**The YOLO counts never exceed 300** — 135 images (8.4%) are at exactly 300, and 99.3% of those have a true count above 300 (median 759). This is consistent with a detection-count cap in the YOLO run (such as the default maximum of 300 detections in common YOLO toolkits — the inference notebook calls `predict` without `max_det`), an inference to be verified. On those images Claude answers above 300 in 84.4% of cases and echoes 300 in 6.7%; its MAE is 670.8 (Experiment A: 1125.3; YOLO: 803.0). The 135 images carry 25.6% of B's total absolute error. On the other 1,465 images the MAE is 179.5 for B, 269.5 for A and 190.2 for YOLO. **Zero YOLO counts:** 26 images; the median answer is 24 (maximum 4,500), MAE 405.2.

---

## 5. Density Classification

Always predicting "High" scores 66.44%; Claude's 71.31% (1141 / 1600) is above it (binomial p ≈ 2×10⁻⁵) but by a smaller margin than Experiment A's.

| Density | n | Recall |
|---|---|---|
| Low | 222 | 39.6% (88 / 222) |
| Medium | 315 | 60.0% (189 / 315) |
| High | 1063 | 81.3% (864 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 88 | 120 | 14 |
| **True Medium** | 17 | 189 | 109 |
| **True High** | 9 | 190 | 864 |

Predicted shares are Low 7.1% / Medium 31.2% / High 61.7% (truth: 13.9% / 19.7% / 66.4%): the model now over-predicts *Medium* and under-predicts High (190 High images are called Medium), the reverse of its Experiment A bias. Errors are balanced in direction (216 predictions sparser than the truth, 243 denser). Per-class recall (Low / Medium / High) of the 5-shot B runs: Qwen 26.6 / 32.7 / 72.0, LLaVA 21.6 / 35.9 / 41.7, Gemma 1.8 / 41.6 / 87.3, GPT 59.9 / 47.9 / 90.4, **Claude 39.6 / 60.0 / 81.3** — the best Medium recall of the five.

---

## 6. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 17.8 | 61.1 | −10.3 |
| Medium (1) | 315 | 61.9 | 188.4 | −57.8 |
| High (2) | 1063 | 310.5 | 1346.0 | −79.7 |

*(bias = mean signed error, predicted − ground truth; negative = under-counts.)*

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 3.8 | +3.1 |
| 11–50 | 378 | 8.3 | −1.9 |
| 51–100 | 301 | 26.8 | −6.4 |
| 101–500 | 625 | 106.5 | −38.1 |
| 501–1,000 | 126 | 505.4 | −136.5 |
| 1,001+ | 112 | 1,891.2 | −551.4 |

Counting is excellent on sparse scenes (MAE 3.8 for 0–10 people, 8.3 for 11–50) and degrades with crowd size, now with an **under-count** above 100 people (the direction of YOLO's own bias). Overall: 373 over-counts, 1159 under-counts, 68 exact; mean signed error −65.8; median absolute error 28.0; 18.9% of predictions within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 220.92 to 180.38; the 10 worst account for 24% of the total absolute error.

---

## 7. Worst Cases and Stock Numbers

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 212 | 9,059 | **45,000** | 1 | 35,941 |
| 3015 | 895 | 11,000 | 11 | 10,105 |
| 814 | 8,994 | **38** | 6 | 8,956 |
| 3539 | 6,757 | 1,200 | 300 | 5,557 |
| 3178 | 7,560 | 2,350 | 9 | 5,210 |
| 1795 | 5,681 | 812 | 300 | 4,869 |

The two largest errors are over-counts on images where YOLO is almost zero (counts of 1 and 11): the model rejects the implausible number and overshoots wildly (45,000 for a crowd of 9,059 — the largest prediction in the run). Large predictions are much rarer than in Experiment A: 2 exceed 10,000 (A: 5) and 6 reach 5,000 or more (A: 26). Image 814 shows the opposite failure, adopting a tiny YOLO count (6) as 38. **Test image 3411** (true count 105; the identical value 21,482 in eight Qwen and Gemma conditions) is answered **110**, exactly the YOLO count. **Image 1510**, which Experiment A answered 60,000, is answered 41 (the YOLO count). **Image 3178** (YOLO count 9) is answered 2,350 rather than copying the 9.

**Stock numbers fade, but do not vanish:** the most frequent answers are 412 (71 times), 58 (58), 27 (44), 52 (42) and 41 (39) — 412 persists, but the Experiment A default of 1200 (70 times) is gone. Multiples of 100 are 5.2% of predictions (A: 15.9%; truth 0.9%), and 64 of the 71 predictions of 1,000 or more are multiples of 100.

---

## 8. Correlation With Ground Truth

- **Pearson r = 0.541**
- **Spearman ρ = 0.879**

Both are far above the open-source 5-shot B runs (best: Pearson 0.112 for Qwen, Spearman 0.761 for Gemma) and below GPT's (0.753 / 0.936). Unlike for GPT, both correlations are slightly *higher* than in Experiment A (0.520 / 0.871).

---

## 9. Interpretation

With five labelled examples and a YOLO count, Claude Haiku 5.5 becomes the second-best model on this condition: MAE 220.92 and MAPE 44.26% (both better than the YOLO baseline and every open-source run), the best Medium-density recall of any model, perfect reliability, and a cost of 17 cents for the whole run. It uses the YOLO number as a lower bound to revise upward (92% of answers at or above it, median 1.26×) rather than as an answer to copy (11.5% exact echoes), which turns the systematic over-count of Experiment A into a mild under-count. Two limitations stand out: the **heavy tail** remains (RMSE 1100.55, worse than YOLO's 737.65, driven by outliers such as 45,000 and 11,000 on images with YOLO counts of 1 and 11), and **density accuracy is lower than without the YOLO count** (71.3% against 74.7%), with a swing from over-predicting High to over-predicting Medium (see the comparison document).

---

## 10. Limitations

- Single non-deterministic run; variance between runs was not measured.
- Only effort `medium` was tested, and the model answered directly on 89% of images.
- The subset analysis in Section 4 uses the ground truth to define groups; it describes behaviour and does not show an explicit plausibility rule.
- The analysis of the 300-count wall is descriptive; its cause (a detection cap in the YOLO run) is an inference.
- The YOLO column in the repository copy of the CSV was added after the run (see the data note above).
- Prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 11. Status

5-shot Experiment B is complete for Claude Haiku 5.5 (see also `Haiku_ExperimentA_Findings.md` and `Haiku_A_vs_B_Comparison.md`). The zero-shot and density-definition experiments have not yet been run for this model.
