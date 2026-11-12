# GPT-6.1 Terra — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. The prompt is the zero-shot Experiment B prompt (YOLO-predicted count given for the test image) with the same single change as in Experiment A: the bare density labels are replaced by an explicit visual definition of Low / Medium / High ("judge by how visually packed the crowd appears, not by exact count"). Wording identical to the Qwen, LLaVA and Gemma density-definition experiments. `gpt-6.1-terra`, OpenAI Responses API, reasoning effort **medium**, 512 px images, Batch API. `temperature` is not settable in reasoning mode, so this is a single non-deterministic run (see Section 5).

The comparison baseline is GPT's own zero-shot Experiment B with the original bare-label prompt (`GPT_ZeroShot_B_Findings.md`). The matching test without the YOLO count is in `GPT_DensityDef_ZeroShotA_Findings.md`.

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | **133.87** | 137.52 |
| RMSE | **490.77** | 558.98 |
| MAPE | 45.64% | **36.19%** |
| Density accuracy | 76.25% | **79.69%** |
| Density precision | 75.62% | 81.09% |
| Density recall | 76.25% | 79.69% |
| Density F1 | 72.77% | **77.73%** |
| Pearson r / Spearman ρ | 0.805 / 0.944 | 0.766 / 0.940 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

Density classification improves; counting error is essentially unchanged (MAE and RMSE a little worse, MAPE better; Section 3). With 79.69%, this is the **highest density accuracy of any of the six GPT conditions** (next best: 78.88% for density-definition Experiment A; 5-shot A and B: 77.81%).

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): the new-prompt Experiment B beats it on all three metrics, as the old-prompt B did.

**Against the other models' density-definition Experiment B runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 65.81% | 66.69% | not significant (McNemar p = 0.098) |
| LLaVA-Interleave-0.5B | 14.56% | 14.20% | small, significant decline (p = 0.031) |
| Gemma 3 (4B) | 64.69% | 37.44% | severe, highly significant decline |
| **GPT-6.1 Terra** | **76.25%** | **79.69%** | **significant improvement (McNemar p = 9.2×10⁻⁵)** |

