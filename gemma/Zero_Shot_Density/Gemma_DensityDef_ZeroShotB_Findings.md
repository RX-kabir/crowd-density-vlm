# Gemma 3 (4B) — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set. Result: a severe, highly significant density degradation — worse even than Experiment A's already-severe collapse.

---

## 1. Headline Results

| Metric | Old Prompt | New Prompt (with definition) |
|---|---|---|
| MAE | 234.54 | 245.46 |
| RMSE | 882.49 | 926.05 |
| Density Accuracy | **64.69%** | **37.44%** |
| Density F1 | 63.28% | 36.35% |

---

## 2. Density: The Collapse From Experiment A Deepens Further

| Density | Old Prompt Recall | New Prompt Recall |
|---|---|---|
| Low | 1.8% | **0.0%** |
| Medium | 67.0% | **94.0%** |
| High | 77.1% | **28.5%** |

Predicted-density distribution collapsed almost entirely to two categories: 1,276 of 1,600 predictions (79.75%) are "Medium," 324 are "High," and **zero are "Low."** McNemar's exact test on the flips (90 wrong→correct, 526 correct→wrong): **p = 7.36×10⁻⁷⁶** — an even more extreme result than Experiment A's already-overwhelming p = 1.1×10⁻⁵⁶, and the single most statistically extreme result anywhere in this project's density-definition study.

---

## 3. Answering the Question This Run Was Meant to Test

Before this run, the open question was whether a concrete YOLO count might counteract the Medium-over-triggering seen in Experiment A — a very large detected count being hard to reconcile with "Medium." **The data says no: the collapse gets worse, not better, with the YOLO count present.** Substitution rate stayed low and essentially unchanged (0.8% vs. Experiment A's context of similarly minimal reliance), meaning Gemma is not simply substituting the YOLO count in place of its own count judgment — the density-collapse mechanism appears to operate independently of how much the model leans on YOLO numerically.

---

## 4. Counting: Small but Statistically Significant Change

MAE increases slightly (234.54 → 245.46); a paired test confirms this is a real, if practically minor, effect (Wilcoxon p = 6.3×10⁻¹¹) — consistent with a broad, small, systematic shift across many images from the longer prompt, similar in character to the tiny-but-significant counting shifts observed in the other two models' density-definition tests.

---

## 5. Interpretation

This result extends and reinforces Experiment A's finding rather than complicating it: the density definition's mismatch with Gemma's own internal (and apparently better-calibrated) sense of the Medium/High boundary is not something the presence of auxiliary detector information corrects — if anything, the longer combined prompt (definition + YOLO block) pushes the collapse further, with Low-density recognition disappearing entirely. Combined with Experiment A, this gives a consistent, replicated picture across both YOLO conditions: the definition is actively harmful for this model, not just under one specific prompt configuration.

---

## 6. Status

This completes the density-definition study for Gemma, and for all three models overall. See `DensityDef_CrossModel_Synthesis.md` for the full cross-model comparison and recommendation.
