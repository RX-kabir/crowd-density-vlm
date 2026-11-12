# GPT-6.1 Terra — Zero-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. Same zero-shot prompt as Experiment A, with one addition: a two-line statement giving the YOLO-predicted count for the test image (identical wording to the other models' zero-shot Experiment B). `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, 512 px images, Batch API. `temperature` is not settable in reasoning mode, so this is a single non-deterministic run.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 133.87 |
| RMSE | 490.77 |
| MAPE | 45.64% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 76.25% |
| Precision | 75.62% |
| Recall | 76.25% |
| F1-score | 72.77% |
| Valid predictions | 1600 / 1600 |

The YOLO baseline on the same images has MAE 241.87, RMSE 737.65 and MAPE 50.64%: Experiment B beats it on all three. Against Experiment A (MAE 198.45) counting error is 32.5% lower; the full paired comparison is in `GPT_ZeroShot_A_vs_B_Comparison.md`.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses with status `completed` | 1600 / 1600 |
| Truncated / incomplete responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 24 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1405 with a single line break between them, 195 with a blank line — both parse correctly). There are no bracketed density words, no explanations and no degenerate placeholder strings, unlike LLaVA's 5-shot Experiment B, where 23.3% of bracketed density words disagreed with their own digit and 3 responses were an identical degenerate string. Cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported): ≈ $2.50, with a mean of 541 reasoning tokens (median 474) per request.

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of 1600 | MAE | Bias |
|---|---|---|---|---|
| Echoes the YOLO count exactly | 215 | 13.4% | 47.8 | −46.1 |
| Within 10% of YOLO, not exact | 76 | 4.8% | 26.7 | −23.8 |
| More than 10% **above** YOLO | 1305 | 81.6% | 154.7 | +28.4 |
| More than 10% **below** YOLO | 4 | 0.3% | 1.0 | −1.0 |

**The answer is almost never below the YOLO count.** 1593 of 1600 predictions (99.6%) are equal to or above it; only 7 are below, and the four that are more than 10% below are reductions of 1–5 people on scenes with 4–14 people, each ending within 3 of the true count. The typical answer is **1.87× the YOLO count** (median ratio; quartiles 1.22× and 4.04×). GPT therefore uses the YOLO number as a floor to be revised upward, not as an answer to be copied.

**Only 13.4% are exact echoes** — far below LLaVA (95.8% in zero-shot B) and Qwen (46.2%), above Gemma (1.3%). Echoes concentrate on easy scenes: the echo rate is 25.2% on Low-density images, 15.2% on Medium and 10.4% on High, and echoed rows have a mean absolute error of 47.8 against 154.7 for the rest.

**A property of the YOLO input itself.** The YOLO counts in this experiment **never exceed 300** — 135 images (8.4%) have a YOLO count of exactly 300 and none has more (Figure 4 shows this as a vertical wall at 300). 99.3% of those images have a true count above 300 (median 759). This is consistent with a detection-count cap in the YOLO inference run, such as the default maximum of 300 detections in common YOLO toolkits — worth verifying in the script that produced `yolo_predictions.csv`, since it would also explain the YOLO baseline's large undercounts on dense scenes. How GPT responds to the saturated value:

| Images with YOLO = 300 (n = 135) | |
|---|---|
| Predicts more than 300 | 87.4% |
| Echoes 300 exactly | 12.6% |
| MAE — Experiment B / Experiment A / YOLO itself | 338.4 / 532.7 / 803.0 |

GPT mostly does not accept 300 as the answer. Across the other 1,465 images (YOLO < 300) the MAE is 115.0 for B, 167.6 for A and 190.2 for YOLO. The 135 saturated images contribute 21.3% of B's total absolute error from 8.4% of the images.

