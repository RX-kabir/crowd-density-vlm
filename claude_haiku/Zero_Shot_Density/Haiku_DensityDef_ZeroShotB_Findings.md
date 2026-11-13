# Claude Haiku 5.5 — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. The prompt is the zero-shot Experiment B prompt (YOLO-predicted count given for the test image) with the same single change as in Experiment A: the bare density labels are replaced by an explicit visual definition of Low / Medium / High ("judge by how visually packed the crowd appears, not by exact count"). Wording identical to the Qwen, LLaVA, Gemma and GPT density-definition experiments. `claude-haiku-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run (see Section 5).

The comparison baseline is Claude's own zero-shot Experiment B with the original bare-label prompt (`../Zero_Shot/Haiku_ZeroShot_B_Findings.md`). The matching test without the YOLO count is in `Haiku_DensityDef_ZeroShotA_Findings.md`.

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | 237.11 | **207.00** |
| RMSE | 1384.49 | **1164.75** |
| MAPE | 43.01% | **37.58%** |
| Density accuracy | 70.31% | **75.38%** |
| Density precision | 70.04% | 78.55% |
| Density recall | 70.31% | 75.38% |
| Density F1 | 65.97% | **74.50%** |
| Pearson r / Spearman ρ | 0.590 / 0.899 | 0.574 / 0.889 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

Density classification improves clearly (+5.1 points accuracy, +8.5 points F1) and counting error falls moderately (MAE −12.7%, MAPE 43.0% → 37.6%), although the counting difference is only weakly supported by the paired tests (Section 3).

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64%): the new-prompt Experiment B beats it on MAE and MAPE but not on RMSE (1164.75), as the old-prompt B did.

**Against Claude's 5-shot Experiment B** (MAE 220.92, RMSE 1100.55, MAPE 44.26%, density 71.31%): the zero-shot definition run has the lower MAE and MAPE, a higher density accuracy (75.38% vs 71.31%; McNemar: 198 images right only here, 133 only in 5-shot, p = 4×10⁻⁴) and a higher RMSE. Its absolute error is lower on 784 images and higher on 576 (Wilcoxon p = 2×10⁻¹⁵). A written definition without examples is therefore at least as good as five labelled examples on this model.

**Against the other models' density-definition Experiment B runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 65.81% | 66.69% | not significant |
| LLaVA-Interleave-0.5B | 14.56% | 14.20% | small, significant decline |
| Gemma 3 (4B) | 64.69% | 37.44% | severe, highly significant decline |
| GPT-6.1 Terra | 76.25% | 79.69% | significant improvement |
| **Claude Haiku 5.5** | **70.31%** | **75.38%** | **significant improvement (McNemar p = 1.8×10⁻⁷)** |

Claude is the second model, after GPT, for which the definition helps in *both* experiments with statistical support — and again with the largest gain (+5.1 points; GPT +3.4). In this condition Claude's counting is better than every open model's on MAE (207.00 vs 235–258) but worse on RMSE (1164.75 vs 680–926), and its MAPE (37.58%) is second only to GPT's (36.19%). Caveat: Claude differs from the open models in scale, architecture, serving and in running with adaptive thinking, and — unlike the open-source runs — it is not deterministic.

---

## 2. Density Classification: Same Pattern as Experiment A — Large Gains on Medium and Low

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | 15.8% (35) | **26.1%** (58) |
| Medium | 315 | 23.8% (75) | **59.7%** (188) |
| High | 1063 | **95.5%** (1015) | 90.3% (960) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 58 | 150 | 14 |
| **True Medium** | 6 | 188 | 121 |
| **True High** | 4 | 99 | 960 |

Predicted-class shares: Low 4.2%, Medium 27.3%, High 68.4% (old prompt: 2.4% / 16.5% / 81.1%; truth: 13.9% / 19.7% / 66.4%). The share of "High" predictions is now almost exactly the true share, and the Medium share has overshot it (27.3% vs 19.7%). Accuracy of 75.38% (1206 / 1600) is far above the always-"High" baseline of 66.44% (binomial p = 5×10⁻¹⁵).

