# Claude Sonnet 5.5 — 5-Shot Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image + the YOLO-predicted count per prediction). The prompt is the 5-shot Experiment A prompt plus one line giving the YOLO count (identical wording to the other models' 5-shot B prompts). `claude-sonnet-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium** (set explicitly; the model's default is `high`), 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run. The comparison with Experiment A is in `Sonnet_A_vs_B_Comparison.md`.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 141.44 |
| RMSE | 458.14 |
| MAPE | 65.76% |
| n (valid) | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 77.44% |
| Precision | 79.34% |
| Recall | 77.44% |
| F1-score | 78.05% |

**Correlation:** Pearson r = 0.793, Spearman ρ = 0.941.

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): B beats it on MAE (−41%) and RMSE (−38%) but not on MAPE; in a paired comparison of absolute error B is closer to the truth on **1249 images**, YOLO on 314 (37 ties; Wilcoxon p = 7×10⁻¹¹³). The MAPE is inflated by one image (Section 6): without it, MAPE would be 34.5%.

**Against the other models' 5-shot Experiment B runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Exact YOLO echo |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 259.16 | 884.06 | 133.52% | 57.9% | 58.7% | 0.112 | 0.645 | 64.6% |
| LLaVA-Interleave-0.5B | 321.11 | 784.55 | 524.81% | 37.8% | 41.4% | 0.070 | 0.402 | 62.4% |
| Gemma 3 (4B) | 240.83 | 881.38 | 89.76% | 66.4% | 62.2% | 0.107 | 0.761 | 1.1% |
| GPT-6.1 Terra | **138.11** | 494.14 | **29.97%** | **77.8%** | 77.5% | 0.753 | 0.936 | 17.7% |
| Claude Haiku 5.5 | 220.92 | 1100.55 | 44.26% | 71.3% | 72.4% | 0.541 | 0.879 | 11.5% |
| **Claude Sonnet 5.5** | 141.44 | **458.14** | 65.76% | 77.4% | **78.1%** | **0.793** | **0.941** | 1.4% |

Sonnet is first on RMSE, density F1, Pearson and Spearman, and a close second on MAE and density accuracy (differences of 3.3 in MAE and 0.4 points of accuracy against GPT). It is far behind GPT on MAPE (65.8% vs 30.0%). Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture and serving, and from GPT in running almost without thinking (Section 7).

---

## 2. Response Reliability: Perfect, With Nine Deviations

