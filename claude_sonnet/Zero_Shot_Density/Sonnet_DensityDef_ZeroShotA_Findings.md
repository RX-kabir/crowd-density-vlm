# Claude Sonnet 5.5 — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples and no YOLO count. The system prompt is the zero-shot prompt with one change: the bare density labels (`0 = Low, 1 = Medium, 2 = High`) are replaced by an explicit visual definition of each class ("judge by how visually packed the crowd appears, not by exact count"; Low = people clearly separated; Medium = moderately close, some overlap but gaps and open space still visible; High = tightly packed, little or no visible space). Identical wording to the Qwen, LLaVA, Gemma, GPT and Claude Haiku density-definition experiments. `claude-sonnet-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium** (set explicitly; the model's default is `high`), 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run (see Section 4).

The comparison baseline throughout is Claude Sonnet's own zero-shot Experiment A with the original bare-label prompt (`../Zero_Shot/Sonnet_ZeroShot_A_Findings.md`).

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | 252.51 | **232.80** |
| RMSE | 1626.03 | **1551.74** |
| MAPE | 45.54% | **41.69%** |
| Density accuracy | 77.81% | **78.12%** |
| Density precision | **84.43%** | 83.31% |
| Density recall | 77.81% | **78.12%** |
| Density F1 | 78.22% | **79.28%** |
| Pearson r / Spearman ρ | 0.685 / 0.938 | 0.713 / 0.929 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

**Accuracy does not change** (+0.3 points; 105 images fixed against 100 broken, McNemar p = 0.78); the definition **redistributes** the correct answers between the classes (Section 3), which raises F1 by 1.1 points. Counting error falls by 8% in MAE but not significantly (Section 4). Sonnet's bare-label baseline was already the best zero-shot A density result of the project, so there was little room: this is the first model for which a written definition leaves density accuracy unchanged.

**Against the other models' density-definition Experiment A runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 66.75% | 68.00% | small, significant improvement |
| LLaVA-Interleave-0.5B | 12.71% | 14.52% | not comparable (reliability fell 38.6% → 22.6%) |
| Gemma 3 (4B) | 64.69% | 42.50% | severe, highly significant decline |
| GPT-6.1 Terra | 75.19% | 78.88% | moderate, significant improvement |
| Claude Haiku 5.5 | 71.62% | 76.38% | moderate, highly significant improvement |
| **Claude Sonnet 5.5** | **77.81%** | **78.12%** | **no change (McNemar p = 0.78)** |

With the definition the three closed models end within 2.5 points of each other (Sonnet 78.12%, GPT 78.88%, Haiku 76.38%): the written rule lifts the weaker bare-label models to the level Sonnet already had. Caveat: Claude Sonnet 5.5 differs from the open models in scale, architecture, serving and in running without visible thinking, and — unlike the open-source runs — it is not deterministic.

**Against YOLO** (MAE 241.87, RMSE 737.65, MAPE 50.64%): the new prompt beats YOLO on MAE (232.80, just) and MAPE (41.69%) but not on RMSE (1551.74).

---

## 2. Response Reliability: Perfect (With One Verbose Response)

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 442 characters (1 response) |

1599 responses are exactly `Count: <n>` and `Density: <d>`. **One response (image 2724, true count 14)** starts by listing what it sees row by row ("Count the panelists: back row: …") before the two required lines; it parses correctly (answer 20). It is the only deviation, and the only visible reasoning in the run.

---

## 3. Density Classification: Same Accuracy, a More Balanced Profile

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | 35.1% (78) | **52.3%** (116) |
| Medium | 315 | **78.1%** (246) | 76.5% (241) |
| High | 1063 | **86.6%** (921) | 84.0% (893) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 116 | 101 | 5 |
| **True Medium** | 13 | 241 | 61 |
| **True High** | 4 | 166 | 893 |

Predicted-class shares: Low 8.3%, Medium 31.8%, High 59.9% (old prompt: 5.0% / 33.1% / 61.9%; truth: 13.9% / 19.7% / 66.4%). The accuracy of 78.12% (1250 / 1600) is far above the always-"High" baseline of 66.44% (one-sided binomial p = 7×10⁻²⁵).

