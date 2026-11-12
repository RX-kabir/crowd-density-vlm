# Qwen2.5-VL-3B — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and a system prompt describing the task. This is a new condition, additional to (not replacing) the existing 5-shot results.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 725.92 |
| RMSE | 2469.95 |
| MAPE | 194.24% |
| n (valid) | 1600 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 66.75% |
| Precision | 63.42% |
| Recall | 66.75% |
| F1-score | 54.85% |

---

## 2. Central Finding: Density "Accuracy" Is Misleading Here — the Model Has Collapsed to the Majority Class

A trivial baseline that always predicts "High" density, regardless of image content, would score **66.44% accuracy** on this test set, since High-density images make up 1063 of 1600 (66.4%) of the total. The model's actual accuracy — **66.75%** — is statistically indistinguishable from this trivial baseline, a difference of 0.3 percentage points.

Per-class recall confirms this directly:

| Density | Recall |
|---|---|
| Low | 1.8% (4/222) |
| Medium | 2.5% (8/315) |
| High | 99.3% (1056/1063) |

The model predicted "High" for 1562 of 1600 images (97.6% of all predictions). It is not meaningfully discriminating crowd density without support examples to calibrate against — it has collapsed to guessing the majority class almost universally. **Accuracy alone would misrepresent this as competent performance; F1-score (54.85%, well below accuracy) reflects the real picture.** This is a stark illustration of why weighted F1 was included alongside accuracy throughout this project, and a clean, citable example for a methods discussion on why accuracy alone is an insufficient metric for imbalanced classification.

---

## 3. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 27.6 | 154.9 | +1.4 |
| Medium (1) | 315 | 107.8 | 421.9 | +8.5 |
| High (2) | 1063 | **1054.9** | 3020.7 | **+867.0** |

*(bias = mean signed error, predicted − ground truth; positive = overcounts.)*

Counting error on Low and Medium images is actually reasonable — comparable to or better than the 5-shot condition. High-density counting error, however, is catastrophic (MAE over 1,000, more than double the 5-shot condition's already-poor 551.6), driven by extreme outlier hallucinations concentrated specifically on the densest scenes.

---

## 4. Correlation With Ground Truth

- **Pearson r = 0.563**
- **Spearman ρ = 0.794**

Both are notably *higher* than the 5-shot Experiment A's correlation (Pearson 0.243). This is not a contradiction with the poor MAE — it indicates the model's general sense of relative crowd size (which images are bigger than others) is reasonably good in zero-shot, arguably better than with support examples present, but a handful of catastrophic outliers (below) dominate the absolute-error metrics.

---

## 5. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 2542 | 4,113 | 50,000 | 45,887 |
| 2070 | 6,073 | 50,000 | 43,927 |
| 212 | 9,059 | 50,000 | 40,941 |
| 3411 | 105 | 21,482 | 21,377 |
| 814 | 8,994 | 50 | 8,944 |
| 3178 | 7,560 | 50 | 7,510 |

Two qualitative patterns stand out:

1. **A new, more extreme hallucination placeholder: exactly 50,000**, appearing on three separate images. This is a more extreme fallback value than the "10,000" placeholder seen in the 5-shot condition — removing support examples appears to have removed a calibrating influence on the *scale* of the model's hallucinations, not just their frequency.
2. **Test image 3411 again produces the identical extreme value (21,482)** seen previously in Qwen 5-shot Experiment A, Qwen 5-shot Experiment B, and both Gemma experiments. This is now confirmed across five separate experimental conditions spanning two model families and two prompting strategies (5-shot and zero-shot) — very strong evidence this specific failure is a property of the image itself rather than of any particular prompt design or auxiliary input.

---

## 6. Interpretation

Removing support examples has a sharply divergent effect depending on which task is measured. Density classification effectively breaks down entirely, collapsing to a majority-class guess. Counting accuracy on sparse-to-moderate scenes holds up reasonably well and rank-correlates with truth better than the 5-shot condition — but high-density counting becomes substantially worse, driven by more extreme hallucinated placeholder values than were seen with support examples present. This suggests support examples serve at least two distinct functions: providing density-calibration signal (whose removal causes the classification collapse) and constraining the scale of the model's hallucinations under uncertainty (whose removal produces more extreme outliers, not just more frequent ones).

---

## 7. Status

Zero-shot Experiment B (test image + YOLO count only, no support examples) has not yet been run for Qwen. LLaVA and Gemma zero-shot experiments have not yet started.
