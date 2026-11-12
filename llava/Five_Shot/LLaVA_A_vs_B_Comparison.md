# LLaVA-Interleave (0.5B) — Experiment A vs. Experiment B: Comparison

**Status:** Both experiments complete on the full 1600-image JHU-CROWD++ test set. Experiment B uses the identical prompt as Experiment A, with one addition — a two-line statement giving the YOLO-predicted count for the test image.

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 503.34 | **321.11** |
| RMSE | 1184.49 | **784.55** |
| MAPE | 1013.03% | **524.81%** |
| Valid predictions | 1577 / 1600 | 1597 / 1600 |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | **47.96%** | 37.75% |
| Precision | 51.53% | 50.26% |
| Recall | **47.96%** | 37.75% |
| F1-score | **49.51%** | 41.40% |

---

## 2. Density-Stratified Counting Error

| Density | Exp. A — MAE / Bias | Exp. B — MAE / Bias |
|---|---|---|
| Low (0) | 472.8 / +437.9 | 243.7 / +193.1 |
| Medium (1) | 380.9 / +276.5 | 168.5 / +33.4 |
| High (2) | 545.9 / −35.5 | 382.5 / −233.9 |

*(bias = mean signed error, predicted − ground truth; positive = overcounts, negative = undercounts.)*

Error improves at every density level from A to B, most sharply on Low and Medium. Bias direction is positive (overcounting) in Experiment A across the board and becomes mixed in Experiment B — positive on sparse scenes, negative on dense ones.

---

## 3. Statistical Significance

Paired comparison of absolute error on the 1574 images with a valid prediction in both experiments:

- Wilcoxon signed-rank test: W = 186,814, **p = 4.2×10⁻⁶¹**
- Paired t-test: t = 7.82, **p = 9.4×10⁻¹⁵**
- Mean absolute error: 500.2 (A) → 321.4 (B)
- Median absolute error: 149 (A) → 78 (B)

The reduction in error from adding the YOLO count is statistically decisive, not attributable to chance.

---

## 4. Source of the Predicted Count

| Behavior | Experiment A | Experiment B |
|---|---|---|
| Echoes a support example's count | 81.7% | 24.2% |
| Echoes the YOLO count | — | 62.6% |
| Independent / own answer | 18.3% | 13.3% |

This table is the key to interpreting the improvement. In Experiment A, the model's dominant behavior is copying one of the 5 labelled support-example counts shown in the prompt — most often the first one — rather than estimating from the test image itself, and this carries essentially no information about the true count (correlation with ground truth ≈ 0). In Experiment B, that behavior is largely *replaced*: the model instead defers to the YOLO count 62.6% of the time. This is a better anchor, since it is at least derived from the actual test image, and it is also empirically the model's most accurate mode in Experiment B (MAE 235 when echoing YOLO vs. 490 when still echoing a support example).

---

## 5. Interpretation

**Adding the YOLO count substantially and significantly improves LLaVA's counting accuracy** — MAE and MAPE roughly halve, and the improvement holds up under a paired significance test. This does not, however, indicate that the model became a better independent visual estimator. The mechanism is a substitution: Experiment A's dominant failure mode (copying an arbitrary support-example number) is replaced by a different anchor (the YOLO count) that happens to correlate better with the truth. Because YOLO's own count is subject to a well-known failure mode — severe undercounting on very dense, heavily-occluded crowds — Experiment B inherits that same bias on the High-density stratum (−233.9), even as its overall accuracy improves.

**Density classification moves in the opposite direction** — accuracy drops from 48.0% to 37.8% — the same count-improves/density-doesn't-improve pattern observed elsewhere in this project. Since both tasks depend on the same underlying scene understanding, this is consistent with the YOLO count anchoring the numeric answer without improving (and possibly mildly displacing) the model's broader judgment about crowd density.

---

## 6. Status

LLaVA Experiment A and B are both complete. Next: Gemma (Experiments A and B), followed by the final three-way comparison (Qwen vs. LLaVA vs. Gemma).
