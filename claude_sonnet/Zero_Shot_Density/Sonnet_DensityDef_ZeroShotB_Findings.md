# Claude Sonnet 5.5 — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples. The prompt is the zero-shot Experiment B prompt (YOLO-predicted count given for the test image) with the same single change as in Experiment A: the bare density labels are replaced by an explicit visual definition of Low / Medium / High ("judge by how visually packed the crowd appears, not by exact count"). Wording identical to the Qwen, LLaVA, Gemma, GPT and Claude Haiku density-definition experiments. `claude-sonnet-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium** (set explicitly; the model's default is `high`), 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run (see Section 5).

The comparison baseline is Claude Sonnet's own zero-shot Experiment B with the original bare-label prompt (`../Zero_Shot/Sonnet_ZeroShot_B_Findings.md`). The matching test without the YOLO count is in `Sonnet_DensityDef_ZeroShotA_Findings.md`.

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | 207.56 | **182.59** |
| RMSE | 1237.58 | **970.49** |
| MAPE | 36.73% | **34.87%** |
| Density accuracy | 76.50% | **77.81%** |
| Density precision | **83.85%** | 83.36% |
| Density recall | 76.50% | **77.81%** |
| Density F1 | 77.31% | **79.23%** |
| Pearson r / Spearman ρ | **0.767** / 0.945 | 0.754 / 0.945 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

Density accuracy rises by 1.3 points and F1 by 1.9 points; the accuracy gain is **not statistically significant** (125 images fixed against 104 broken, McNemar p = 0.19), but, as in Experiment A, the profile changes markedly (Section 2). Counting error falls (MAE −12%, RMSE −22%), although only weakly supported by the paired tests (Section 3).

**Against YOLO** (MAE 241.87, RMSE 737.65, MAPE 50.64%): the new prompt beats it on MAE (−25%) and MAPE (34.87% vs 50.64%) but not on RMSE (970.49).

**Against the other models' density-definition Experiment B runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 65.81% | 66.69% | not significant |
| LLaVA-Interleave-0.5B | 14.56% | 14.20% | small, significant decline |
| Gemma 3 (4B) | 64.69% | 37.44% | severe, highly significant decline |
| GPT-6.1 Terra | 76.25% | 79.69% | significant improvement |
| Claude Haiku 5.5 | 70.31% | 75.38% | significant improvement |
| **Claude Sonnet 5.5** | **76.50%** | **77.81%** | **small, not significant (McNemar p = 0.19)** |

With the definition the three closed models end within 2 points of each other on density (GPT 79.69%, Sonnet 77.81%, Haiku 75.38%). In counting, Sonnet's MAE (182.59) is better than every open model's (235–258) and Haiku's (207.00) but behind GPT's (137.52); its RMSE (970.49) is worse than GPT's (558.98) and every open model's (680–926); and its MAPE (34.87%) is the lowest of all six models (GPT 36.19%) — see the cross-model summary in Section 7. Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture, serving and in running without visible thinking, and — unlike the open-source runs — it is not deterministic.

---

## 2. Density Classification: A Large Gain on Low, a Cost on High

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | 36.5% (81) | **57.7%** (128) |
| Medium | 315 | **79.4%** (250) | 76.8% (242) |
| High | 1063 | **84.0%** (893) | 82.3% (875) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 128 | 89 | 5 |
| **True Medium** | 16 | 242 | 57 |
| **True High** | 3 | 185 | 875 |

Predicted-class shares: Low 9.2%, Medium 32.2%, High 58.6% (old prompt: 5.4% / 34.8% / 59.9%; truth: 13.9% / 19.7% / 66.4%). Accuracy of 77.81% (1245 / 1600) is far above the always-"High" baseline of 66.44% (binomial p = 1×10⁻²³).

