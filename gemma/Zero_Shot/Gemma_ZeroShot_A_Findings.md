# Gemma 3 (4B) — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and the zero-shot system prompt (identical text to Qwen's and LLaVA's zero-shot experiments).

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 332.24 |
| RMSE | 2687.40 |
| MAPE | 61.82% |
| Valid predictions | 1599 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 64.69% |
| Precision | 77.01% |
| Recall | 64.69% |
| F1-score | 63.17% |

---

## 2. A Distinctive Collapse Pattern — Partial, Not Total

Unlike Qwen (which collapsed almost entirely to predicting "High") or LLaVA (which collapsed almost entirely to a single class in both zero-shot conditions), Gemma's zero-shot density judgment degrades unevenly:

| Density | Recall |
|---|---|
| Low | 1.8% |
| **Medium** | **62.9%** |
| High | 78.4% |

Low-density recall fails badly, consistent with every other model's zero-shot behavior in this project — but Medium and High retain real, functional discrimination between them. This is a materially different failure mode from a full majority-class collapse: Gemma appears to specifically lose the ability to recognize sparse scenes without support examples to calibrate against, while retaining a workable sense of "how crowded" among denser scenes.

---

## 3. Density-Stratified Counting Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 24.4 | 139.4 | −19.4 |
| Medium (1) | 315 | 70.8 | 188.9 | −63.7 |
| High (2) | 1063 | 474.2 | **3295.4** | −50.4 |

*(bias = mean signed error, predicted − ground truth.)* The High-density stratum's RMSE is nearly 7× its MAE — a clear signature of a small number of extreme outliers dominating that group's error, detailed in Section 5.

---

## 4. Correlation With Ground Truth

- **Pearson r = 0.379**
- **Spearman ρ = 0.854** — the highest of any experiment in this project

This continues a pattern visible in both Qwen and Gemma: removing support examples improves the model's general sense of relative crowd ordering (Spearman), while simultaneously removing whatever was constraining the *scale* of its worst hallucinations (driving Pearson and raw error metrics down). Better rank-sense, worse absolute accuracy, at the same time — not a contradiction, but two different properties moving in opposite directions for the same underlying reason.

---

## 5. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 4159 | 6,210 | **75,000** | 68,790 |
| 4056 | 6,660 | **75,000** | 68,340 |
| 2203 | 4,622 | 35,000 | 30,378 |
| 3411 | 105 | **21,482** | 21,377 |
| 2592 | 2,069 | 12,000 | 9,931 |
| 3334 | 1,026 | 8,000 | 6,974 |

Two findings here stand out beyond this project's usual pattern of round-number hallucination:

1. **75,000 is a new record placeholder value**, appearing twice, more extreme than any previous hallucination magnitude observed (the prior record was 50,000, from Qwen's zero-shot Experiment A).
2. **Test image 3411 again produces the identical extreme value, 21,482** — now observed in **seven separate experimental conditions**: Qwen 5-shot A, Qwen 5-shot B, Gemma 5-shot A, Gemma 5-shot B, Qwen zero-shot A, Qwen zero-shot B, and this run. This spans both model families, both prompting strategies, and both YOLO conditions. This is now one of the most robust qualitative findings in the entire project and warrants a dedicated case-study figure in the paper — the consistency of this specific value on this specific image, across so many independent conditions, is very unlikely to be coincidental.

---

## 6. Interpretation

Gemma's zero-shot degradation is real but more contained and more structured than what was observed in the other two models. Rather than a full collapse to a single density label or a small set of placeholder count values, Gemma retains partial, functional density discrimination (Medium vs. High) and a genuinely improved rank-ordering sense of crowd size (highest Spearman correlation observed in this project) — at the cost of losing calibration on the *scale* of its estimates, producing occasional extreme outliers that dominate aggregate error metrics, and losing the ability to recognize sparse (Low-density) scenes specifically. This is consistent with Gemma's generally stronger performance across every other experiment in this project, and suggests the model's underlying scene-understanding capability degrades more gracefully than the smaller/differently-architected models when support-example scaffolding is removed — while still being far from immune to it.

---

## 7. Status

Zero-shot Experiment B (test image + YOLO count, no support images) has not yet been run for Gemma. This will complete zero-shot coverage for all three models.
