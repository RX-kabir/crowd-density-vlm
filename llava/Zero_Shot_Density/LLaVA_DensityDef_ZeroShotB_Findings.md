# LLaVA-Interleave (0.5B) — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set.

---

## 1. Headline Results

| Metric | Old Prompt | New Prompt (with definition) |
|---|---|---|
| MAE | 233.42 | 235.07 |
| Format-valid rate | 99.9% (1599/1600) | 99.9% (1598/1600) |
| Density Accuracy | 14.56% | 14.20% |

---

## 2. Reliability: Rescued by the YOLO Anchor, Unlike Experiment A

Experiment A showed the density definition worsening LLaVA's format-following reliability substantially (38.6% → 22.6%). Experiment B shows no such collapse — reliability stays at 99.9% in both conditions. The presence of a concrete YOLO number to anchor to appears to stabilize the model's output format regardless of prompt length, resolving the open question raised before this run: the Experiment A backfire does not generalize to Experiment B.

---

## 3. Density Accuracy: Small but Statistically Significant Worsening

| Density | Old Prompt | New Prompt |
|---|---|---|
| Low | 100.0% | 100.0% |
| Medium | 3.5% | 1.6% |
| High | 0.0% | 0.0% |

Image-level tracking: 0 images flipped wrong→correct, 6 flipped correct→wrong. McNemar's exact test: **p = 0.031** — a small but real negative effect. Both conditions remain dominated by near-total collapse to "Low" (98%+ of predictions), so this is a minor worsening of an already-severe problem rather than a meaningful behavioral change.

---

## 4. Counting: No Significant Change

MAE is essentially flat (233.42 → 235.07), and a paired significance test confirms this: **Wilcoxon p = 0.808**. Consistent with expectations — this prompt change targets density, not counting.

---

## 5. Substitution Rate: Essentially Unchanged

| | Old Prompt | New Prompt |
|---|---|---|
| Exact YOLO echo rate | 95.8% | 93.8% |

A small decrease, likely not meaningful given both figures represent overwhelming, near-total substitution either way.

---

## 6. A Notable Break in the Recurring Anomaly

Test image 3411 — which has hallucinated the identical value 21,482 in ten separate instances elsewhere in this project (both Qwen and Gemma, every condition tested) — does **not** do so here. Instead, LLaVA predicts 110, closely matching the true count of 105, because the YOLO detector happened to give an accurate count (110) for this specific image and LLaVA's extreme substitution rate (93.8%) means it simply echoed that accurate value.

This is a useful piece of confirming evidence for the project's central substitution-rate finding: LLaVA "avoids" this particular failure not through better independent visual judgment, but by chance — because it defers almost entirely to an external number that happened to be correct here. Qwen and Gemma, which substitute far less (1–58% depending on condition), continue to hallucinate on this image regardless of what YOLO reports, because they are relying on their own (apparently faulty) internal processing of it rather than an external anchor.

---

## 7. Interpretation

Combined with Experiment A, the picture for LLaVA is consistent: the density definition provides no meaningful benefit and, where it has any measurable effect, moves in the negative direction — a severe reliability backfire in the zero-shot-only condition (A), and a small but statistically significant worsening of density accuracy in the YOLO-assisted condition (B). This stands in clear contrast to Qwen, where the same definition produced small but genuine improvements in both experiments. The pattern reinforces the finding from Experiment A: prompt-clarity interventions do not transfer uniformly across model scale, and the smallest model in this project is measurably worse off for a change that helped a larger one.

---

## 8. Status

LLaVA's density-definition test is now complete for both Experiment A and B. Per your supervisor's request, Gemma is the remaining model to test.