| Check | Result |
|---|---|
| Responses with stop reason `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count and density parsed | 1600 / 1600 each |

1591 responses are exactly `Count: <n>` and `Density: <d>`. **Nine responses (0.6%) begin with a visible one-by-one count of the people in the picture** (up to 658 characters) before ending with the two required lines; all parse correctly. They are the only responses of the 5-shot A *or* B run with any thinking-like output (Experiment A: none). All nine are small crowds (true count 7–17; YOLO count 6–23): the model counted them out, and its answers are within 0–2 people of the truth on eight of the nine (MAE 1.7). See Section 7.

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of 1600 | MAE |
|---|---|---|---|
| Echoes the YOLO count exactly | 23 | 1.4% | 0.6 |
| Within 10% of YOLO, not exact | 215 | 13.4% | 50.0 |
| More than 10% **above** YOLO | 1334 | 83.4% | 160.6 |
| More than 10% **below** YOLO | 28 | 1.8% | 45.9 |

**Sonnet almost never copies the YOLO count** (1.4% exact echoes — Haiku 11.5%, GPT 17.7%, Qwen 64.6%, LLaVA 62.4%) but uses it as a floor: 95.6% of answers are at or above it, and the typical answer is **1.69× the YOLO count** (median ratio; quartiles 1.18× and 4.0×). Echoes occur on easy scenes (9.0% of Low-density images, 0.6% of Medium, 0.1% of High). B's answer is closer to the YOLO count than A's in 70% of images; 1328 of the 1600 count predictions (83%) differ from A's.

**The 300 cap.** The YOLO counts never exceed 300 (135 images at exactly 300, 99.3% with a true count above 300, median 759). This is consistent with a detection cap in the YOLO inference script (not verified). Sonnet answers above 300 in 95.6% of these cases and never echoes 300; MAE is 412.6 for B, 437.5 for A and 803.0 for YOLO itself, while on the other 1,465 images the figures are 116.4 / 123.5 / 190.2. The saturated images carry 24.6% of B's total absolute error.

**Zero YOLO counts.** On the 26 images with a YOLO count of zero the median answer is 43.5 (maximum 6,200), MAE 414.7.

| Subset | n | Echo rate | MAE — B | MAE — A | MAE — YOLO |
|---|---|---|---|---|---|
| YOLO ≥ 75% of the true count | 404 | 5.7% | 18.2 | 29.0 | 12.4 |
| YOLO < 25% of the true count | 402 | 0.0% | 394.3 | 392.2 | 728.7 |

When YOLO is close, Sonnet moves toward it (MAE 29.0 → 18.2, still above YOLO's own 12.4). When YOLO is far too low, Sonnet **does not use it at all** — MAE is the same with and without the number (394.3 vs 392.2), roughly half of YOLO's 728.7: its own estimate of these dense scenes was already better than the detector's.

---

## 4. Density: Unchanged by the YOLO Count

| Density | n | Recall |
|---|---|---|
| Low | 222 | 60.8% (135) |
| Medium | 315 | 58.4% (184) |
| High | 1063 | 86.5% (920) |

Confusion matrix (rows = truth, columns = prediction): Low [135, 80, 7]; Medium [22, 184, 109]; High [10, 133, 920]. Predicted shares are Low 10.4%, Medium 24.8%, High 64.8% (truth: 13.9% / 19.7% / 66.4%). Accuracy of 77.44% (1239 / 1600) is far above the always-"High" baseline of 66.44% (binomial p = 4×10⁻²²); 196 predictions are denser than the truth and 165 sparser. As in A, Low and Medium recall are the best of any model, and High recall (86.5%) the lowest of the closed models.

---

## 5. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 16.9 | 84.4 | −9.1 |
| Medium (1) | 315 | 44.8 | 116.0 | −29.6 |
| High (2) | 1063 | 196.1 | 557.2 | −18.0 |

By ground-truth count — MAE / mean bias: 0–10: 44.7 / +44.5; 11–50: 7.5 / +2.3; 51–100: 25.7 / +6.0; 101–500: 85.6 / +1.8; 501–1,000: 369.7 / +10.3; above 1,000: 1,009.5 / −340.7. Predictions lean slightly low (603 over-counts, 913 under-counts, 84 exact; mean signed error −19.1), the median absolute error is 22.0 and 27.6% of predictions are within ±10% of the truth (GPT 5-shot A: 27.2%). Removing the 5 worst predictions lowers MAE from 141.44 to 126.27; the 10 worst account for 17.9% of the total absolute error. The 0–10 band's MAE of 44.7 is a single image (2269, below): its median absolute error is 0.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | error |
|---|---|---|---|---|
| 814 | 8,994 | 1,200 | 6 | −7,794 |
| 4304 | 839 | 6,200 | 0 | +5,361 |
| 2203 | 4,622 | 9,000 | 201 | +4,378 |
| 3539 | 6,757 | 2,850 | 300 | −3,907 |
| 4056 | 6,660 | 3,200 | 10 | −3,460 |
| 3178 | 7,560 | 4,200 | 9 | −3,360 |
| 2269 | 5 | **2,500** | 1 | +2,495 |

Two of the over-counts, images 4304 and 2269, are scenes with a YOLO count of 0 or 1 where the model rejects the number and then answers with a large figure. Image 2269 (true count 5) is the biggest outlier in proportional terms: it alone adds 31 points to MAPE (65.76% → 34.5% without it); in Experiment A it was answered 1,500. The largest errors in absolute terms are under-counts of very large crowds. Only **one** prediction exceeds 10,000 (image 212: 12,000 for a true 9,059, YOLO count 1; in A: 14,500); the maximum prediction in the run is 12,000.

**Test image 3411 (true 105; YOLO 110)** — the source of the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered **118** (A: 112); the anomaly does not reproduce.

**Stock answers.** The most frequent values are 45 (70 times), 150 (65), 120 and 85 (58 each), 230 and 420 (55 each). 51.4% of predictions are multiples of 10 (truth: 10.4%) and 6.0% multiples of 100 (truth 0.9%; Haiku B: 5.2%); of the 117 predictions of 1,000 or more, 63 are multiples of 100. 18 predictions (1.1%) equal one of the five support counts.

---

## 7. Reasoning and Cost

| Quantity | Value |
|---|---|
| Requests with more than a bare answer (output > 15 tokens) | **9 of 1600 (0.6%)** (A: 0) |
| Mean / median / max output tokens | 14.1 / 13 / 281 |
| Mean input tokens / request | 1,897 |
| Total input / output tokens | 3,034,551 / 22,509 |
| Cost at Batch prices ($1 / $5 per 1M tokens; Anthropic's published rates, to be verified) | ≈ **$3.15** (A: $3.08) |

At medium effort Sonnet answers directly on 99.4% of requests, as in A. The nine exceptions are the small-crowd images described in Section 2: on 402 images with a YOLO count of 17 or less only nine triggered counting out loud, and the YOLO line is the only difference from A, where none did. Their MAE is 1.7 against 142.2 for the rest; their density accuracy (55.6%) is lower, as the labels on small scenes are hard to predict (several are labelled Low but called Medium).

---

## 8. Interpretation

With the YOLO count Claude Sonnet 5.5 keeps what it already did well without it and adds a small gain: it uses the number as a lower bound, never copies it (1.4% echoes), takes it into account where it is close to the truth (MAE on those images 29.0 → 18.2) and ignores it where it is far too low — the opposite of the copy strategy of Qwen and LLaVA. The result is the best RMSE of any model (458.14), the best density F1 and correlations, and a MAE within 2.4% of GPT-6.1 Terra's, at one answer line per request. The one metric on which it lags GPT clearly is MAPE (65.8% vs 30.0%), and it is a one-image problem (2269) plus a slight bias on very small scenes. The YOLO count does not change density classification. Compared with Claude Haiku 5.5, which gained a third of its MAE from the same line, the benefit for Sonnet is small (−5.7%) because its examples-only answers were already close to the truth (see `Sonnet_A_vs_B_Comparison.md`).

---

## 9. Limitations

- One run, not deterministic; run-to-run variation was not measured, so small differences (e.g. against GPT) are not meaningful.
- Only effort `medium` was tested; at that setting thinking is practically absent.
- The subset analyses use the ground truth to define groups; they describe behaviour and do not show an explicit rule.
- The 300-count wall in the YOLO input is described from the data; its cause has not been verified in the inference script.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

5-shot experiments A and B are complete for Claude Sonnet 5.5. The zero-shot and density-definition conditions have not yet been run.