**Zero YOLO counts.** 26 images have a YOLO count of 0; GPT's median answer on these is 32.5 (maximum 3,780), MAE 408.1 — the model rejects the zero but its replacement is unreliable.

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 15.9 | 94.9 | −11.2 |
| Medium (1) | 315 | 36.8 | 80.3 | −8.0 |
| High (2) | 1063 | 187.3 | 598.9 | +28.6 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)* The error is concentrated in the High stratum, but unlike Experiment A (High bias +240.7) the bias is now small. Mean signed error by true count: 0–10: +19.8; 11–50: +3.4; 51–100: +13.0; 101–500: +14.7; 501–1,000: +54.2; above 1,000: +27.0. Predictions are balanced in sign: 730 over-counts, 787 under-counts, 83 exact; median absolute error 20.5; 29.0% of predictions are within ±10% of the truth.

**Density classification**

| Density | Recall |
|---|---|
| Low | 33.8% (75 / 222) |
| Medium | 28.6% (90 / 315) |
| High | 99.3% (1055 / 1063) |

Confusion matrix (rows = truth, columns = prediction): Low [75, 117, 30]; Medium [0, 90, 225]; High [0, 8, 1055]. 76.25% accuracy is above the always-"High" baseline (66.44%), but it is carried by High recall: 225 of 315 Medium images (71%) and 30 of 222 Low images are called High, and 81.9% of all predictions are "High" (truth: 66.4%).

---

## 5. Correlation With Ground Truth

- **Pearson r = 0.805**
- **Spearman ρ = 0.944**

Both are well above the one open-source zero-shot Experiment B correlation documented in this project (Gemma: Pearson 0.192, Spearman 0.835), though slightly below Experiment A's (0.869 / 0.961) — pulling answers toward a compressed, capped YOLO scale marginally weakens the model's own ordering of crowd sizes.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 3178 | 7,560 | **14** | 9 | 7,546 |
| 4159 | 6,210 | 12,000 | 55 | 5,790 |
| 814 | 8,994 | 3,500 | 6 | 5,494 |
| 3697 | 2,447 | 7,500 | 77 | 5,053 |
| 2580 | 990 | 5,987 | 72 | 4,997 |
| 3015 | 895 | 5,284 | 11 | 4,389 |

The largest error, image 3178, is the one clear case of the model adopting an absurdly small YOLO count (9) as its answer (14); in Experiment A it had instead over-shot to 12,000. In the other five, the model correctly rejects an implausibly low YOLO count but lands too high, often on round values (12,000, 3,500, 7,500). The largest prediction in the run is 12,000 (one above 10,000).

**Test image 3411 (true count 105)** — which produced the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **110**, exactly the YOLO count; the anomaly does not reproduce.

---

## 7. Interpretation

With a YOLO count in the prompt, GPT-6.1 Terra becomes both the most accurate and one of the most reliable systems in the project: MAE 133.87, perfect formatting, no hallucinated placeholders, and better than the YOLO input on every counting metric. It gets there by a strategy no open-source model showed: it neither copies the YOLO number (13.4% echo) nor ignores it, but treats it as a lower bound and revises upward — 99.6% of answers are at or above it, typically at about 1.9× — which cancels the over-estimation bias seen in Experiment A (+1,308 per image above 1,000 people becomes +27). The model also does not accept the saturated "300" (87.4% answer above it).

Two limitations stand out. Density labelling is essentially unchanged — the count gives scale, not the dataset's Low/Medium/High boundaries — so 71% of Medium images are still called High. And a floor-and-revise strategy fails when the floor is absurdly low: image 3178 shows the model following a YOLO count of 9 down to 14 for a crowd of 7,560.

---

## 8. Limitations

- Single, non-deterministic run; variance between runs was not measured.
- The analysis of the 300-count wall is descriptive; the cause (a detection cap in the YOLO run) is an inference from the data, not something verified here.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning.

---

## 9. Status

Zero-shot Experiment B is complete for GPT-6.1 Terra (see also `GPT_ZeroShot_A_Findings.md` and `GPT_ZeroShot_A_vs_B_Comparison.md`). The 5-shot experiments are also complete (see `../Five_Shot/`); the density-definition experiments have not yet been run for this model.
