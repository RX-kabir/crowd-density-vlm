# Qwen2.5-VL-3B — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set. This tests whether adding an explicit visual definition of Low/Medium/High density (rather than leaving the labels undefined) changes model behavior, following your supervisor's request to validate the change before extending it to the other models.

---

## 1. Headline Results

| Metric | Old Prompt (bare labels) | New Prompt (with definition) |
|---|---|---|
| MAE | 725.92 | 694.18 |
| RMSE | 2469.95 | 2692.04 |
| Density Accuracy | 66.75% | **68.00%** |
| Density F1 | 54.85% | 58.02% |

---

## 2. Density Classification: A Real, Statistically Significant Improvement

Per-class recall:

| Density | Old Prompt | New Prompt |
|---|---|---|
| Low | 1.8% | **5.4%** |
| Medium | 2.5% | **7.3%** |
| High | 99.3% | 99.1% |

Tracking individual images rather than aggregate accuracy: **27 images flipped from an incorrect to a correct density prediction, while only 7 flipped the other way.** A statistical test on this pattern (McNemar's exact test) gives **p = 0.0008** — a genuine, non-random effect, despite the modest scale of the underlying accuracy change.

**Important context on scale:** while statistically real, the absolute improvement is small. Low and Medium recall roughly triple but remain far from good (5.4% and 7.3%) — the model still predicts "High" for the large majority of sparse and moderate-density images. This is a measurable step in the right direction, not a fix for the underlying collapse.

---

## 3. A Methodological Note Worth Recording

A 25-image diagnostic sample, deliberately chosen to include many of the old prompt's density errors, initially suggested this prompt change made no difference at all (1 change, 0 improvements). The full 1600-image result contradicts that: a real, significant effect exists, but at a low enough rate (27/1600 ≈ 1.7% of images) that a 25-image sample had a real chance of missing it — and did. This is worth noting in the paper's methodology if the small-sample check is mentioned at all: it demonstrates why a full-scale run is necessary before concluding a prompt change has no effect, particularly for modest-sized effects.

---

## 4. Counting Performance: No Meaningful Change

MAE improves slightly (725.92 → 694.18) but a paired significance test (Wilcoxon) gives **p = 0.345** — not significant. This is expected: only the density-labels section of the prompt changed, and there is no mechanistic reason it should affect counting behavior. The extreme-outlier hallucination pattern is untouched — test image 3411 again produces the identical value 21,482 (now a ninth confirmed instance of this anomaly across the project), and a new 50,000 placeholder hallucination appears on a previously-unseen image (filename 4066).

---

## 5. Density-Stratified Counting Error

| Density | n | MAE | Bias |
|---|---|---|---|
| Low | 222 | 28.7 | −20.4 |
| Medium | 315 | 99.5 | −21.3 |
| High | 1063 | 1009.4 | +809.1 |

Broadly similar in shape to the old prompt's stratified error, consistent with counting behavior being largely unaffected by this change.

---

## 6. Interpretation

The density definition produces a small but genuine improvement in density classification, concentrated in correctly identifying some previously-misclassified Low and Medium density images, with no effect on counting. This supports a more precise diagnosis than either "the definition doesn't help" (contradicted by the full-scale significance test) or "the definition fixes the problem" (contradicted by the still-poor absolute recall on Low/Medium). The most accurate characterization: **explicit definitions provide a modest, statistically real benefit, but the dominant cause of zero-shot density collapse lies elsewhere** — most plausibly in how much weight the model gives to instructions stated only in the system prompt versus reinforced through demonstrated examples, which zero-shot prompting removes entirely.

---

## 7. Status

Qwen zero-shot Experiment B with the density-definition prompt is the next planned step, followed by the same test across LLaVA and Gemma, per your supervisor's request to check this across all three models.
