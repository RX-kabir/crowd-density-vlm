# Claude Haiku 5.5 — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples and no YOLO count. The system prompt is the zero-shot prompt with one change: the bare density labels (`0 = Low, 1 = Medium, 2 = High`) are replaced by an explicit visual definition of each class ("judge by how visually packed the crowd appears, not by exact count"; Low = people clearly separated; Medium = moderately close, some overlap but gaps and open space still visible; High = tightly packed, little or no visible space). Identical wording to the Qwen, LLaVA, Gemma and GPT density-definition experiments. `claude-haiku-5-5`, Anthropic Messages API (Message Batches), adaptive thinking, effort **medium**, 512 px images. Sampling parameters cannot be set on this model, so this is a single non-deterministic run (see Section 4 for why that matters for this test).

The comparison baseline throughout is Claude's own zero-shot Experiment A with the original bare-label prompt (`../Zero_Shot/Haiku_ZeroShot_A_Findings.md`).

---

## 1. Headline Results

| Metric | Old prompt (bare labels) | New prompt (with definitions) |
|---|---|---|
| MAE | 482.64 | **278.39** |
| RMSE | 3396.90 | **1845.96** |
| MAPE | 69.81% | **49.19%** |
| Density accuracy | 71.62% | **76.38%** |
| Density precision | 71.33% | 78.50% |
| Density recall | 71.62% | 76.38% |
| Density F1 | 67.09% | **74.62%** |
| Pearson r / Spearman ρ | 0.580 / 0.899 | 0.612 / 0.900 |
| Valid predictions | 1600 / 1600 | 1600 / 1600 |

The new prompt raises density accuracy by 4.8 points and F1 by 7.5 points, and also lowers counting error substantially (Section 4 explains why the counting change should not be attributed to the prompt text alone). It reaches **higher density accuracy than Claude's 5-shot A run** (76.38% vs 74.69%; the difference is not statistically significant: McNemar p = 0.079) and **lower counting error** (MAE 278.39 vs 341.74, MAPE 49.19% vs 91.64%) — without any support example.

**Against the other models' density-definition Experiment A runs (accuracy, old → new prompt):**

| Model | Old prompt | New prompt | Outcome |
|---|---|---|---|
| Qwen2.5-VL-3B | 66.75% | 68.00% | small, significant improvement |
| LLaVA-Interleave-0.5B | 12.71% | 14.52% | not comparable (reliability fell 38.6% → 22.6%) |
| Gemma 3 (4B) | 64.69% | 42.50% | severe, highly significant decline |
| GPT-6.1 Terra | 75.19% | 78.88% | moderate, significant improvement |
| **Claude Haiku 5.5** | **71.62%** | **76.38%** | **moderate, highly significant improvement (McNemar p = 2.5×10⁻⁸)** |

Claude shows the largest gain of any model in the project (+4.8 points; GPT +3.7, Qwen +1.3) but still ends 2.5 points below GPT. Caveat: Claude differs from the open models in scale, architecture, serving and in running with adaptive thinking, and — unlike the open-source runs — it is not deterministic.

**Against YOLO** (MAE 241.87, RMSE 737.65, MAPE 50.64%): the new prompt beats YOLO on MAPE (49.19%) but is still worse on MAE and RMSE.

---

## 2. Response Reliability: Perfect (With One Verbose Response)

| Check | Result |
|---|---|
| Responses ending `end_turn` | 1600 / 1600 |
| Truncated / refused / API errors | 0 / 0 / 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 1,035 characters (1 response) |

1599 responses are exactly `Count: <n>` and `Density: <d>` (1286 with a blank line between them, 313 with a single line break). **One response (image 1200) ignores the format at the start**: it lists the 18 people it can see one by one, then ends with `Count: 18` and `Density: 1`. It parses correctly (true count 18, true density 1), but is the only occurrence in any Claude condition and is the first sign of the model deviating from the bare format. Otherwise reliability is not affected by the longer prompt — the opposite of LLaVA.

---

## 3. Density Classification: A Real Improvement, on Low and Medium

Per-class recall:

| Density | n | Old prompt | New prompt |
|---|---|---|---|
| Low | 222 | 18.0% (40) | **25.2%** (56) |
| Medium | 315 | 23.2% (73) | **52.7%** (166) |
| High | 1063 | **97.2%** (1033) | 94.1% (1000) |