GPT is the only model for which the definition helps in *both* experiments with statistical support (Qwen's gain was significant only in A). Caveat: GPT-6.1 Terra differs from the open models in scale, architecture, API serving **and** in running with medium-effort reasoning enabled, and — unlike the open-source runs — it is not deterministic.

---

## 2. Density Classification: Same Pattern as Experiment A — a Large Gain on Medium

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | **33.8%** (75) | 29.3% (65) |
| Medium | 315 | 28.6% (90) | **56.5%** (178) |
| High | 1063 | **99.3%** (1055) | 97.1% (1032) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 65 | 131 | 26 |
| **True Medium** | 3 | 178 | 134 |
| **True High** | 0 | 31 | 1032 |

Predicted-class shares: Low 4.2%, Medium 21.2%, High 74.5% (old prompt: 4.7% / 13.4% / 81.9%; truth: 13.9% / 19.7% / 66.4%). Accuracy of 79.69% (1275 / 1600) is far above the always-"High" baseline of 66.44% (binomial p ≈ 8×10⁻³²).

**Image-level tracking.** 222 density predictions changed between the two prompts: **124 images flipped from wrong to right and 69 from right to wrong** (McNemar's exact test p = 9.2×10⁻⁵). By true class:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | 19 | 29 |
| Medium | **101** | 13 |
| High | 4 | 27 |

As in Experiment A, the whole gain is on Medium images (+101 / −13), paid for by small losses on Low (−29 / +19) and High (−27 / +4). The most frequent label change is again High → Medium (145 images), followed by Low → Medium (26) and Medium → High (26). The YOLO count does not change the picture: it is a statement about scale, not about where the dataset draws the class boundaries, so the written definition does the same work it did without it. The remaining weakness is as before — 134 of 315 Medium images (43%) are still called High, and 131 of 222 Low images (59%) are called Medium; the model almost never calls a scene sparser than the truth (34 images; 291 are called denser).

---

## 3. Counting: No Significant Change

| | Old prompt | New prompt |
|---|---|---|
| MAE | 133.87 | 137.52 |
| Mean signed error | +15.9 | +0.03 |

A paired comparison of absolute error finds no significant difference (**Wilcoxon p = 0.23, paired t-test p = 0.66**; the new prompt is better on 613 images, the old on 680, 307 ties). This is what the design predicts, since only the density-label section of the prompt changed, and it is a useful contrast with Experiment A, where the same paired test did show a significant counting change (see Section 5). The counting error profile is otherwise the same as in the old B run:

| Density | n | MAE (new / old) | Bias (new / old) |
|---|---|---|---|
| Low (0) | 222 | 19.5 / 15.9 | −16.1 / −11.2 |
| Medium (1) | 315 | 39.8 / 36.8 | −15.6 / −8.0 |
| High (2) | 1063 | 191.1 / 187.3 | +8.0 / +28.6 |

By ground-truth count (new prompt):

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 8.9 | +8.5 |
| 11–50 | 378 | 8.2 | +2.3 |
| 51–100 | 301 | 22.2 | +8.1 |
| 101–500 | 625 | 74.3 | −0.3 |
| 501–1,000 | 126 | 324.6 | +12.7 |
| 1,001+ | 112 | 1,092.9 | −46.2 |

Across all images, 638 are over-counted, 888 under-counted and 74 exact; the median absolute error is 22.0 and 28.8% of predictions are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 137.52 to 115.05.

---

## 4. Use of the YOLO Count: Almost Unchanged

| | Old prompt | New prompt |
|---|---|---|
| Exact echo of the YOLO count | 215 (13.4%) | 253 (15.8%) |
| Answers at or above the YOLO count | 99.6% | 99.1% |
| Median ratio, answer / YOLO count | 1.87× | 1.72× |
| Echo rate: Low / Medium / High images | 25.2 / 15.2 / 10.4% | 27.5 / 17.1 / 13.0% |
| YOLO ≥ 75% of truth (404 images): echo rate / MAE | 40.8% / 15.6 | 44.3% / 12.0 |
| YOLO < 25% of truth (402 images): echo rate / MAE | 1.7% / 401.3 | 2.7% / 419.8 |

In the Qwen experiment the longer prompt coincided with a large increase in YOLO substitution (46.2% → 57.9%). GPT shows nothing like it: the exact-echo rate moves from 13.4% to 15.8%, and the answer is closer to the YOLO count than the old-prompt answer on only 52.8% of images (a coin flip). The "floor-and-revise" strategy of the old run (99% of answers at or above the YOLO count) is intact. The cap in the YOLO input (counts never exceed 300; 135 images at exactly 300, 99.3% with a true count above 300) is again handled mostly by rejecting it: 83.7% of answers on those images exceed 300 (old: 87.4%), MAE 324.0 (old: 338.4; YOLO: 803.0); these images carry 19.9% of the total absolute error from 8.4% of the data.

---

## 5. Density-Definition A vs. B, and a Methodological Caveat

Within the density-definition prompt, the YOLO count still lowers counting error: **MAE 169.95 (A) → 137.52 (B), −19.1%; RMSE −8.1%**; Wilcoxon p = 9.6×10⁻¹⁵, paired t-test p = 8.5×10⁻⁴; B has the lower error on 837 images, A on 630 (133 ties). Density accuracy does not change significantly between A and B under this prompt: 42 images wrong → right, 29 right → wrong (p = 0.15).

The A→B counting gain is **smaller under the new prompt (−19.1%) than under the old one (−32.5%, 198.45 → 133.87)**. The reason is visible in the tables: counting under the new prompt improved in Experiment A (MAE 198.45 → 169.95) but not in Experiment B (133.87 → 137.52), so the gap between A and B narrowed from the A side. Because the density-label change should not by itself affect counting, and B (where the paired test finds no counting change) behaves as the design predicts while A does not, the A-side counting shift is a candidate for **run-to-run variation of a non-deterministic model** rather than an effect of the prompt. No repeat of either old-prompt run was made, so this cannot be settled with the present data; a repeated run would give an estimate of the noise against which both the counting and the density differences could be judged. The density improvement is consistent across A and B and concentrated in one class, which makes it the more credible finding, but its McNemar p-values do not account for the model's own non-determinism.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 1343 | 3,428 | 12,500 | 26 | 9,072 |
| 814 | 8,994 | **115** | 6 | 8,879 |
| 1510 | 3,641 | 12,000 | 41 | 8,359 |
| 4159 | 6,210 | 12,000 | 55 | 5,790 |
| 2203 | 4,622 | **201** | 201 | 4,421 |
| 2070 | 6,073 | 10,478 | 9 | 4,405 |

The pattern is the old one: the model rejects an implausibly low YOLO count (all six are ≤ 55 against true counts of 3,428–8,994) but lands too high on four of the six, or follows it down (814: 115; 2203: 201, an exact echo). The largest prediction is 12,500; four predictions exceed 10,000. Comparison with the old-prompt B run on individual images: **image 3178** (true 7,560, YOLO 9), the old run's clear failure (answered 14), is now answered **7,428**; image 814 gets worse (3,500 → 115); image 3411 (true 105, YOLO 110) is answered **130** (old: 110, an exact echo) — the 21,482 anomaly seen in Qwen and Gemma does not reproduce.

---

## 7. Reasoning Effort and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Mean input tokens / request | 341 | 420 |
| Mean output tokens / request | — | 570 (of which reasoning: 555; median 490) |
| Longest output | — | 2,323 tokens |
| Actual cost at Batch prices ($1 / $5 per 1M tokens, 50% discount; third-party-reported) | ≈ $2.50 | ≈ **$2.62** |

Reasoning is slightly longer with the definition (555 vs 541 tokens; paired Wilcoxon p ≈ 1.5×10⁻⁴) and, as in Experiment A, shorter with the YOLO count than without (555 vs 696). It correlates negatively with the true count (ρ = −0.26) and with absolute error (ρ = −0.26), and is highest on Medium-density images (mean 708 tokens vs 509 for Low and 520 for High).

---

## 8. Interpretation

The density definition improves GPT-6.1 Terra's density classification in Experiment B as it did in A: accuracy rises from 76.25% to 79.69% and F1 from 72.77% to 77.73%, driven almost entirely by Medium images (recall 28.6% → 56.5%), at a modest cost on Low (33.8% → 29.3%) and High (99.3% → 97.1%). Unlike Qwen, where the same longer prompt appeared to push the model towards copying the YOLO number, GPT's use of the YOLO count is unchanged (echo rate 13.4% → 15.8%; still at or above the YOLO count in 99% of answers), and counting error is statistically unchanged. The two prompt elements — the definition and the YOLO count — therefore act independently here, on different parts of the output: the count shapes the count, the definition shapes the density label. The weakness that remains is on the sparse end of the scale (Low recall 29.3%), which labelled examples handle better than a written definition (5-shot B: 59.9%).

Across the study, GPT therefore adds a **fourth outcome** to the three already observed: a moderate, consistent gain in both A and B (Qwen: a small gain in A only; LLaVA: a reliability backfire; Gemma: a severe decline), consistent with the idea that whether a written definition helps depends on how badly the model's own implicit boundary is placed — here, poorly enough (77% of Medium images called High under the old prompt) that a rule helped rather than interfered.

---

## 9. Limitations

- Single, non-deterministic run, compared against a single old-prompt run; run-to-run variance was not measured (Section 5).
- Each McNemar p-value treats the two runs as fixed; it does not include the model's own sampling variation.
- GPT differs from the open models in scale, architecture, serving and use of medium-effort reasoning.
- The 300-count wall in the YOLO input is described from the data; its cause (a detection cap in the YOLO run) is an inference and has not been verified.
- Token prices are third-party-reported and should be checked against OpenAI's pricing page.

---

## 10. Status

Density-definition Experiments A and B are both complete for GPT-6.1 Terra. **All six GPT conditions are now complete** (5-shot A/B, zero-shot A/B, density-definition A/B). The remaining step for this model is to add GPT as a fourth model to the final cross-model comparison and to the density-definition synthesis.
