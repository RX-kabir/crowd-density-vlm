# Claude Sonnet 5.5 — Zero-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both zero-shot experiments complete on the full 1600-image JHU-CROWD++ test set. Neither uses support examples; Experiment B differs from A only by the extra two-line statement giving the YOLO-predicted count (identical wording to the other models' zero-shot B prompts). `claude-sonnet-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, images resized to 512 px. Sampling parameters cannot be set on this model, so each condition is a single non-deterministic run. Per-experiment detail: `Sonnet_ZeroShot_A_Findings.md` and `Sonnet_ZeroShot_B_Findings.md`.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 252.51 | **207.56** |
| RMSE | 1626.03 | **1237.58** |
| MAPE | 45.54% | **36.73%** |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **77.81%** | 76.50% |
| Precision | **84.43%** | 83.85% |
| Recall | **77.81%** | 76.50% |
| F1-score | **78.22%** | 77.31% |

**Correlation with ground truth**

| | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.685 | 0.938 |
| Experiment B | **0.767** | **0.945** |

The YOLO count lowers counting error (MAE −17.8%, RMSE −23.9%, MAPE −19.3%) and raises the linear correlation, but **slightly lowers density accuracy (−1.3 points)**. For GPT-6.1 Terra the same comparison was −32.5% MAE and +1.1 points of density; for Claude Haiku −50.9% MAE and −1.3 points.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): B beats it on MAE and MAPE but not on RMSE; A beat it only on MAPE. In a paired comparison of absolute error B is closer to the truth than YOLO on 1267 images (YOLO: 296; ties: 37), A on 1049 (YOLO: 500).

**Effect of the YOLO count in zero-shot, all models (A → B)**

| Model | MAE (A → B) | Density accuracy (A → B) |
|---|---|---|
| Qwen2.5-VL-3B | 725.92 → 262.36 | 66.8% → 65.8% |
| LLaVA-Interleave-0.5B | 380.67 (617 valid) → 233.86 | 12.7% → 14.6% |
| Gemma 3 (4B) | 332.24 → 234.54 | 64.7% → 64.7% |
| GPT-6.1 Terra | 198.45 → 133.87 | 75.2% → 76.3% |
| Claude Haiku 5.5 | 482.64 → 237.11 | 71.6% → 70.3% |
| **Claude Sonnet 5.5** | 252.51 → **207.56** | 77.8% → **76.5%** |

The relative MAE gain from the YOLO count is the smallest of any model (Sonnet −17.8%; Gemma −29%, GPT −33%, LLaVA −39%, Haiku −51%, Qwen −64%), in line with the pattern that the better the unaided model, the less it gains — but Sonnet's A run was already good only on typical images; the gain is in the tail (Section 2).

---

## 2. Statistical Significance

Paired comparison of absolute error on all 1600 images: **Wilcoxon signed-rank W = 290,503, p = 4.4×10⁻¹⁰; paired t-test t = −1.40, p = 0.16.** B has the lower error on 714 images, A on 496, with 390 ties. The rank test shows a consistent shift on the typical image (median absolute error 26.0 → 22.0; within ±10%: 23.4% → 25.1%), but the t-test, which weights the large errors, does not reach significance: the mean improvement of 45 per image is real in size but uncertain in a paired sense, because on a few images the YOLO count makes the error larger (e.g. 212: 20,000 → 45,000; 1343: 6,500 → 12,000) while on others it removes a huge one (1510: 40,000 → 5,000).

