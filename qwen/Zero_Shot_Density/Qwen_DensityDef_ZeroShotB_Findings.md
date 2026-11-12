# Qwen2.5-VL-3B — Zero-Shot Experiment B: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set.

---

## 1. Headline Results

| Metric | Old Prompt | New Prompt (with definition) |
|---|---|---|
| MAE | 262.36 | 258.27 |
| RMSE | 922.89 | 909.44 |
| Density Accuracy | 65.81% | 66.69% |
| Density F1 | 55.71% | 58.40% |

---

## 2. Density: Same Direction of Improvement as Experiment A, But Not Statistically Significant

| Density | Old Prompt | New Prompt |
|---|---|---|
| Low | 2.3% | 5.9% |
| Medium | 6.0% | 10.2% |
| High | 96.8% | 96.1% |

Image-level tracking: 38 flipped wrong→correct, 24 flipped correct→wrong. McNemar's exact test: **p = 0.098** — not significant at conventional thresholds, in contrast to Experiment A's clean, significant result (p = 0.0008) on the same prompt change. The direction of the effect is consistent with A, but weaker and noisier here.

---

## 3. Counting: Small but Statistically Significant Improvement

MAE barely moves (262.36 → 258.27), but a paired test says this is real: **Wilcoxon p = 3.1×10⁻¹⁴**. A small, highly consistent shift across many images, not driven by a few large changes.

---

## 4. A Plausible Explanation for Both Results: Increased YOLO Substitution

| | Old Prompt | New Prompt |
|---|---|---|
| Exact YOLO echo rate | 46.2% | **57.9%** |

Adding the density definition made the system prompt substantially longer and more complex. One plausible mechanism for the pattern in Sections 2–3: the model appears to lean *more* on the YOLO count as a shortcut under this longer prompt, which would explain a modest but consistent counting improvement (more reliance on YOLO's generally-adequate number) alongside a weaker density effect (less attention available for applying the new definition thoughtfully when more of the response is effectively "copy the given number"). This is a hypothesis suggested by the data, not a directly proven mechanism — worth flagging as such if included in the paper.

---

## 5. Density-Stratified Counting Error (new prompt)

| Density | n | MAE | Bias |
|---|---|---|---|
| Low | 222 | 33.9 | −28.1 |
| Medium | 315 | 86.5 | −59.3 |
| High | 1063 | 356.0 | −250.3 |

Broadly similar shape to the old prompt's B results — undercounting bias growing with density, consistent with continued reliance on YOLO's own undercounting tendency.

---

## 6. Worst Cases and the Recurring Anomaly

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 3411 | 105 | **21,482** | 110 | 21,377 |
| 814 | 8,994 | 6 | 6 | 8,988 |
| 3178 | 7,560 | 10 | 9 | 7,550 |
| 4056 | 6,660 | 10 | 10 | 6,650 |
| 3539 | 6,757 | 300 | 300 | 6,457 |

Every worst case except 3411 is an exact or near-exact YOLO echo. **Image 3411 again produces 21,482** — now a tenth confirmed instance of this anomaly across the project, occurring under the density-definition prompt as well, with an accurate YOLO count (110) supplied and ignored.

---

## 7. Density-Definition A vs. B (Internal Comparison)

Within the density-definition prompt itself, B still shows a large, highly significant counting improvement over A (Wilcoxon p = 4.6×10⁻³⁷, mean absolute error 694.18 → 258.27) — confirming the core A-vs-B pattern established throughout this project holds under the new prompt too.

---

## 8. Interpretation

The density definition's benefit, clearly established in Experiment A, does not carry over as cleanly to Experiment B — same direction, weaker magnitude, not statistically significant. The most likely explanation is a genuine interaction between the two prompt elements: a longer, more detailed system prompt combined with a concrete auxiliary number to anchor to appears to increase reliance on that number, at some cost to the density definition's effectiveness. This is a nuanced but useful finding — it suggests prompt improvements aimed at one task (density) can have secondary effects on model behavior in a different part of the same prompt (counting reliance), which is worth testing further, though not necessarily worth re-engineering the prompt over at this stage.

---

## 9. Status

Qwen's density-definition test is now complete for both Experiment A and B. Per your supervisor's request, the same test should next be run on LLaVA and Gemma.