**Image-level tracking.** 232 density predictions changed between the two prompts: **125 images flipped from wrong to right and 104 from right to wrong** (McNemar's exact test p = 0.19). By true class:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | **56** | 9 |
| Medium | 22 | 30 |
| High | 47 | **65** |

As in Experiment A, the definition helps the **Low** class clearly (+56 / −9; recall 36.5% → 57.7%), is neutral to slightly negative on Medium (+22 / −30) and costs on **High** (+47 / −65). The most frequent label changes are High → Medium (87 images), Medium → Low (70) and Medium → High (66). The YOLO count does not change the picture: the written definition does the same work with it as without it. Remaining weaknesses: 89 of 222 Low images (40%) are still called Medium, 185 High images are called Medium (old prompt: 167), and the predicted Medium share (32.2%) is well above the true share (19.7%). 204 predictions are sparser than the truth and 151 denser.

**Compared with Sonnet's 5-shot B:** the definition reaches the same accuracy (77.81% vs 77.44%; 154 images right only here, 148 only in 5-shot; p = 0.77) with a different profile (Low / Medium / High recall: 57.7 / 76.8 / 82.3 vs 60.8 / 58.4 / 86.5). **Compared with GPT-6.1 Terra's density-definition B run** (paired): GPT is right on 177 images where Sonnet is wrong and Sonnet on 147 where GPT is wrong (p = 0.11); identical labels on 1255 of 1600 images (78%). **Compared with Haiku's:** Sonnet alone is right on 173 images, Haiku alone on 134 (p = 0.030).

---

## 3. Counting: A Moderate Improvement, Not Clearly Significant

| | Old prompt | New prompt |
|---|---|---|
| MAE | 207.56 | 182.59 |
| RMSE | 1237.58 | 970.49 |
| MAPE | 36.73% | 34.87% |
| Mean signed error | +95.8 | +46.6 |

A paired comparison of absolute error finds **no significant change** (Wilcoxon p = 0.11, paired t-test p = 0.075; the new prompt is better on 458 images, the old on 528, with 614 ties; the median absolute error moves from 22.0 to 23.0). The count prediction differs between the runs on 996 of 1600 images although the two sets of predictions are almost perfectly rank-correlated (Spearman ρ = 0.988): the lower mean is mostly the tail. Because only the density-label text changed, a genuine counting effect is not expected, and the improvement is within what run-to-run variation of a non-deterministic model could produce (see Section 5).

| Density | n | MAE (new / old) | Bias (new / old) |
|---|---|---|---|
| Low (0) | 222 | 17.4 / 19.1 | −9.6 / +2.5 |
| Medium (1) | 315 | 39.8 / 50.6 | −28.0 / −15.1 |
| High (2) | 1063 | 259.4 / 293.4 | +80.5 / +148.2 |

By ground-truth count (new prompt) — MAE / mean bias: 0–10: 1.8 / +1.6; 11–50: 6.3 / −0.4; 51–100: 21.8 / −3.7; 101–500: 91.0 / −5.8; 501–1,000: 395.2 / +70.4; above 1,000: 1,575.3 / +629.9. Predictions lean low (530 over-counts, 998 under-counts, 72 exact); 25.4% are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 182.59 to 145.53. MAPE is not driven by a single image (largest contribution 8 points). **Five** predictions exceed 10,000 (old prompt: 6) and account for 20.0% of the total absolute error; without them (descriptive only: the group is defined by the model's own outputs) MAE would be 146.56.

---

## 4. Use of the YOLO Count: Almost Unchanged

| | Old prompt | New prompt |
|---|---|---|
| Exact echo of the YOLO count | 21 (1.3%) | 26 (1.6%) |
| Within 10% of YOLO, not exact | 277 | 268 |
| Answers at or above the YOLO count | 93.9% | 92.6% |
| Median ratio, answer / YOLO count | 1.64× | 1.60× |
| Echo rate: Low / Medium / High images | 8.6 / 0.6 / 0.0% | 9.5 / 1.0 / 0.2% |
| YOLO ≥ 75% of truth (404 images): echo rate / MAE | 5.0% / 16.4 | 5.7% / 17.8 |
| YOLO < 25% of truth (402 images): echo rate / MAE | 0.2% / 649.2 | 0.2% / 555.8 |

In contrast to Qwen (more copying under the longer prompt) and Haiku (fewer echoes), Sonnet's use of the YOLO count is essentially the same with and without the definition: a floor, never copied. The cap in the YOLO input (counts never exceed 300; 135 images at exactly 300, 99.3% with a true count above 300) is again rejected: 95.6% of answers on those images exceed 300, none echoes 300, and MAE on them is 491.5 (old: 515.8; YOLO itself 803.0), against 154.1 for the other 1,465 images; they contribute 22.7% of the total absolute error from 8.4% of the data. On the 26 images with a YOLO count of zero the median answer is 42 (maximum 4,500) and MAE 491.0.

---

## 5. Density-Definition A vs. B, and a Methodological Caveat

Within the density-definition prompt the YOLO count lowers counting error: **MAE 232.80 (A) → 182.59 (B), −21.6%; RMSE 1551.74 → 970.49, −37.5%**; Wilcoxon p = 2×10⁻⁶, paired t-test p = 0.0055; B has the lower error on 677 images, A on 518 (405 ties). Density accuracy does not change between A and B under this prompt (78.12% in A, 77.81% in B: 34 images wrong → right, 39 right → wrong, p = 0.64). The A→B gain is similar to that under the bare-label prompt (−17.8%), with the difference that the paired rank test is clearer here and the tail (RMSE) shrinks more.

The counting differences between the old-prompt and new-prompt runs — in A as well as in B — are small relative to what run-to-run variation can produce: Sonnet's counts differ on 996–1062 of 1600 images between the two prompts, with rank correlation 0.98–0.99, and the paired tests do not find a significant change in either experiment. No repeat of either old-prompt run was made, so neither the counting nor the density differences can be separated from the model's own non-determinism; the McNemar p-values do not include it. The density effect is more credible than the counting effect because it is directional and concentrated in one class (Low), in both A and B.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | error |
|---|---|---|---|---|
| 212 | 9,059 | **40,000** | 1 | +30,941 |
| 4159 | 6,210 | 15,000 | 55 | +8,790 |
| 2203 | 4,622 | 12,000 | 201 | +7,378 |
| 814 | 8,994 | **2,000** | 6 | −6,994 |
| 2070 | 6,073 | 12,000 | 9 | +5,927 |
| 4056 | 6,660 | 12,000 | 10 | +5,340 |

The pattern is the old one: the model rejects an implausibly low YOLO count (all six are ≤ 201 against true counts of 4,622–9,059) and lands too high on five of the six, or too low (814). The largest prediction is 40,000 (image 212; old prompt: 45,000). Compared with the old-prompt B run: **image 3178** (true 7,560, YOLO 9) goes from 20,000 to 6,000, image 2203 from 25,000 to 12,000 and image 814 from 6,000 to 2,000, while image 4159 worsens (12,000 → 15,000). **Test image 3411 (true 105; YOLO 110)** is answered **105**, exactly the true count (as in the old run); the anomaly seen in Qwen and Gemma does not reproduce. The most frequent predictions are 45 (79 times), 120 (69), 150 (68), 420 (55); 11.5% are multiples of 100 (old prompt: 9.1%).

---

## 7. Reasoning and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Requests with a bare answer (output ≤ 15 tokens) | 1595 (99.7%) | 1593 (99.6%) |
| Mean / max output tokens | 13.8 / 346 | 14.1 / 453 |
| Mean input tokens / request | 464 | 588 |
| Total input / output tokens | 741,727 / 22,095 | 940,127 / 22,570 |
| Cost at Batch prices ($1 / $5 per 1M tokens; Anthropic's published rates, to be verified) | ≈ $0.85 | ≈ **$1.05** |

The definition does **not** change how much Sonnet thinks (paired Wilcoxon on output length: p = 0.88), unlike for Claude Haiku, where it raised the share of bare answers from 4% to 37%. Seven requests (0.4%) begin with a visible count of people (old B: 5; density-definition A: 1) — all small crowds (true count 6–16, YOLO 5–23): their MAE is 1.3 against 183.4 for the rest, but their density accuracy is low (3 of 7 correct against 78%), and two of the seven echo the YOLO count (28.6% against 1.5%).

**Cross-model summary, zero-shot density-definition B** (new prompt): Qwen 258.27 / 909.44 / 66.70% / 66.7% (MAE / RMSE / MAPE / accuracy); LLaVA 235.07 / 680.04 / 55.71% / 14.2%; Gemma 245.46 / 926.05 / 58.98% / 37.4%; GPT 137.52 / 558.98 / 36.19% / 79.7%; Haiku 207.00 / 1164.75 / 37.58% / 75.4%; **Sonnet 182.59 / 970.49 / 34.87% / 77.8%**. Sonnet has the best MAPE and the second-best MAE and density accuracy of the six.

---

## 8. Interpretation

The density definition improves Claude Sonnet 5.5's density classification only modestly in Experiment B — accuracy 76.50% → 77.81% (not significant) and F1 77.31% → 79.23% — but, as in A, it reshapes the profile: Low recall jumps from 36.5% to 57.7% (56 images fixed, 9 broken), Medium and High recall each lose 1–3 points, and the predictions become less biased toward Medium. The reason is the same: Sonnet's bare-label calibration was already good (Medium recall 79%), so the rule has little to repair and mostly moves the Low/Medium boundary; the models that gained clearly from the definition (GPT, Haiku) started from a poor bare-label calibration. The YOLO count and the definition act independently — the use of the count is unchanged (1.6% echoes, a floor), density is unchanged by the count, and the A→B counting gain is about the same under both prompts. Counting error is lower than under the bare-label prompt, but not significantly, and the accompanying figures should not be attributed to the prompt text.

Across the study Sonnet is a distinct outcome: for neither A nor B does the definition change density accuracy significantly, whereas GPT and Haiku gain consistently, Qwen's gain is small and unreliable, LLaVA backfires and Gemma is severely harmed — consistent with the hypothesis that a written definition helps in proportion to how poorly the model's implicit class boundaries are placed.

---

## 9. Limitations

- Single, non-deterministic run, compared against a single old-prompt run; run-to-run variance was not measured (Section 5).
- Each McNemar p-value treats the two runs as fixed; it does not include the model's own sampling variation.
- The tail analysis defines groups from the model's own outputs and is descriptive.
- The 300-count wall in the YOLO input is described from the data; its cause (a detection cap in the YOLO run) is an inference and has not been verified.
- Only effort `medium` was tested; thinking is practically absent at that setting.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Density-definition Experiments A and B are both complete for Claude Sonnet 5.5. **All six Sonnet conditions are now complete** (5-shot, zero-shot, zero-shot + density definition, each A and B). The remaining step is to add GPT, Claude Haiku and Claude Sonnet to the final cross-model comparison and to the density-definition synthesis.
