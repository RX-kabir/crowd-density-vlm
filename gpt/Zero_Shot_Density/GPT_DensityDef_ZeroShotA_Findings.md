# GPT-6.1 Terra — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples and no YOLO count. The system prompt is the zero-shot prompt with one change: the bare density labels (`0 = Low, 1 = Medium, 2 = High`) are replaced by an explicit visual definition of each class ("judge by how visually packed the crowd appears, not by exact count"; Low = people clearly separated; Medium = moderately close, some overlap but gaps and open space still visible; High = tightly packed, little or no visible space). Identical wording to the Qwen, LLaVA and Gemma density-definition experiments. `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, 512 px images, Batch API. `temperature` is not settable in reasoning mode, so this is a single non-deterministic run (see Section 4 for why that matters for this particular test).

The comparison baseline throughout is GPT's own zero-shot Experiment A with the original bare-label prompt (`GPT_ZeroShot_A_Findings.md`).

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | 198.45 | **169.95** |
| RMSE | 773.75 | **607.96** |
| MAPE | 54.86% | 55.27% |
| Density accuracy | 75.19% | **78.88%** |
| Density precision | 73.50% | 80.49% |
| Density recall | 75.19% | 78.88% |
| Density F1 | 71.00% | **76.68%** |
| Pearson r / Spearman ρ | 0.869 / 0.961 | 0.877 / 0.959 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

The new prompt gives the **highest density accuracy of any GPT condition so far** (78.88%, against 77.81% for both 5-shot runs) and the highest zero-shot F1; its F1 (76.68%) is just below the 5-shot runs' (77.25% and 77.52%). It reaches this without any support example.

**Against the other models' density-definition Experiment A runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 66.75% | 68.00% | small, significant improvement (McNemar p = 0.0008) |
| LLaVA-Interleave-0.5B | 12.71% | 14.52% | not comparable (reliability fell 38.6% → 22.6%) |
| Gemma 3 (4B) | 64.69% | 42.50% | severe, highly significant decline |
| **GPT-6.1 Terra** | **75.19%** | **78.88%** | **moderate, significant improvement (McNemar p = 1.9×10⁻⁵)** |

GPT is the second model, after Qwen, for which the definition helps, and the improvement is larger in absolute terms (+3.7 points vs +1.3). Caveat: GPT-6.1 Terra differs from the open models in scale, architecture, API serving **and** in running with medium-effort reasoning enabled, and — unlike the open-source runs — it is not deterministic.

---

## 2. Response Reliability: Perfect, Unchanged

| Check | Result |
|---|---|
| Responses with status `completed` | 1600 / 1600 |
| Truncated / incomplete responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 23 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1595 with a single line break, 5 with a blank line). The longer prompt does not affect format compliance — the opposite of LLaVA, whose already-poor reliability fell by almost half under the same text.

---

## 3. Density Classification: A Real Improvement, Concentrated in the Medium Class

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | **33.3%** (74) | 26.6% (59) |
| Medium | 315 | 22.2% (70) | **54.3%** (171) |
| High | 1063 | **99.6%** (1059) | 97.1% (1032) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 59 | 137 | 26 |
| **True Medium** | 2 | 171 | 142 |
| **True High** | 0 | 31 | 1032 |

Predicted-class shares: Low 3.8%, Medium 21.2%, High 75.0% (old prompt: 4.8% / 11.6% / 83.6%; truth: 13.9% / 19.7% / 66.4%). The Medium share of predictions is now almost exactly the true Medium share (21.2% vs 19.7%), and the over-prediction of "High" is cut by about half (83.6% → 75.0% against a truth of 66.4%).

The accuracy of 78.88% (1262 / 1600) is far above the always-"High" baseline of 66.44% (one-sided binomial p ≈ 4×10⁻²⁸).