**Image-level tracking.** 281 density predictions changed between the two prompts: **160 images flipped from wrong to right and 79 from right to wrong** (McNemar's exact test p = 1.8×10⁻⁷). By true class:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | 26 | 3 |
| Medium | **121** | 8 |
| High | 13 | **68** |

The gain is on Medium (+121 / −8) and Low (+26 / −3), and is paid for on High (−68 / +13). The most frequent label change is High → Medium (220 images), followed by Medium → Low (29) and Medium → High (22): the model now assigns the Medium label far more readily — 99 High images are called Medium (old prompt: 47) — which is the cost of the rule. Remaining weaknesses: 121 of 315 Medium images (38%) are still called High, and 150 of 222 Low images (68%) are called Medium; the model calls 109 scenes sparser than the truth and 285 denser.

---

## 3. Counting: A Moderate Improvement That Is Mostly in the Tail

| | Old prompt | New prompt |
|---|---|---|
| MAE | 237.11 | 207.00 |
| RMSE | 1384.49 | 1164.75 |
| MAPE | 43.01% | 37.58% |
| Mean signed error | +25.1 | −39.4 |

A paired comparison of absolute error is only weakly significant (**Wilcoxon p = 0.025, paired t-test p = 0.27**; the new prompt is better on 709 images, the old on 630, with 261 ties). The mean improves, but the typical image is barely affected: the median absolute error moves from 28.0 to 26.0, and the share within ±10% of the truth from 19.2% to 21.4%. The change in mean signed error from +25 to −39 means that predictions now lean slightly *below* the truth: 397 over-counts, 1139 under-counts, 64 exact.

| Density | n | MAE (new / old) | Bias (new / old) |
|---|---|---|---|
| Low (0) | 222 | 26.5 / 21.7 | −24.8 / −20.5 |
| Medium (1) | 315 | 59.9 / 102.4 | −55.2 / +2.9 |
| High (2) | 1063 | 288.3 / 322.0 | −37.7 / +41.2 |

By ground-truth count (new prompt):

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 1.2 | +0.8 |
| 11–50 | 378 | 7.7 | −3.4 |
| 51–100 | 301 | 25.6 | −4.1 |
| 101–500 | 625 | 88.8 | −32.4 |
| 501–1,000 | 126 | 436.8 | −144.1 |
| 1,001+ | 112 | 1,875.2 | −197.7 |

Removing the 5 worst predictions lowers MAE from 207.00 to 157.18. Four predictions exceed 10,000 (old prompt: 5) and account for 21.6% of the total absolute error; without them MAE would be 162.71.

---

## 4. Use of the YOLO Count: Less Copying Than Before

| | Old prompt | New prompt |
|---|---|---|
| Exact echo of the YOLO count | 225 (14.1%) | **98 (6.1%)** |
| Within 10% of YOLO, not exact | 318 | 370 |
| Answers at or above the YOLO count | 93.9% | 90.6% |
| Median ratio, answer / YOLO count | 1.37× | 1.35× |
| Echo rate: Low / Medium / High images | 23.9 / 20.3 / 10.2% | 17.6 / 8.3 / 3.1% |
| YOLO ≥ 75% of truth (404 images): echo rate / MAE | 31.7% / 19.0 | 15.3% / 14.5 |
| YOLO < 25% of truth (402 images): echo rate / MAE | 4.5% / 717.1 | 3.5% / 634.6 |

Opposite to Qwen, where the longer prompt coincided with *more* YOLO substitution (46.2% → 57.9%), Claude copies the number less than half as often (14.1% → 6.1%) while still treating it as a floor (median answer 1.35× the YOLO count); its answer is closer to the YOLO count than the old-prompt answer on only 40% of images. The cap in the YOLO input (counts never exceed 300; 135 images at exactly 300, 99.3% with a true count above 300) is again mostly rejected: 94.1% of answers on those images exceed 300 and only 0.7% echo 300; MAE on them is 477.8 (old: 620.2; YOLO itself: 803.0), against 182.0 for the other 1,465 images, and the saturated images contribute 19.5% of the total absolute error from 8.4% of the data. On the 26 images with a YOLO count of zero the median answer is 20 (maximum 4,200) and MAE is 387.1.

---

## 5. Density-Definition A vs. B, and a Methodological Caveat

Within the density-definition prompt the YOLO count lowers the *mean* counting error — **MAE 278.39 (A) → 207.00 (B), −25.6%; RMSE 1845.96 → 1164.75, −36.9%** — but the paired test finds no difference in typical error (**Wilcoxon p = 0.90; paired t-test p = 0.029**; B has the lower error on 718 images, A on 738, 144 ties). The gain is a tail effect, as in the old-prompt zero-shot comparison, where B nevertheless was better on slightly more images. Density accuracy does not change significantly under this prompt (75.38% in B vs 76.38% in A: 58 images wrong → right, 74 right → wrong, p = 0.19).

The A→B counting gain is **smaller under the new prompt (−25.6%) than under the old prompt (−50.9%, 482.64 → 237.11)**, because the definition prompt already improved Experiment A (MAE 482.64 → 278.39) far more than B (237.11 → 207.00). Since only the density-label text changed, a prompt effect on counting is not expected mechanistically, and the large counting change in A in particular is a candidate for **run-to-run variation of a non-deterministic model** — and/or for the changed amount of thinking (Section 7). No repeat of either old-prompt run was made, so this cannot be settled with the present data. The density improvement is consistent in A and B and concentrated in two classes, which makes it the more credible finding, but its McNemar p-values do not include the model's own non-determinism.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | error |
|---|---|---|---|---|
| 212 | 9,059 | **45,000** | 1 | +35,941 |
| 4159 | 6,210 | 20,000 | 55 | +13,790 |
| 4279 | 2,308 | 14,000 | 25 | +11,692 |
| 3015 | 895 | 11,000 | 11 | +10,105 |
| 814 | 8,994 | **14** | 6 | −8,980 |
| 3178 | 7,560 | **12** | 9 | −7,548 |

The model overshoots by a large factor when YOLO is absurdly low (212, 4159, 4279, 3015), but in the two other cases with extreme under-counts (814, 3178) it *adopts* YOLO's near-zero count (14 for 6; 12 for 9). Image 3178 is a reversal: the old-prompt B run answered 2,000, now 12; 2203 improves (2,500 → 412, still an under-count). The largest prediction is 45,000 (old prompt: 45,000; zero-shot A: 87,412). **Test image 3411 (true 105; YOLO 110)** — the source of the identical prediction 21,482 in eight Qwen and Gemma conditions — is answered 125 (old: 118); the anomaly does not reproduce.

**Stock answers.** Rounding is lower than in A: 5.4% of predictions are multiples of 100 (old prompt: 6.3%); the most frequent values are 412 (46 times), 30 (36), 180 (31), 120 (29).

---

## 7. Reasoning and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Requests with a bare answer (output ≤ 15 tokens) | 64 (4.0%) | **598 (37.4%)** |
| Mean / median / max output tokens | 244 / 183 / 932 | 174 / 150 / 904 |
| Mean input tokens / request | 464 | 588 |
| Total input / output tokens | 741,727 / 390,161 | 940,127 / 278,362 |
| Cost at Batch prices ($0.05 / $0.25 per 1M tokens; Anthropic's published rates, to be verified) | ≈ $0.13 | ≈ **$0.12** |

As in Experiment A, the definition makes the model think far less: 37.4% of requests receive a bare answer (paired Wilcoxon on output length p ≈ 2×10⁻⁸⁷). Thinking is not reported separately, so output length is a proxy. Bare-answer requests concern larger crowds (median true count 179.5, against 76.5 for the others), are more often right on density (85.3% vs 69.5%) and echo the YOLO count less (3.3% vs 7.8%); their MAE is 225.1 against 196.2. Output length correlates negatively with the true count (ρ = −0.41) and with absolute error (ρ = −0.27), and is highest on Low and Medium scenes (mean 271 and 248 tokens against 132 for High). By output-length quartile: ≤ 150 tokens: n = 805, MAE 247.8, density accuracy 87.0%, echo rate 3.2%; 151–274: n = 395, MAE 160.6, accuracy 75.4%, echo 3.3%; above 274: n = 400, MAE 170.6, accuracy 52.0%, echo 14.8% (median true count 38). These are associations, not causal claims. All 1600 responses follow the bare format (941 with a single line break, 659 with a blank line); the verbose response seen once in Experiment A does not recur.

---

## 8. Interpretation

The density definition improves Claude Haiku 5.5's density classification in Experiment B as it did in A: accuracy rises from 70.31% to 75.38% and F1 from 65.97% to 74.50%, with the gain on Medium (recall 23.8% → 59.7%) and Low (15.8% → 26.1%) at the price of High (95.5% → 90.3%). The share of "High" predictions falls to 68.4%, almost exactly the true 66.4%. The effect is again independent of the YOLO number — the written definition does the same work with or without it (A: +4.8 points; B: +5.1) — and in this model it brings zero-shot density accuracy above Claude's 5-shot results.

Counting is a different matter. The mean error falls (MAE −12.7%), but the typical image is barely affected, and the use of the YOLO count changes: exact echoes drop from 14.1% to 6.1%, the model keeps treating the number as a floor, and in two extreme cases it follows a near-zero count down. The accompanying drop in thinking (4.0% → 37.4% of bare answers) indicates that the longer prompt alters more of the model's behaviour than the density rule alone, which is why counting differences should not be attributed to the definition. Across the study Claude joins GPT as a model for which a written definition helps consistently in A and B, whereas Qwen's gain is small and unreliable, LLaVA backfires and Gemma is severely harmed; as for GPT, the likely reason is that the model's own implicit class boundary (a threshold placed too low under the bare-label prompt) was poor enough that an explicit rule helped.

---

## 9. Limitations

- Single, non-deterministic run, compared against a single old-prompt run; run-to-run variance was not measured (Section 5).
- Each McNemar p-value treats the two runs as fixed; it does not include the model's own sampling variation.
- Thinking effort is inferred from output length; the large shift in bare answers is an observation, not an explanation.
- The 300-count wall in the YOLO input is described from the data; its cause (a detection cap in the YOLO run) is an inference and has not been verified.
- Claude differs from the open models in scale, architecture, serving and use of adaptive thinking.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Density-definition Experiments A and B are both complete for Claude Haiku 5.5. **All six Claude conditions are now complete** (5-shot A/B, zero-shot A/B, density-definition A/B). The remaining step for this model is to add Claude (and GPT) to the final cross-model comparison and to the density-definition synthesis.