Density change (accuracy 77.81% → 76.50%): 96 density predictions changed, **37 from wrong to right and 58 from right to wrong** — exact McNemar p = 0.040. The decline is marginally significant (and within the model's own sampling noise, which was not measured).

---

## 3. Where the Change Comes From

**By ground-truth count**

| True count | n | MAE — A | MAE — B | Mean bias — A | Mean bias — B | YOLO's own bias |
|---|---|---|---|---|---|---|
| 0–10 | 58 | 1.8 | **1.7** | +1.6 | +1.5 | −1.5 |
| 11–50 | 378 | 8.5 | **6.8** | +2.9 | +0.4 | −11.4 |
| 51–100 | 301 | 28.9 | **22.7** | +8.5 | −0.8 | −33.2 |
| 101–500 | 625 | 116.7 | **93.7** | +42.3 | +5.6 | −122.3 |
| 501–1,000 | 126 | 550.9 | **425.6** | +364.3 | +121.8 | −486.9 |
| 1,001+ | 112 | 2,229.2 | **1,878.5** | +1,789.1 | +1,200.1 | −2,091.1 |

Error falls in every band. The systematic over-count of Experiment A, which grows with crowd size (+42 for 101–500, +364 for 501–1,000, +1,789 above 1,000), is removed up to 500 people (bias +5.6) and halved or better above (+122 and +1,200), pulled toward YOLO's own (much larger) under-count. Mean signed error over all images falls from **+172.8 to +95.8**; over-counts from 758 to 584, under-counts rise from 777 to 945 (exact: 65 → 71). The number of predictions above 10,000 is the same in both (6) and those of 5,000 or more fall from 20 to 18.

**By density class** (MAE / RMSE / mean bias)

| Density | n | Exp. A | Exp. B |
|---|---|---|---|
| Low (0) | 222 | 65.2 / 784.1 / +49.9 | 19.1 / 105.3 / +2.5 |
| Medium (1) | 315 | 49.8 / 217.2 / −1.6 | 50.6 / 220.4 / −15.1 |
| High (2) | 1063 | 351.7 / 1958.9 / +250.1 | 293.4 / 1512.8 / +148.2 |

The gains are on High (MAE −17%) and, nominally, Low — where the improvement (65.2 → 19.1) comes from a single image: 2740, labelled Low-density but with a true count of 2,842, answered 14,500 in A and 4,200 in B. Medium is unchanged and acquires a small negative bias.

**Mechanism: the YOLO count as a floor**

- Only 21 of 1600 B predictions (1.3%) exactly match the YOLO count, but 93.9% are at or above it; the typical answer is 1.64× the YOLO count. B's answer is closer to the YOLO count than A's in 63.9% of images; 1227 of the 1600 count predictions differ from A's.
- **When the YOLO count is at least 75% of the true count (404 images):** echo rate 5.0%, MAE falls from 31.1 (A) to 16.4 (B); YOLO itself has 12.4.
- **When it is below 25% of the true count (402 images):** echo rate 0.2%, MAE falls from 768.9 to 649.2 (YOLO's own: 728.7).
- **The 300 cap:** the YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300). On those images B has an MAE of 515.8 against 589.3 for A and 803.0 for YOLO; B answers above 300 in 97.0% of them and never echoes 300. They carry 21.0% of B's total absolute error. Consistent with a detection cap in the YOLO inference script (not verified).
- **Stock numbers:** the A favourite 230 (114 times) is replaced by 85 (68) and 45 (67); multiples of 10 rise from 53.2% to 56.9%.

---

## 4. Density: The YOLO Count Does Not Help

| Density | Recall — A | Recall — B |
|---|---|---|
| Low | 35.1% | **36.5%** |
| Medium | 78.1% | **79.4%** |
| High | **86.6%** | 84.0% |

Predicted-class shares: A — Low 5.0%, Medium 33.1%, High 61.9%; B — 5.4%, 34.8%, 59.9% (truth: 13.9% / 19.7% / 66.4%). Of the 96 changed labels, the most frequent is High → Medium (55 images; 141 High images were called Medium in A, 167 in B), followed by Medium → High (23). By true class: Low +9 / −6, Medium +12 / −8, **High +16 / −44** — the net loss is on High images that the YOLO line moves into the Medium bin, plausibly because the capped YOLO counts make crowded scenes look less crowded. Medium images called High fall from 68 to 63 and Low images called Medium from 142 to 139.

---

## 5. Worst-Case Examples

| test_filename | true | YOLO | A prediction | B prediction |
|---|---|---|---|---|
| 212 | 9,059 | 1 | 20,000 | **45,000** |
| 2203 | 4,622 | 201 | **45,000** | 25,000 |
| 3178 | 7,560 | 9 | 30,000 | 20,000 |
| 2070 | 6,073 | 9 | 12,500 | 18,500 |
| 1510 | 3,641 | 41 | 40,000 | 5,000 |
| 1343 | 3,428 | 26 | 6,500 | 12,000 |

The YOLO count repairs the two worst over-counts of A (1510 and 2203), but images with an absurdly low YOLO count (1–26: 212, 2070, 1343) are answered with even larger five-figure values in B. The 10 worst predictions' share of the total error is 37.8% in A and 34.3% in B. **Image 3411** (true 105; YOLO 110) is answered 85 in A and 105 in B; the 21,482 anomaly occurs in neither.

---

## 6. Reliability, Thinking and Cost

| | Experiment A | Experiment B |
|---|---|---|
| Responses `end_turn` / parsed (count and density) | 1600 / 1600 | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Requests with more than a bare answer (output > 15 tokens) | **0** | 5 (0.3%) |
| Mean output tokens / request | 13.1 | 13.8 |
| Mean input tokens / request | 425 | 464 |
| Cost at Batch prices ($1 / $5 per million tokens; verify) | ≈ $0.78 | ≈ $0.85 |

Reliability is perfect in both. Sonnet answers directly on every A request and on all but five B requests — small crowds (true count 7–14) on which it counted out loud, answering within 0–1 people of the truth on four of the five.

---

## 7. Against GPT-6.1 Terra and Claude Haiku 5.5, Zero-Shot Experiment B (Paired)

**GPT:** MAE 207.56 against 133.87; GPT's absolute error is lower on 824 images, Sonnet's on 666 (110 ties; Wilcoxon p = 5×10⁻⁶). On density the two are indistinguishable (Sonnet alone right on 178 images, GPT alone on 174; McNemar p = 0.87). GPT echoes the YOLO count more often (13.4% vs 1.3%) and overshoots far less when it rejects an implausible YOLO count.

**Haiku:** MAE 207.56 against 237.11 (RMSE 1237.58 vs 1384.49); Sonnet's absolute error is lower on 953 images, Haiku's on 519 (128 ties; Wilcoxon p = 4×10⁻²¹). On density Sonnet alone is right on 229 images and Haiku alone on 130 (McNemar p = 2×10⁻⁷); identical labels on 1199 of 1600. Haiku echoes the YOLO count in 14.1% of cases, Sonnet in 1.3%.

---

## 8. Zero-Shot B vs. 5-Shot B (Claude Sonnet)

| | Zero-shot B | 5-shot B |
|---|---|---|
| MAE / RMSE / MAPE | 207.56 / 1237.58 / **36.73%** | **141.44 / 458.14** / 65.76% |
| Density accuracy | 76.50% | 77.44% |
| Recall Low / Medium / High | 36.5 / **79.4** / 84.0 | **60.8** / 58.4 / 86.5 |
| Exact YOLO echo | 1.3% | 1.4% |
| Cost | ≈ $0.85 | ≈ $3.15 |

With the YOLO count in the prompt, the five examples reduce MAE by 32% and RMSE by 63%, but the typical image is unchanged (absolute error lower on 585 images in zero-shot, on 640 in 5-shot; 375 ties; Wilcoxon p = 0.14) and density accuracy does not differ significantly (130 images right only in zero-shot, 145 only in 5-shot; p = 0.40). Zero-shot has the much lower MAPE (36.7% vs 65.8%, the latter inflated by one image) and costs a quarter as much. The difference in the density profile is the same as in Experiment A: examples buy Low recall (36.5% → 60.8%) at the cost of Medium recall (79.4% → 58.4%).

---

## 9. Interpretation

For Claude Sonnet 5.5 the YOLO count is a **modest scale correction that works on counting but not on density**. It removes the systematic over-count on scenes of up to 500 people, cuts the mean error by 18% and lifts MAPE below that of every other model, but cannot repair the dense scenes on which the YOLO count itself is nearly zero: there the model rejects the number and overshoots by an order of magnitude, which keeps RMSE (1237.58) well above YOLO's and GPT's. Density accuracy slips by 1.3 points — a small but, in a paired test, marginally significant decline concentrated on High images pulled into the Medium class. Compared with the other models, Sonnet's relative gain from the number is the smallest, because its unaided estimates were already good for typical crowds; the practical contrast with GPT-6.1 Terra — same prompts, same use of the number as a floor — is calibration: GPT's revisions land close to the truth, Sonnet's sometimes at 12,000–45,000.

---

## 10. Limitations

- Each condition is a single non-deterministic run; variance was not measured, so the 1.3-point density decline (McNemar p = 0.040) should be read with the model's own sampling noise in mind.
- Only effort `medium` was tested; thinking is practically absent at that setting.
- The subset analyses use the ground truth (or the model's own outputs) to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 11. Status

Zero-shot experiments A and B and 5-shot experiments A and B are complete for Claude Sonnet 5.5. The zero-shot density-definition experiments have not yet been run for this model.
