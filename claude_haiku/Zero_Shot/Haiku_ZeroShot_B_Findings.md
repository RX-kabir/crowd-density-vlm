# Claude Haiku 5.5 — Zero-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. Same zero-shot prompt as Experiment A, with one addition: a two-line statement giving the YOLO-predicted count for the test image (identical wording to the other models' zero-shot Experiment B). `claude-haiku-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 237.11 |
| RMSE | 1384.49 |
| MAPE | 43.01% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 70.31% |
| Precision | 70.04% |
| Recall | 70.31% |
| F1-score | 65.97% |
| Valid predictions | 1600 / 1600 |

**Correlation:** Pearson r = 0.590, Spearman ρ = 0.899.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): Experiment B beats it on MAE (by a hair) and MAPE (43.01% vs 50.64%) but **not on RMSE** (1384 vs 738). In a paired comparison of absolute error B is closer to the truth on **1090 images**, YOLO on 273 (237 ties; Wilcoxon p = 5×10⁻⁸⁷). Against Experiment A (MAE 482.64) counting error is 50.9% lower; the full paired comparison is in `Haiku_ZeroShot_A_vs_B_Comparison.md`.

**Against the other zero-shot Experiment B runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Exact YOLO echo |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 262.36 | 922.89 | 67.82% | 65.8% | 55.7% | 0.294 | 0.772 | 46.2% |
| LLaVA-Interleave-0.5B | 233.86 | 679.08 | 53.29% | 14.6% | 4.7% | 0.420 | 0.747 | 95.8% |
| Gemma 3 (4B) | 234.54 | 882.49 | 56.67% | 64.7% | 63.3% | 0.192 | 0.835 | 1.3% |
| GPT-6.1 Terra | **133.87** | **490.77** | 45.64% | **76.25%** | **72.77%** | **0.805** | **0.944** | 13.4% |
| **Claude Haiku 5.5** | 237.11 | 1384.49 | **43.01%** | 70.31% | 65.97% | 0.590 | 0.899 | 14.1% |

Claude has the **lowest MAPE of all five models** (43.01%, GPT 45.64%) — most of its answers are proportionally close — but its MAE is no better than LLaVA's or Gemma's (which largely copy or ignore the YOLO count) and its RMSE is the worst of the five, because five predictions above 10,000 remain (Section 6). Density accuracy and both correlations are second to GPT and far above the open models. As always, Claude differs from the open models in scale, architecture, serving and adaptive thinking, so the gaps cannot be attributed to one cause.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 24 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (925 with a single line break, 675 with a blank line between them; both parse). No explanations and no degenerate strings. Cost at Batch prices ($0.05 / $0.25 per 1M tokens; Anthropic's published rates, to be verified): **≈ $0.13**, mean 244 output tokens per request (median 183; thinking is included in this figure).

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of 1600 | MAE | Bias |
|---|---|---|---|---|
| Echoes the YOLO count exactly | 225 | 14.1% | 95.5 | −95.0 |
| Within 10% of YOLO, not exact | 318 | 19.9% | 69.5 | — |
| More than 10% **above** YOLO | 1038 | 64.9% | 321.7 | +81.7 |
| More than 10% **below** YOLO | 19 | 1.2% | 96.8 | — |

**The answer is rarely below the YOLO count.** 1502 of 1600 predictions (93.9%) are equal to or above it. The typical answer is **1.37× the YOLO count** (median ratio; quartiles 1.04× and 3.0×): the model uses the number as a floor and revises upward, less aggressively than GPT (1.87×). 1470 count predictions (92%) differ from Experiment A's, and B's answer is closer to the YOLO count than A's in 84.4% of images.

**Exact echoes are the minority (14.1%)** — between Gemma (1.3%) and Qwen (46.2%) and almost the same as GPT (13.4%). They concentrate on easy scenes: echo rate 23.9% on Low, 20.3% on Medium, 10.2% on High images; there is no difference between requests with and without extended thinking (14.1% in both).

**The 300 cap in the YOLO input.** The YOLO counts never exceed 300: 135 images (8.4%) have a YOLO count of exactly 300 and none has more; 99.3% of those images have a true count above 300 (median 759). This is consistent with a detection cap in the YOLO inference script (such as a default maximum of 300 detections) but has not been verified. Claude's response: on those images it answers above 300 in **95.6%** of cases and echoes 300 in only 1.5%; MAE is 620.2 for B, 1203.0 for A and 803.0 for YOLO itself. On the other 1,465 images the figures are 201.8 / 416.3 / 190.2 (YOLO is then slightly better than B). The 135 saturated images contribute 22.1% of B's total absolute error from 8.4% of the images.

**Zero YOLO counts.** On the 26 images with a YOLO count of 0, the median answer is 20 (maximum 5,200) and MAE is 483.0 — the model rejects the zero but its replacement is unreliable.

**When YOLO is nearly right vs. very wrong:**

| Subset | n | Echo rate | MAE — B | MAE — A | MAE — YOLO |
|---|---|---|---|---|---|
| YOLO ≥ 75% of the true count | 404 | 31.7% | 19.0 | 50.1 | 12.4 |
| YOLO < 25% of the true count | 402 | 4.5% | 717.1 | 1540.5 | 728.7 |

When YOLO is close, Claude moves toward it (MAE 50.1 → 19.0) but is still a little worse than copying it. When YOLO is far too low, Claude recovers more than half of the A error (1540 → 717), ending at about YOLO's own level.

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 21.7 | 117.6 | −20.5 |
| Medium (1) | 315 | 102.4 | 888.0 | +2.9 |
| High (2) | 1063 | 322.0 | 1627.4 | +41.2 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)* By true count — MAE / mean bias: 0–10: 1.4 / +0.9; 11–50: 8.3 / −3.9; 51–100: 28.5 / −1.7; 101–500: 102.2 / −13.8; 501–1,000: 562.1 / +33.9; above 1,000: 2,079.3 / +413.9. Predictions are now strongly sign-skewed *downward* (419 over-counts, 1115 under-counts, 66 exact; mean signed error +25.1, driven by a few giant over-counts), the median absolute error is 28.0 and 19.2% of predictions are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 237.11 to 172.51; the 10 worst account for 35.2% of the total absolute error.

