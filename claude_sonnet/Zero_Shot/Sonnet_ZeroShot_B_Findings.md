# Claude Sonnet 5.5 — Zero-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. Same zero-shot prompt as Experiment A, with one addition: a two-line statement giving the YOLO-predicted count for the test image (identical wording to the other models' zero-shot Experiment B). `claude-sonnet-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium** (set explicitly; the model's default is `high`), 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 207.56 |
| RMSE | 1237.58 |
| MAPE | 36.73% |
| Valid predictions | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 76.50% |
| Precision | 83.85% |
| Recall | 76.50% |
| F1-score | 77.31% |
| Valid predictions | 1600 / 1600 |

**Correlation:** Pearson r = 0.767, Spearman ρ = 0.945.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): B beats it on MAE (−14%) and MAPE (36.73% vs 50.64%) but **not on RMSE** (1237.58). In a paired comparison of absolute error B is closer to the truth than YOLO on **1267 images**, YOLO on 296 (37 ties; Wilcoxon p = 7×10⁻¹¹²). Against Experiment A (MAE 252.51) counting error is 17.8% lower; the full comparison is in `Sonnet_ZeroShot_A_vs_B_Comparison.md`.

**Against the other zero-shot Experiment B runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Exact YOLO echo |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 262.36 | 922.89 | 67.82% | 65.8% | 55.7% | 0.294 | 0.772 | 46.2% |
| LLaVA-Interleave-0.5B | 233.86 | 679.08 | 53.29% | 14.6% | 4.7% | 0.420 | 0.747 | 95.8% |
| Gemma 3 (4B) | 234.54 | 882.49 | 56.67% | 64.7% | 63.3% | 0.192 | 0.835 | 1.3% |
| GPT-6.1 Terra | **133.87** | **490.77** | 45.64% | 76.25% | 72.77% | **0.805** | 0.944 | 13.4% |
| Claude Haiku 5.5 | 237.11 | 1384.49 | 43.01% | 70.31% | 65.97% | 0.590 | 0.899 | 14.1% |
| **Claude Sonnet 5.5** | 207.56 | 1237.58 | **36.73%** | **76.50%** | **77.31%** | 0.767 | **0.945** | 1.3% |

Sonnet has the **best MAPE, density accuracy, density F1 and Spearman correlation** of the six models in this condition, and the second-best MAE and Pearson correlation, behind GPT-6.1 Terra. Its RMSE, however, is worse than that of GPT and of every open model except Haiku's: six predictions above 10,000 remain (Section 6). Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture and serving, and from GPT in running without visible thinking (Section 7); the experiment cannot attribute differences to any single factor.

---

## 2. Response Reliability: Perfect, With Five Deviations

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count and density parsed | 1600 / 1600 each |

1595 responses are exactly `Count: <n>` and `Density: <d>`. **Five responses (0.3%) begin with a visible, one-by-one count of the people in the picture** (up to 972 characters) before ending with the two required lines; all parse correctly. All five are small crowds (true count 7–14, YOLO count 6–23) and the answers are within 0–1 people of the truth on four of them and +7 on the fifth (MAE 1.6). Experiment A produced no such response; as in the 5-shot runs, the YOLO line seems to be what triggers this occasional counting out loud (Section 7).

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of 1600 | MAE | Bias |
|---|---|---|---|---|
| Echoes the YOLO count exactly | 21 | 1.3% | 9.0 | −8.9 |
| Within 10% of YOLO, not exact | 277 | 17.3% | 40.0 | — |
| More than 10% **above** YOLO | 1272 | 79.5% | 250.2 | +130.9 |
| More than 10% **below** YOLO | 30 | 1.9% | 85.7 | — |