**Tracking individual images.** 214 density predictions changed between the two prompts: **123 images flipped from an incorrect to a correct density, while 64 flipped the other way** (McNemar's exact test p = 1.9×10⁻⁵). The flips split by true class as follows:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | 14 | 29 |
| Medium | **107** | 6 |
| High | 2 | 29 |

So the net gain is entirely on Medium images (+107 / −6), partly paid for by losses on Low (−29 / +14) and High (−29 / +2). The most common change of label is High → Medium (153 images), followed by Low → Medium (29); the model now reads moderately packed scenes as Medium rather than defaulting to High, but it also pulls a few genuinely Low and High images into the Medium bin. The new Medium wording ("some overlap … but gaps and open space still visible") appears to be matched too eagerly: of the 163 Low images that are misclassified, 137 are now called Medium and only 26 High.

The remaining weakness is unchanged in kind: 142 of 315 Medium images (45%) are still called High, and 137 of 222 Low images (62%) are called Medium. The model still almost never calls a scene sparser than the truth (33 images; 305 are called denser).

**Compared with the 5-shot run** (same model): the definition gets zero-shot to the same overall accuracy (78.88% vs 77.81%) and a similar F1 (76.68% vs 77.25%), but through a different profile — better Medium and High recall than 5-shot A (54.3% vs 44.4%; 97.1% vs 91.3%) and much worse Low recall (26.6% vs 60.4%). Labelled examples teach the sparse end of the scale better than a written definition does.

---

## 4. Counting: Changed Too — With a Caveat That Matters

Only the density-label section of the prompt changed, so no mechanistic effect on counting would be expected, as in the open-source runs (Qwen: MAE 725.92 → 694.18, p = 0.345; not significant). Here, however, counting error also falls: **MAE 198.45 → 169.95 and RMSE 773.75 → 607.96** (paired Wilcoxon p = 8.1×10⁻⁴, paired t-test p = 1.7×10⁻³; the new prompt has the lower absolute error on 782 images, the old on 660, 158 ties). The mean signed error drops from +162.5 to +129.8 (still an over-count), and the improvement sits on dense scenes: bias above 1,000 people falls from +1,308 to +899. MAPE is unchanged (54.86% → 55.27%).

**Why this cannot be read as an effect of the prompt text alone.** The open-source runs used greedy decoding, so any difference between two prompts is attributable to the prompt. GPT in reasoning mode is not deterministic, and no repeat run of the *old* prompt was made, so run-to-run variation is unmeasured. The count prediction differs between the two runs on 1450 of 1600 images (90.6%), though the two sets of predictions are almost perfectly rank-correlated (Spearman ρ = 0.993). Part or all of the counting change — and, in principle, part of the density change — could therefore be run-to-run variation rather than an effect of the definition. The density result is much less likely to be noise than the counting result, because it is directional and concentrated in the one class (Medium) that the definition describes, but the McNemar p-value does not account for the model's own non-determinism. A repeat of the old-prompt run (or of this one) would quantify it.

---

## 5. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 15.2 | 97.2 | −8.8 |
| Medium (1) | 315 | 36.7 | 75.1 | +9.6 |
| High (2) | 1063 | 241.8 | 743.4 | +194.3 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)* Old-prompt MAE on the same strata: Low 11.5, Medium 40.6, High 284.3. The shape is the same as before: small errors on sparse and moderate scenes, and an over-count concentrated on the High stratum.

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 18.6 | +18.3 |
| 11–50 | 378 | 10.4 | +6.4 |
| 51–100 | 301 | 33.2 | +26.1 |
| 101–500 | 625 | 107.6 | +90.2 |
| 501–1,000 | 126 | 399.0 | +311.5 |
| 1,001+ | 112 | 1,244.6 | +898.9 |

Across all images, 1063 are over-counted, 448 under-counted and 89 exact; the median absolute error is 30.0 and 26.3% of predictions are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 169.95 to 148.32.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 4159 | 6,210 | 14,567 | 8,357 |
| 2203 | 4,622 | 12,000 | 7,378 |
| 1343 | 3,428 | 10,284 | 6,856 |
| 3178 | 7,560 | 14,268 | 6,708 |
| 3697 | 2,447 | 8,500 | 6,053 |
| 2354 | 1,019 | 6,247 | 5,228 |

All six are over-counts, as in the old-prompt run. The largest prediction is 14,567 (old prompt: 19,847); five predictions exceed 10,000 (old: 8); there are no 50,000 or 75,000 style placeholder values. **Test image 3411 (true count 105)**, which produced the identical value 21,482 in eight Qwen and Gemma conditions (and a ninth, in Qwen's own density-definition run), is answered **152**; the anomaly does not reproduce, as in every other GPT condition. Images that triggered extreme hallucinations in other models remain well handled (4056: 6,814 for a true 6,660; 3334: 1,017 for a true 1,026; 212: 8,432 for a true 9,059).

---

## 7. Reasoning Effort and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Mean input tokens / request | 317 | 396 |
| Mean output tokens / request | 662 | 711 (of which reasoning: 696; median 613) |
| Longest output | 2,942 | 2,981 tokens |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported) | ≈ $2.90 | ≈ **$3.16** |

The model reasons somewhat longer with the definition (696 vs 646 tokens; paired Wilcoxon p ≈ 4×10⁻¹⁵), consistent with having more to weigh. As before, reasoning length correlates negatively with the true count (ρ = −0.18) and with absolute error (ρ = −0.26), and is highest on Medium-density images (mean 857 tokens vs 589 for Low and 670 for High) — and, by predicted class, on images the model labels Medium (739).

---

## 8. Interpretation

The density definition helps GPT-6.1 Terra: density accuracy rises from 75.19% to 78.88% and F1 from 71.00% to 76.68%, with no loss of format reliability, and the improvement is statistically real on the paired test (123 images fixed vs 64 broken). It operates almost entirely on the Medium class (recall 22.2% → 54.3%), which is exactly the class the written definition describes most concretely, and at a cost on the Low class (33.3% → 26.6%) and a small cost on High (99.6% → 97.1%). The model's predicted class mix moves from 83.6% "High" to 75.0%, much closer to the true 66.4%. This makes GPT a **fourth distinct outcome** in the project's density-definition study: Qwen — a small genuine gain; LLaVA — a reliability backfire; Gemma — a severe decline from overriding a good implicit judgment; GPT — a moderate gain that largely repairs the Medium class, because the model's earlier calibration (a boundary placed too low, with 77% of Medium images called High) was poor enough that a written rule helped rather than interfered.

Two qualifications. First, the sparse end of the scale is not fixed by definition: Low recall is still only 26.6%, well below the 60.4% that five labelled examples achieve. Second, the counting shift that accompanies the density result should not be attributed to the prompt (Section 4), and the density result itself would be firmer with a measurement of the model's own run-to-run variation.

---

## 9. Limitations

- Single, non-deterministic run (no temperature control in reasoning mode), compared against a single old-prompt run; run-to-run variance was not measured, so neither the density nor the counting difference can be fully separated from noise.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning; the comparison cannot attribute differences to any single factor.
- Token prices are third-party-reported and should be checked against OpenAI's pricing page.

---

## 10. Status

Density-definition Experiment A is complete for GPT-6.1 Terra. Experiment B is also complete — see `GPT_DensityDef_ZeroShotB_Findings.md`. The remaining step is to add GPT as a fourth model to the cross-model density-definition synthesis and the final comparison.