**Density classification**

| Density | Recall |
|---|---|
| Low | 15.8% (35 / 222) |
| Medium | 23.8% (75 / 315) |
| High | 95.5% (1015 / 1063) |

Confusion matrix (rows = truth, columns = prediction): Low [35, 142, 45]; Medium [3, 75, 237]; High [1, 47, 1015]. 70.31% accuracy (1125 / 1600) is above the always-"High" baseline of 66.44% (one-sided binomial p = 5×10⁻⁴), but it is carried by High recall. The model predicts "High" for 81.1% of images (truth: 66.4%), "Medium" for 16.5% and "Low" for 2.4%; 424 images are called denser than the truth and only 51 sparser.

---

## 5. Correlation With Ground Truth

- **Pearson r = 0.590**
- **Spearman ρ = 0.899**

Both are practically unchanged from Experiment A (0.580 / 0.899): the YOLO count corrects the scale of the answers without changing how the model *ranks* scenes. Spearman is above Gemma's 0.835 (the best open-source zero-shot B value) and below GPT's 0.944; Pearson (0.590) is well above every open model (best: LLaVA 0.420) and well below GPT (0.805).

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | error |
|---|---|---|---|---|
| 4056 | 6,660 | **45,000** | 10 | +38,340 |
| 212 | 9,059 | 30,000 | 1 | +20,941 |
| 3281 | 2,397 | 18,000 | 5 | +15,603 |
| 4159 | 6,210 | 21,456 | 55 | +15,246 |
| 3015 | 895 | 15,000 | 11 | +14,105 |
| 814 | 8,994 | **16** | 6 | −8,978 |