**Sonnet uses the YOLO count as a floor, not as an answer.** 1503 of 1600 predictions (93.9%) are at or above it, the typical answer is **1.64× the YOLO count** (median ratio; quartiles 1.13× and 3.87×), and only 1.3% are exact echoes — the same as Gemma's 1.3% and far below Haiku (14.1%), GPT (13.4%), Qwen (46.2%) and LLaVA (95.8%). Echoes occur on easy scenes (8.6% of Low-density images, 0.6% of Medium, none of High). B's answer is closer to the YOLO count than A's in 63.9% of images; 1227 of the 1600 count predictions (77%) differ from A's.

**The 300 cap.** The YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300, median 759). This is consistent with a detection cap in the YOLO inference script (not verified). Sonnet answers above 300 in 97.0% of these cases and never echoes 300; MAE on them is 515.8 for B, 589.3 for A and 803.0 for YOLO, against 179.2 / 221.5 / 190.2 on the other 1,465 images (where YOLO is slightly better than B). The saturated images carry 21.0% of B's total absolute error.

**Zero YOLO counts.** On the 26 images with a YOLO count of zero the median answer is 46 (maximum 4,200), MAE 426.2.

| Subset | n | Echo rate | MAE — B | MAE — A | MAE — YOLO |
|---|---|---|---|---|---|
| YOLO ≥ 75% of the true count | 404 | 5.0% | 16.4 | 31.1 | 12.4 |
| YOLO < 25% of the true count | 402 | 0.2% | 649.2 | 768.9 | 728.7 |

When YOLO is close, Sonnet moves toward it (MAE 31.1 → 16.4) but stays above YOLO's own 12.4. When YOLO is far too low, MAE falls by 16% (768.9 → 649.2) and ends below YOLO's own level (728.7), but the error stays large.

---

## 4. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 19.1 | 105.3 | +2.5 |
| Medium (1) | 315 | 50.6 | 220.4 | −15.1 |
| High (2) | 1063 | 293.4 | 1512.8 | +148.2 |

By ground-truth count — MAE / mean bias: 0–10: 1.7 / +1.5; 11–50: 6.8 / +0.4; 51–100: 22.7 / −0.8; 101–500: 93.7 / +5.6; 501–1,000: 425.6 / +121.8; above 1,000: 1,878.5 / +1,200.1. The bias is practically zero up to 500 people. Predictions lean slightly low in count (584 over-counts, 945 under-counts, 71 exact), but the mean signed error is +95.8 because of the large over-counts at the top; the median absolute error is 22.0 and 25.1% of predictions are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 207.56 to 151.94; the 10 worst account for 34.3% of the total absolute error.

**Density classification**

| Density | Recall |
|---|---|
| Low | 36.5% (81 / 222) |
| Medium | **79.4%** (250 / 315) |
| High | 84.0% (893 / 1063) |

Confusion matrix (rows = truth, columns = prediction): Low [81, 139, 2]; Medium [2, 250, 63]; High [3, 167, 893]. Accuracy of 76.50% (1224 / 1600) is far above the always-"High" baseline of 66.44% (binomial p = 1×10⁻¹⁸). Predicted shares are Low 5.4%, Medium 34.8%, High 59.9% (truth: 13.9% / 19.7% / 66.4%): as in A, the model over-uses Medium (139 of 222 Low images and 167 of 1063 High images are called Medium) instead of defaulting to High as GPT and Haiku do; 204 predictions are denser than the truth and 172 sparser.

---

## 5. Correlation With Ground Truth

- **Pearson r = 0.767**
- **Spearman ρ = 0.945**

Both are above Experiment A's (0.685 / 0.938): with the YOLO count the linear fit improves markedly (the over-counts are smaller), while the ranking of scenes is almost unchanged. Spearman is the highest of the six models in this condition (GPT: 0.944); Pearson is second to GPT's 0.805 and well above every open model (best: LLaVA 0.420) and Haiku (0.590).

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | error |
|---|---|---|---|---|
| 212 | 9,059 | **45,000** | 1 | +35,941 |
| 2203 | 4,622 | 25,000 | 201 | +20,378 |
| 3178 | 7,560 | 20,000 | 9 | +12,440 |
| 2070 | 6,073 | 18,500 | 9 | +12,427 |
| 1343 | 3,428 | 12,000 | 26 | +8,572 |
| 4159 | 6,210 | 12,000 | 55 | +5,790 |