Confusion matrix, new prompt (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 56 | 148 | 18 |
| **True Medium** | 2 | 166 | 147 |
| **True High** | 3 | 60 | 1000 |

Predicted-class shares: Low 3.8%, Medium 23.4%, High 72.8% (old prompt: 2.6% / 15.2% / 82.1%; truth: 13.9% / 19.7% / 66.4%). The over-prediction of "High" falls by 9 points and the Medium share is now slightly *above* the true share (23.4% vs 19.7%). The accuracy of 76.38% (1222 / 1600) is far above the always-"High" baseline of 66.44% (one-sided binomial p = 2.8×10⁻¹⁸).

**Tracking individual images.** 225 density predictions changed between the two prompts: **131 images flipped from an incorrect to a correct density, while 55 flipped the other way** (McNemar's exact test p = 2.5×10⁻⁸). By true class:

| True class | Wrong → right | Right → wrong |
|---|---|---|
| Low | 21 | 5 |
| Medium | **98** | 5 |
| High | 12 | **45** |

The net gain is on Medium (+98 / −5) and Low (+21 / −5), partly paid for by High (−45 / +12). The most common change of label is High → Medium (172 images), followed by Medium → High (24) and Medium → Low (22): the model now reads moderately packed scenes as Medium rather than defaulting to High, but it also pulls 60 genuinely High images into the Medium bin (old prompt: 29). Unlike GPT — whose gain on Medium came with a clear loss on Low — Claude gains on both sparse classes.

The remaining weakness is unchanged in kind: 147 of 315 Medium images (47%) are still called High, and 148 of 222 Low images (67%) are called Medium. The model still rarely calls a scene sparser than the truth (65 images; 313 are called denser).

**Compared with the 5-shot run** (same model): overall the definition reaches the same level (76.38% vs 74.69% accuracy; F1 74.62% vs 73.41%) through a different profile — better Medium and High recall than 5-shot A (52.7% vs 45.4%; 94.1% vs 92.4%) and worse Low recall (25.2% vs 31.5%).

**Compared with GPT-6.1 Terra's density-definition A run** (paired): GPT is right on 108 images where Claude is wrong, Claude on 68 where GPT is wrong (McNemar p = 0.003); the two models give identical density labels on 1411 of 1600 images (88.2%).

---

## 4. Counting: Changed Too — With a Caveat That Matters

Only the density-label section of the prompt changed, so no mechanistic effect on counting would be expected (in the open-source runs, which used greedy decoding, counting did not change significantly). Here counting error falls markedly: **MAE 482.64 → 278.39 (−42%), RMSE 3396.90 → 1845.96 (−46%), MAPE 69.81% → 49.19%** (paired Wilcoxon p = 1.2×10⁻¹¹, paired t-test p = 0.0024; the new prompt has the lower absolute error on 797 images, the old on 592, 211 ties). The mean signed error falls from +368.7 to +131.1; the improvement is concentrated on dense scenes (bias above 1,000 people: +3,811 → +1,475) and in the number of predictions above 10,000 (15 → 9). The median absolute error moves only from 32 to 29, and 21.3% of predictions are within ±10% of the truth (old: 19.1%).

**Why this cannot be read as an effect of the prompt text alone.** Claude Haiku 5.5 is not deterministic and no repeat of the old-prompt run was made, so run-to-run variation is unmeasured. The count prediction differs between the two runs on 1404 of 1600 images (87.8%), although the two sets of predictions are almost perfectly rank-correlated (Spearman ρ = 0.977). Moreover, the longer prompt visibly changes *how much the model thinks* (Section 7): the share of requests answered with a bare answer goes from 1.6% to 40.6%. A change in thinking behaviour is a plausible route from a density-definition paragraph to counting error, but this experiment cannot establish that. The density result is more likely to be genuine than the counting result — it is directional and concentrated in the classes that the definition describes — yet the McNemar p-value does not include the model's own non-determinism.

---

## 5. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 14.3 | 44.5 | −10.1 |
| Medium (1) | 315 | 161.0 | 2037.3 | +89.2 |
| High (2) | 1063 | 368.3 | 1974.5 | +173.0 |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)* Old-prompt MAE on the same strata: Low 21.4, Medium 203.9, High 661.6. The Medium RMSE (2037) is again driven by a single image (3281, true 2,397, predicted 38,500), the same image that received 50,000 under the old prompt.

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 1.8 | +1.4 |
| 11–50 | 378 | 10.8 | +4.2 |
| 51–100 | 301 | 33.2 | +15.3 |
| 101–500 | 625 | 110.1 | +34.1 |
| 501–1,000 | 126 | 492.1 | +134.0 |
| 1,001+ | 112 | 2,682.5 | +1,474.9 |

Across all images 756 are over-counted, 779 under-counted and 65 exact. Removing the 5 worst predictions lowers MAE from 278.39 to 191.31.

**The tail.** Nine predictions (0.6%) exceed 10,000 (old prompt: 15) and account for **39.3%** of the total absolute error; excluding them (post hoc, defined by the model's own outputs, so only descriptive) leaves MAE 169.87 and RMSE 580.11, below YOLO's 241.87 / 737.65 and comparable to GPT's.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 4056 | 6,660 | 45,000 | 38,340 |
| 212 | 9,059 | 47,000 | 37,941 |
| 3281 | 2,397 | 38,500 | 36,103 |
| 3015 | 895 | 15,000 | 14,105 |
| 4159 | 6,210 | 20,000 | 13,790 |
| 4066 | 2,184 | 12,000 | 9,816 |

All are over-counts. Placeholder-style round values (45,000, 47,000, 15,000, 12,000) persist, but the largest prediction is 47,000 (old prompt: 87,412). **Test image 3411 (true count 105)**, the source of the identical prediction 21,482 in eight Qwen and Gemma conditions, is answered 170 (old prompt: 175); the anomaly does not reproduce.

**Same hard images, old vs. new prompt:**

| Image | True | Old prompt | New prompt |
|---|---|---|---|
| 2203 | 4,622 | 87,412 | 4,000 |
| 2542 | 4,113 | 20,000 | 8,000 |
| 4159 | 6,210 | 21,456 | 20,000 |
| 4056 | 6,660 | 45,000 | 45,000 |
| 212 | 9,059 | 45,000 | 47,000 |
| 814 | 8,994 | 1,200 | 120 |
| 3334 | 1,026 | 400 | 1,500 |

The new prompt fixes the worst old over-counts (2203, 2542) but not the cases where the model's count of a very dense scene is simply off by an order of magnitude (4056, 212), and image 814 is now a severe under-count. **Stock answers:** the most frequent values are 180 (56 times; old: 74), 150 (51), 120 (42), 300 (41) and 350 (37); 12.9% of predictions are multiples of 100 (old: 9.4%).

---

## 7. Reasoning and Cost

| Quantity | Old prompt | New prompt |
|---|---|---|
| Requests with a bare answer (output ≤ 15 tokens) | 25 (1.6%) | **649 (40.6%)** |
| Mean / median / max output tokens | 199 / 131 / 1,102 | 141 / 105 / 944 |
| Mean input tokens / request | 425 | 549 |
| Total input / output tokens | 679,327 / 318,520 | 877,727 / 226,299 |
| Cost at Batch prices ($0.05 / $0.25 per 1M tokens; Anthropic's published rates, to be verified) | ≈ $0.11 | ≈ **$0.10** |

The density definition makes the model think *far less*: 649 requests (40.6%) get a bare answer, against 25 before (paired Wilcoxon on output length p ≈ 7×10⁻⁷⁶). Thinking is not reported separately by the API, so output length is used as a proxy. Bare-answer requests are on larger crowds (median true count 165, against 92 for the others) and are more often right on density (85.4% vs 70.2%); MAE is 294.0 for bare answers and 267.7 for the rest. Output length correlates negatively with true count (ρ = −0.26) and with absolute error (ρ = −0.23), and is highest on Low and Medium scenes (mean 249 and 201 tokens against 101 for High) and for images labelled Medium (260). By output-length quartile: ≤ 105 tokens: n = 808, MAE 302.9, density accuracy 87.3%; 106–204: n = 394, MAE 330.4, accuracy 81.0%; above 204: n = 398, MAE 177.1, accuracy 49.7% (these are small crowds, median true count 39, on which the density label is hard). These are associations, not causal claims.

---

## 8. Interpretation

The density definition helps Claude Haiku 5.5: accuracy rises from 71.62% to 76.38% and F1 from 67.09% to 74.62%, with no loss of format reliability apart from one verbose response, and the gain is statistically firm on the paired test (131 images fixed vs 55 broken). It operates mostly on the Medium class (recall 23.2% → 52.7%), also helps Low (18.0% → 25.2%), and costs some High recall (97.2% → 94.1%). The model's predicted class mix moves from 82.1% "High" to 72.8%, towards the true 66.4%. In the project's density-definition study Claude joins GPT as a model whose earlier calibration (a boundary placed too low, with 77% of Medium images called High) was poor enough that a written rule helped, whereas Gemma's good implicit judgement was overridden and LLaVA could not follow the longer prompt; Claude's gain (+4.8 points) is the largest observed. The definition lifts zero-shot density accuracy above the 5-shot result, but it does not beat GPT (78.88%).

Two qualifications. First, the sparse end of the scale is still not fixed by definition: Low recall is 25.2%, and two thirds of Low images are labelled Medium. Second, the counting improvement that accompanies the density result — and the change in how much the model thinks — means that the prompt probably altered more than just the label rule; the counting gain should not be read as a property of the definition and the whole result would be firmer with a measurement of the model's run-to-run variance.

---

## 9. Limitations

- Single, non-deterministic run (no sampling control on this model), compared against a single old-prompt run; run-to-run variance was not measured, so neither the density nor the counting difference can be fully separated from noise.
- Thinking effort is inferred from output length; the large change in the share of bare answers is an observation, not an explanation.
- Claude differs from the open models in scale, architecture, serving and use of adaptive thinking; the comparison cannot attribute differences to any single factor.
- Token prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

Density-definition Experiment A is complete for Claude Haiku 5.5. Experiment B (with the YOLO count) has not yet been run. After it, Claude and GPT can be added to the cross-model density-definition synthesis and the final comparison.