**Tracking individual images.** 211 density predictions changed between the two prompts: **105 images flipped from wrong to right, and 100 from right to wrong** (McNemar's exact test p = 0.78). By true class:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | **46** | 8 |
| Medium | 26 | 31 |
| High | 33 | **61** |

The definition helps the **Low** class clearly (+46 / −8; recall 35.1% → 52.3%), is neutral on Medium (+26 / −31) and costs on **High** (+33 / −61). The most common change of label is High → Medium (87 images); next are Medium → Low (60) and Medium → High (55): the model moves its Medium/High and Low/Medium boundaries both around, with the Low gain as the net result. The model now makes errors in both directions at similar rates (183 predictions sparser than the truth, 167 denser; old prompt: 143 / 212), where the bare-label prompt over-estimated. Remaining weaknesses: 101 of 222 Low images (45%) are still called Medium, 166 High images are called Medium, and the Medium share of predictions (31.8%) is well above the true share (19.7%).

**Compared with Sonnet's own 5-shot run:** the definition reaches the same accuracy (78.12% vs 77.94%; 142 images right only here, 139 only in 5-shot; p = 0.91) and a slightly higher F1 (79.28% vs 78.48%), with a different profile — higher Medium recall (76.5% vs 59.7%), lower Low recall (52.3% vs 59.0%) and lower High recall (84.0% vs 87.3%).

**Compared with GPT-6.1 Terra's density-definition A run** (paired): GPT is right on 156 images where Sonnet is wrong, Sonnet on 144 where GPT is wrong (McNemar p = 0.53): no difference; identical density labels on 1279 of 1600 images (79.9%). **Compared with Claude Haiku's:** Sonnet alone is right on 169, Haiku alone on 141 (p = 0.13): with the definition the two Claude models are statistically indistinguishable on density, though Sonnet's counting remains better (Section 4).

---

## 4. Counting: Slightly Better, Not Significantly

Only the density-label section of the prompt changed, so no mechanistic effect on counting is expected. The counting error falls — **MAE 252.51 → 232.80 (−8%), RMSE 1626.03 → 1551.74 (−5%), MAPE 45.54% → 41.69%**, and the mean signed error from +172.8 to +125.8 — but the paired tests find **no significant change** (Wilcoxon p = 0.76, paired t-test p = 0.60; the new prompt has the lower absolute error on 513 images, the old on 540, with 547 ties; the median absolute error is 26.0 in both). Count predictions differ on 1062 of 1600 images (66%) although the two runs are almost perfectly rank-correlated (Spearman ρ = 0.984): the typical re-run variation of a non-deterministic model. The apparent improvement is therefore indistinguishable from run-to-run variation, and no repeat of the old-prompt run was made to measure it. Notably, and in contrast to Claude Haiku (where the definition changed how much the model thought and counting error fell by 42%), the definition has **no effect on thinking** for Sonnet (Section 7).

**By density class** (MAE / RMSE / bias), new prompt: Low 14.5 / 56.1 / −4.6; Medium 51.2 / 243.5 / −5.5; High 332.2 / 1899.0 / +192.0 (old-prompt MAE: 65.2, 49.8, 351.7). The Low improvement (65.2 → 14.5) comes from a single image: 2740, labelled Low-density with a true count of 2,842, which was answered 14,500 in the old run and 2,500 now.

By ground-truth count — MAE / mean bias: 0–10: 1.8 / +1.7; 11–50: 7.6 / +1.6; 51–100: 27.2 / +4.2; 101–500: 105.8 / +16.7; 501–1,000: 463.5 / +225.5; above 1,000: 2,114.2 / +1,433.4. Over- and under-counts: 672 vs 863 (65 exact); 21.6% of predictions are within ±10% of the truth. Removing the 5 worst predictions lowers MAE from 232.80 to 166.99. MAPE is not driven by any single image (largest contribution 8 points).

**The tail.** Five predictions exceed 10,000 (old prompt: 6) and account for **28.5%** of the total absolute error; without them (descriptive only: the group is defined by the model's own outputs) MAE would be 167.00 and RMSE 523.32, below YOLO's 241.87 / 737.65. Twenty predictions are 5,000 or more, as before.

---

## 5. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 212 | 9,059 | **60,000** | 50,941 |
| 2203 | 4,622 | 25,000 | 20,378 |
| 3178 | 7,560 | 20,000 | 12,440 |
| 4159 | 6,210 | 18,000 | 11,790 |
| 768 | 1,425 | 12,000 | 10,575 |
| 814 | 8,994 | 4,200 | −4,794 |

The largest prediction is 60,000 (image 212; old prompt: 20,000, where its maximum was 45,000), a placeholder-style value of the kind seen in the other models. **Test image 3411 (true count 105)**, the source of the identical prediction 21,482 in eight Qwen and Gemma conditions, is answered **85** (as in the old run); the anomaly does not reproduce.

**Same hard images, old vs. new prompt:**

| Image | True | Old prompt | New prompt |
|---|---|---|---|
| 2203 | 4,622 | 45,000 | 25,000 |
| 2740 | 2,842 | 14,500 | 2,500 |
| 814 | 8,994 | 6,000 | 4,200 |
| 4159 | 6,210 | 9,500 | 18,000 |
| 212 | 9,059 | 20,000 | 60,000 |
| 4056 | 6,660 | 9,500 | 9,500 |
| 2542 | 4,113 | 6,500 | 6,500 |

Some worst cases improve and others worsen by similar amounts, as expected for a change that should not affect counting. **Stock answers:** the most frequent predictions are 230 (108 times), 150 (84), 45 (79), 120 (65), 95 (61) and 38 (57); 55.1% of predictions are multiples of 10 and 10.5% multiples of 100 (old prompt: 7.6%).

---

## 6. Against Claude Haiku 5.5 and GPT-6.1 Terra (Counting, Paired)

**Haiku (density-definition A):** Sonnet's MAE is 232.80 against 278.39; its absolute error is lower on 774 images, Haiku's on 674 (152 ties; Wilcoxon p = 0.048) — a much narrower margin than with the bare-label prompt (p = 4×10⁻¹⁴).
**GPT:** GPT's MAE is 169.95; its absolute error is lower on 808 images, Sonnet's on 705 (87 ties; Wilcoxon p = 0.13).

---

## 7. Reasoning and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Requests with a bare answer (output ≤ 15 tokens) | 1600 (100%) | 1599 (99.9%) |
| Mean / max output tokens | 13.1 / 14 | 13.2 / 181 |
| Mean input tokens / request | 425 | 549 |
| Total input / output tokens | 679,327 / 20,958 | 877,727 / 21,110 |
| Cost at Batch prices ($1 / $5 per 1M tokens; Anthropic's published rates, to be verified) | ≈ $0.78 | ≈ **$0.98** |

The definition does not make Sonnet think: it answers directly on 1599 of 1600 requests in both conditions (the single exception is described in Section 2). This differs from Claude Haiku 5.5, for which the same prompt change raised the share of bare answers from 1.6% to 40.6%. The only cost difference is the 30% longer input.

---

## 8. Interpretation

The density definition does not help Claude Sonnet 5.5 on accuracy — 77.81% → 78.12%, a difference well within noise — but it changes where the model is right: Low-class recall rises from 35.1% to 52.3% (46 images fixed, 8 broken), at the expense of a few points on High (86.6% → 84.0%), which leaves F1 slightly higher (79.28%) and the predictions more evenly balanced between over- and under-estimates. The likely reason is the one seen for the other closed models in reverse: the models that gained from the definition (GPT, Haiku) had bare-label calibrations that placed the boundaries badly (most Medium images called High); Sonnet's bare-label calibration was already good, so the rule has nothing to repair and mainly shifts the Low/Medium boundary. In the project's density-definition study Sonnet is therefore a **fifth distinct outcome**: Qwen — a small gain; LLaVA — a reliability backfire; Gemma — a severe decline; GPT and Haiku — moderate gains; Sonnet — no change in accuracy, a rebalancing of recall. The counting improvement that accompanies the result is not significant and should not be attributed to the prompt.

---

## 9. Limitations

- Single, non-deterministic run, compared against a single old-prompt run; run-to-run variance was not measured, so neither the density nor the counting difference can be separated from noise (the McNemar p-value of 0.78 does not include it either way).
- The tail analysis defines groups from the model's own outputs and is descriptive.
- Sonnet differs from the open models in scale, architecture, serving and use of adaptive thinking; the comparison cannot attribute differences to any single factor.
- Only effort `medium` was tested; thinking is practically absent at that setting.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Density-definition Experiment A is complete for Claude Sonnet 5.5. Experiment B is also complete (see `Sonnet_DensityDef_ZeroShotB_Findings.md`), so all six Sonnet conditions are done; Haiku, Sonnet and GPT can now be added to the cross-model density-definition synthesis and the final comparison.