Six predictions exceed 10,000 (as in Experiment A) and together account for **28.8%** of the total absolute error; without them MAE would be 148.40 (descriptive only: the group is defined by the model's own outputs). In four of the six the YOLO count is absurdly low (1–55) and the model, rejecting it, overshoots by a large factor. The maximum prediction is 45,000 (image 212; A: 20,000).

**Same hard images, A vs. B:** the YOLO count removes the worst over-count of A on image 1510 (40,000 → 5,000) and halves it on 2203 (45,000 → 25,000) and 3178 (30,000 → 20,000), but makes 212 worse (20,000 → 45,000, YOLO count 1) and 1343 worse (6,500 → 12,000, YOLO 26); image 814 (true 8,994, YOLO 6) is answered 6,000 in both. **Test image 3411 (true 105; YOLO 110)** — the source of the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **105**, exactly the true count (A: 85); the anomaly does not reproduce.

**Stock answers.** The most frequent predictions are 85 (68 times), 45 (67), 120 (62), 230 (60), 150 (56), 38 (53), 60 (51) and 420 (46); 56.9% of predictions are multiples of 10 (A: 53.2%; truth 10.4%) and 9.1% multiples of 100 (A: 7.6%; truth 0.9%); of the 129 predictions of 1,000 or more, 107 are multiples of 100.

---

## 7. Reasoning and Cost

| Quantity | Value |
|---|---|
| Requests with more than a bare answer (output > 15 tokens) | **5 of 1600 (0.3%)** (A: 0) |
| Mean / median / max output tokens | 13.8 / 13 / 346 |
| Mean input tokens / request | 464 |
| Total input / output tokens | 741,727 / 22,095 |
| Cost at Batch prices ($1 / $5 per 1M tokens; Anthropic's published rates, to be verified) | ≈ **$0.85** (A: $0.78) |

As in A, Sonnet answers directly on essentially every request. The five exceptions are the small-crowd images described in Section 2: their MAE is 1.6 against 208.2 for the rest, and their density accuracy 60% against 76.6%. Claude Haiku 5.5, by contrast, produced extended output on 96.0% of its zero-shot B requests (mean 244 tokens).

---

## 8. Interpretation

With the YOLO count, Claude Sonnet 5.5 improves on its own zero-shot A on every counting metric (MAE −17.8%, RMSE −23.9%, MAPE −19.3%) and becomes the best model of the study in this condition on MAPE, density accuracy, density F1 and Spearman correlation — while still trailing GPT-6.1 Terra clearly on MAE and RMSE because the model, on a few dense scenes whose YOLO count is implausibly low, rejects the number and overshoots to 12,000–45,000. It never copies the number (1.3% echoes) and uses it as a floor, which gives a near-zero bias up to 500 people. Density classification is not improved by the count — it is slightly worse than in A — and keeps the same distinctive profile: the best Medium recall of any model (79.4%), modest Low recall (36.5%) and a tendency to over-use the Medium label. The remaining question for this model is whether a written definition of the density classes helps the Low class, which the density-definition experiments will show.

---

## 9. Limitations

- One run, not deterministic; run-to-run variation was not measured, so small differences (e.g. density accuracy against GPT, or A against B) are not meaningful.
- The tail analysis defines groups from the model's own outputs and is descriptive.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- Only effort `medium` was tested; thinking is practically absent at that setting.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Zero-shot experiments A and B are complete for Claude Sonnet 5.5 (comparison: `Sonnet_ZeroShot_A_vs_B_Comparison.md`), as are the 5-shot experiments (see `../Five_Shot/`). The density-definition experiments have not yet been run for this model.