Five predictions exceed 10,000 (A: 15; maximum 45,000, down from 87,412) and together they account for **27.5%** of the total absolute error. In every one of them the YOLO count is absurdly low (1–55): the model recognises that the number cannot be right and overshoots by a large factor. Image 814 is the opposite case — YOLO says 6, the truth is 8,994, and the model answers 16, adopting the bad number. Without the five large predictions MAE would be 172.51 (descriptive only; the group is defined by the model's own outputs).

**Test image 3411 (true count 105; YOLO 110)** — the source of the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **118** (A: 175); the anomaly does not reproduce.

**Same hard images, A vs. B:**

| Image | True | YOLO | A | B |
|---|---|---|---|---|
| 2203 | 4,622 | 201 | 87,412 | 2,500 |
| 1510 | 3,641 | 41 | 50,000 | 2,500 |
| 2542 | 4,113 | 300 | 20,000 | 4,500 |
| 1343 | 3,428 | 26 | 15,420 | 4,200 |
| 3178 | 7,560 | 9 | 7,500 | 2,000 |
| 4056 | 6,660 | 10 | 45,000 | 45,000 |
| 212 | 9,059 | 1 | 45,000 | 30,000 |

The YOLO count fixes several of the placeholder-style over-counts of Experiment A (2203, 1510, 2542, 1343) but not the cases where YOLO is itself near zero (4056, 212); and on 3178 it turns a near-perfect A answer (7,500) into a poor one (2,000).

**Stock answers.** Rounding is less pronounced than in A: multiples of 10 are 32.2% of predictions (A: 46.4%; truth: 10.4%), multiples of 100 are 6.2% (A: 9.4%; truth 0.9%); of 92 predictions of 1,000 or more, 75 are multiples of 100. Most frequent answers: 12 (30 times), 350 (26), 20 and 24 (24 each), 180 (23). The A default of 180 (74 times) loses most of its weight.

---

## 7. Reasoning and Cost

| Quantity | Value |
|---|---|
| Requests with more than a bare answer (output > 15 tokens) | 1536 of 1600 (96.0%) |
| Mean / median / max output tokens | 244 / 183 / 932 |
| Mean input tokens / request | 464 |
| Total input / output tokens | 741,727 / 390,161 |
| Cost at Batch prices (Anthropic's published rates, to be verified) | ≈ **$0.13** |

As in A, the model thinks on nearly every request; the YOLO line adds about 22% to output length (199 → 244 tokens). Thinking is not reported separately, so output length is a proxy. It correlates negatively with true count (Spearman ρ = −0.49) and with absolute error (ρ = −0.34):

| Output-length quartile | n | MAE | Density accuracy | Median true count | Echo rate |
|---|---|---|---|---|---|
| ≤ 141 tokens | 401 | 178.1 | 89.5% | 182 | 10.0% |
| 142–183 | 399 | 450.9 | 84.0% | 215 | 8.3% |
| 184–322 | 400 | 172.3 | 67.5% | 89 | 12.5% |
| > 322 | 400 | 147.8 | 40.2% | 37 | 25.5% |

(Associations, not causal claims.) The longest answers are small crowds, where the model deliberates, echoes YOLO most often (25.5%) and gets the counts right but the density label wrong (40% accuracy).

---

## 8. Interpretation

With the YOLO count, Claude Haiku 5.5 improves every counting metric over zero-shot A (MAE −51%, RMSE −59%, MAPE 69.8% → 43.0%) and reaches the best MAPE of any model in this condition, yet only just matches the YOLO baseline on MAE and still trails it on RMSE. The reason is the same as in A: a handful of dense scenes whose YOLO count is implausibly low (1–55) are answered with 15,000–45,000. The model treats the YOLO number as a floor and, when it distrusts it, overshoots. Density is unaffected or slightly worse (70.31% vs 71.62%): the count says nothing about where the dataset draws class boundaries, and the model's "High" bias (81%) is unchanged. In relation to GPT, which also uses the number as a floor but overshoots far less, the two models differ mainly in how well-calibrated the revision is.

---

## 9. Limitations

- One run, not deterministic; run-to-run variation was not measured, so small differences (e.g. in density accuracy) should be read with sampling noise in mind.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- The tail analysis defines groups from the model's own outputs and is descriptive.
- The downloaded B CSV did not contain `yolo_predicted_count`; the repository copy has it added from `yolo/yolo_predictions.csv` (the baseline reproduces exactly: MAE 241.87).
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Zero-shot Experiments A and B are complete for Claude Haiku 5.5 (comparison: `Haiku_ZeroShot_A_vs_B_Comparison.md`), as are the 5-shot experiments (see `../Five_Shot/`). The density-definition experiments have not yet been run for this model.
