# Gemma 3 (4B) — Zero-Shot: Findings & Comparison (Experiment A vs. B)

**Status:** Both zero-shot experiments complete on the full 1600-image JHU-CROWD++ test set. This completes zero-shot coverage for all three models (Qwen2.5-VL-3B, LLaVA-Interleave-0.5B, Gemma 3 4B).

---

## 1. Headline Results

**Counting**

| Metric | Experiment A (no YOLO) | Experiment B (with YOLO) |
|---|---|---|
| MAE | 332.24 | 234.54 |
| RMSE | 2687.40 | 882.49 |
| MAPE | 61.82% | 56.67% |
| Valid predictions | 1599 / 1600 | **1600 / 1600** |

**Density classification**

| Metric | Experiment A | Experiment B |
|---|---|---|
| Accuracy | 64.69% | 64.69% |
| Precision | 77.01% | 77.70% |
| Recall | 64.69% | 64.69% |
| F1-score | 63.17% | 63.28% |

Density metrics are essentially unchanged between conditions — accuracy is identical to two decimal places.

---

## 2. Central Finding: the Counting Improvement Is Not Statistically Significant

Paired comparison of absolute error (n=1599, after excluding the one image unparseable in Experiment A): **Wilcoxon signed-rank p = 0.216; paired t-test p = 0.093.** Neither reaches conventional significance.

This is the first non-significant A→B comparison anywhere in this project — every other model, in both prompting conditions, showed a statistically significant change (often overwhelmingly so, with p-values as extreme as 10⁻⁶¹). The mechanism is directly visible in Section 3: with only 1.3% of predictions exactly matching the YOLO count, there is no substitution effect to drive a systematic, reliable shift. The lower raw MAE in Experiment B should not be read as evidence the YOLO count reliably helps Gemma in the zero-shot setting — the data doesn't support that claim at conventional confidence levels.

---

## 3. Mechanism: Gemma Remains Almost Entirely Independent of the YOLO Count

**Only 21 of 1600 predictions (1.3%) exactly match the YOLO count given** — even lower than Gemma's own 5-shot Experiment B rate (1.1%, itself already the lowest substitution rate observed for any model in this project). This is a striking contrast with the other two models' zero-shot Experiment B behavior: LLaVA reached 95.8% exact YOLO-echo, Qwen reached 46.2%. Across both prompting conditions tested, Gemma consistently does not lean on the auxiliary count as an anchor the way the other two models do.

---

## 4. Density-Stratified Counting Error

| Density | Exp. A — MAE / Bias | Exp. B — MAE / Bias |
|---|---|---|
| Low (0) | 24.4 / −19.4 | 30.6 / −28.4 |
| Medium (1) | 70.8 / −63.7 | 74.8 / −70.2 |
| High (2) | 474.2 / −50.4 | 324.5 / −267.8 |

High-density MAE improves substantially in raw terms (474.2 → 324.5), but per Section 2 this should not be read as a reliable effect — the paired significance test says otherwise. Bias becomes more negative (more undercounting) at every density level in B, a small directional pull toward YOLO's own undercounting tendency, consistent with the low but non-zero engagement implied by the 1.3% echo rate.

---

## 5. Correlation With Ground Truth

| Condition | Pearson r | Spearman ρ |
|---|---|---|
| Experiment A | 0.379 | 0.854 |
| Experiment B | 0.192 | 0.835 |

Both correlation measures are essentially similar to (Spearman) or lower than (Pearson) Experiment A's — again consistent with the YOLO count not meaningfully changing the model's underlying behavior.

---

## 6. A Recurring Anomaly, Now Confirmed Eight Times

Test image 3411 (true count 105) again produced **the identical extreme prediction of 21,482** — the same value now observed in all four of this project's Qwen and Gemma conditions (5-shot A, 5-shot B, zero-shot A, zero-shot B), for both models, with an accurate YOLO count (110) provided and evidently ignored in both Gemma runs. This is the single largest error in this run by a wide margin and is now one of the most robust, independently-reproduced qualitative findings in the entire project — strong evidence of a fixed property of this specific image rather than of any model, prompt, or auxiliary input.

**Other worst-case examples (Experiment B):**

| test_filename | true count | predicted | YOLO count | abs. error |
|---|---|---|---|---|
| 3411 | 105 | 21,482 | 110 | 21,377 |
| 814 | 8,994 | 35 | 6 | 8,959 |
| 212 | 9,059 | 300 | 1 | 8,759 |
| 3178 | 7,560 | 12 | 9 | 7,548 |
| 4056 | 6,660 | 12,000 | 10 | 5,340 |

Aside from 3411, the remaining largest errors are severe undercounts on extremely dense scenes, loosely tracking (though not exactly matching) the also-severely-undercounting YOLO input.

---

## 7. Interpretation

Gemma's zero-shot behavior is consistent across both experimental conditions in a way none of the other model/condition combinations in this project have shown: response reliability stays near-perfect, density judgment is essentially unaffected by the auxiliary count, and — critically — the model does not substitute the YOLO number for its own judgment to any meaningful degree. The apparent counting improvement in Experiment B is not statistically reliable, which is itself an important, honest finding: it demonstrates that "auxiliary information significantly helps" is not a universal property even within a single model family, but depends on how much the model actually engages with that information — and Gemma, across every condition tested in this project, engages with it the least.

---

## 8. Status

**Zero-shot experiments are now complete for all three models.** Combined with the completed 5-shot experiments, this gives a full 2×2×3 design (prompting strategy × YOLO condition × model) for the final cross-model synthesis. The VisDrone-mismatched-YOLO robustness check remains pending for all three models under the 5-shot condition.
