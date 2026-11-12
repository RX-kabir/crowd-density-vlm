# Gemma 3 (4B) — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set. Result: the density definition causes a severe, highly significant **degradation** in density accuracy — the most dramatic effect (in either direction) of any density-definition test run in this project.

---

## 1. Headline Results

| Metric | Old Prompt | New Prompt (with definition) |
|---|---|---|
| MAE | 332.24 | 326.50 |
| Density Accuracy | **64.69%** | **42.50%** |
| Density F1 | 63.17% | 42.85% |

---

## 2. The Central Finding: Mass Reclassification of High → Medium

| Density | Old Prompt Recall | New Prompt Recall |
|---|---|---|
| Low | 1.8% | 0.9% |
| Medium | 62.9% | **90.5%** |
| High | 78.4% | **37.0%** |

Predicted-density distribution shifted sharply toward "Medium": 623 → 1,171 of 1,600 predictions. Critically, **all 445 images that flipped from correct to incorrect** — previously correctly identified as High-density — were reclassified specifically as **Medium**, not Low. This is not noise; it's a systematic shift in where Gemma now draws the High/Medium boundary.

McNemar's exact test on the full set of flips (93 wrong→correct, 448 correct→wrong): **p = 1.05×10⁻⁵⁶** — the most statistically extreme result of any density-definition experiment in this project, in either direction.

---

## 3. Why This Model, Specifically

Gemma's original zero-shot Experiment A was distinctive among the three models tested: it already showed genuine, functional discrimination between Medium and High density (recall 62.9% and 78.4% respectively) rather than collapsing to a single majority class the way Qwen and LLaVA did. The most likely explanation for this result: **the explicit written definition overrides an already-reasonable internal judgment with a stricter rule that doesn't match where Gemma had already learned to draw the boundary.** The new Medium definition's wording — "gaps and open space are still visible" — appears to be satisfied by many genuinely High-density scenes that have *some* visible gaps somewhere in the frame, even when overall very crowded, pulling Gemma's threshold for calling something "High" considerably stricter than its own prior (better-calibrated) implicit judgment.

This is a meaningfully different failure mode from what was seen in the other two models:
- **Qwen** had no strong prior density judgment to override — the definition filled a genuine gap, producing a small, real improvement.
- **LLaVA** showed a reliability backfire (worse format-following under a longer prompt) rather than a judgment-boundary shift.
- **Gemma** had a good prior judgment that the definition actively disrupted — arguably the most instructive failure mode for prompt design, since it shows an intervention harming a case that didn't need fixing.

---

## 4. Counting: Statistically Significant but Practically Negligible

MAE barely changes (332.24 → 326.50), yet a paired test says this is significant (Wilcoxon p = 7.2×10⁻⁵⁶) — consistent with a broad, small, systematic shift across many images rather than a meaningful practical difference. Correlation remains similar (Pearson 0.277, Spearman 0.844, both close to the original run's figures).

---

## 5. Interpretation

Across all three models tested, the same density-definition text produces three qualitatively different outcomes: a small genuine improvement (Qwen), a reliability backfire with density largely unaffected (LLaVA), and a severe density degradation in a model that previously had the best density behavior of the three (Gemma). This is a strong, well-evidenced argument against assuming a "clearer instructions always help" model of prompt engineering — the effect of an explicit definition depends heavily on whether it aligns with, is neutral to, or actively conflicts with a given model's pre-existing (and not directly observable) internal representation of the concept being defined. For a paper, this triad of results is considerably more interesting than any single outcome alone would have been.

---

## 6. Status

Gemma's density-definition test for Experiment A is complete, showing a clear and severe backfire. Experiment B is the next and final planned step to complete this test across all three models.
