# Final Cross-Model Comparison — All 3 Models, Both Prompting Strategies

**Scope:** Qwen2.5-VL-3B, LLaVA-Interleave-0.5B, and Gemma 3 (4B), each under 5-shot and zero-shot prompting, each with and without an auxiliary YOLO count (12 conditions total), plus the YOLO baseline. All experiments use manually-annotated, cross-verified density labels and an identical prompt text across models (adapted only for each model's required API format).

---

## 1. Headline Result: Density "Accuracy" Is Often Not Real Discrimination

The single most important pattern in this entire project, visible immediately in the density accuracy figure: **most conditions cluster tightly around the trivial "always predict High" baseline (66.44%)** — Qwen's four conditions range 57.9–67.5%, Gemma's range 64.7–69.0%. Neither model is reliably beating a classifier that never looks at the image.

**LLaVA is the exception, but not a positive one** — it falls well *below* this trivial baseline in three of its four conditions (37.8%, 12.7%, 14.6%), meaning it performs *worse* than random majority-guessing, not just unimpressively. Its zero-shot Experiment A in particular represents close to a full breakdown of visual grounding (Section 4).

**Practical implication for how these results should be reported:** density accuracy alone should never be presented without either the per-class recall breakdown or a comparison to the trivial baseline — in most conditions here, it does not represent genuine crowd-density discrimination.

---

## 2. Counting Performance

Full results in the tables above. Two patterns hold consistently:

- **Adding the YOLO count improves counting accuracy in every one of the 6 model/prompting-strategy combinations tested** (comparing A vs. B within each).
- **The reliability of that improvement varies enormously** — see Section 3.

Gemma achieves the lowest MAE in 3 of 4 of its own conditions and is the best-performing model overall in both zero-shot conditions (234.54 in 0-shot B, the best counting result across the entire project). Qwen's zero-shot A is the single worst result in the whole study (MAE 725.92), driven by extreme, unconstrained hallucinations with no support examples to calibrate against.

---

## 3. Statistical Significance Differs Sharply by Model — This Is a Central Finding

| Model | 5-shot p | 0-shot p |
|---|---|---|
| Qwen | 1.7×10⁻⁴⁶ | 9.1×10⁻⁴⁴ |
| LLaVA | 4.2×10⁻⁶¹ | 7.7×10⁻²² |
| Gemma | 0.0096 | **0.216 (not significant)** |

Qwen and LLaVA show overwhelming statistical significance in both prompting conditions. Gemma's 5-shot improvement is significant but far more marginal, and its **zero-shot improvement is not statistically significant at all** — the first non-significant result in this entire project. This is not a weakness in the analysis; it is explained directly and completely by Section 4.

---

## 4. The Explanation: Substitution Rate

The mechanism behind Section 3 is directly measurable — what fraction of each model's Experiment B predictions are an exact copy of the YOLO count given, versus an independently-generated answer:

| Model / condition | Exact YOLO echo |
|---|---|
| Qwen — 0-shot B | 46.2% |
| LLaVA — 5-shot B | 62.6% |
| LLaVA — 0-shot B | **95.8%** |
| Gemma — 5-shot B | 1.1% |
| Gemma — 0-shot B | **1.3%** |

*(Qwen's 5-shot B substitution rate was not part of the finalized measurement set and is omitted.)*

**This single metric explains nearly everything in Sections 2 and 3.** LLaVA and Qwen show large, highly significant B-improvements because they substitute heavily — much of their "improvement" reflects deferring to a better external number, not improved visual reasoning. Gemma shows minimal substitution in *both* prompting conditions, and correspondingly shows the most marginal (5-shot) or entirely absent (zero-shot) statistical improvement. A model that barely uses the auxiliary information cannot show a reliable, systematic benefit from it — and Gemma's results are exactly consistent with that logic, both times it was tested.

---

## 5. Response Reliability: a Second, Separate Axis From Accuracy

| Model | 5-shot A | 5-shot B | 0-shot A | 0-shot B |
|---|---|---|---|---|
| Qwen | 100% | 100% | 100% | 100% |
| LLaVA | 98.6% | 99.8% | **38.6%** | 99.9% |
| Gemma | 100% | 100% | 99.9% | 100% |

Qwen and Gemma are essentially perfectly reliable across every condition tested. LLaVA is reliable except in one specific condition — zero-shot Experiment A — where reliability collapses to 38.6%. Critically, **adding the YOLO count in LLaVA's zero-shot Experiment B restores reliability to 99.9%**, even though density accuracy does not improve and in fact the model's density judgment collapses even further in that same condition (Section 1). Reliability and accuracy are separate properties that can move independently, and this project's data shows a clean case of exactly that.

---

## 6. Model-Specific Zero-Shot Collapse Patterns

Removing support examples affects each model differently, not uniformly:

- **Qwen** collapses toward predicting the majority density class ("High") almost universally (97.6% of predictions in zero-shot A), while remaining fully format-reliable.
- **LLaVA** collapses on two axes simultaneously: format reliability breaks down (only 38.6% valid) and the actual values produced (whether correctly formatted or not) become almost entirely round powers of 10 (93.9–98.7%, depending on response type) — closer to a failure of visual grounding altogether than a density-specific problem.
- **Gemma** shows the most contained degradation: it retains partial, functional density discrimination between Medium and High (recall 62.9% and 78.4% respectively in zero-shot A) while specifically losing the ability to recognize Low-density scenes (1.8% recall) — and its zero-shot rank-correlation with ground truth (Spearman ρ = 0.854) is the highest of any experiment in this project, despite the raw MAE being poor due to a small number of extreme outliers.

---

## 7. A Cross-Cutting Qualitative Anomaly

**Test image 3411 (true count: 105) produced the identical extreme prediction, 21,482, in eight separate instances**: Qwen 5-shot A, Qwen 5-shot B, Qwen 0-shot A, Qwen 0-shot B, Gemma 5-shot A, Gemma 5-shot B, Gemma 0-shot A, and Gemma 0-shot B — spanning both model families, both prompting strategies, and both YOLO conditions, including cases where an accurate YOLO count (110) was supplied and evidently ignored. This did not occur in any LLaVA condition. The exact recurrence of this specific value on this specific image, entirely independent of prompt design or auxiliary input, is very strong evidence of a property of the image itself (or its interaction with a shared aspect of these two models' vision processing) rather than coincidence.

A related, broader pattern: **the magnitude of round-number placeholder hallucinations escalates specifically in zero-shot conditions** — 10,000 (Qwen 5-shot) → 50,000 (Qwen 0-shot) → 75,000 (Gemma 0-shot) — consistent with support examples constraining not just *whether* a model hallucinates under uncertainty, but the *scale* of what it hallucinates.

---

## 8. Which Model Performed Best?

| Criterion | Best |
|---|---|
| Lowest counting error (any condition) | Gemma — 0-shot B: MAE 234.54 |
| Highest density accuracy (any condition) | Gemma — 5-shot A: 69.00% |
| Most reliable output formatting | Qwen and Gemma — ~100% across all 4 conditions |
| Most robust to prompting-strategy removal | Gemma — smallest zero-shot degradation on both tasks |
| Largest measured benefit from the YOLO count | LLaVA and Qwen — but substantially via substitution, not reasoning (Section 4) |

**Gemma 3 (4B) is the strongest model overall**, and by a wider margin than raw accuracy numbers alone suggest — it is also the most reliable, the most robust to losing few-shot scaffolding, and the only model whose behavior is consistent with genuine (if limited) reasoning over auxiliary information rather than substitution. LLaVA (0.5B), by far the smallest model, is the weakest on every axis measured, including reliability itself in the zero-shot setting.

---

## 9. Limitations

- The `distractor` metadata field is confounded with ground-truth density and was not analyzed as an independent effect.
- `scene_type` has ~58 categories, many represented by only 1–2 images.
- The three models differ in both scale (0.5B / 3B / 4B) and architecture; this study cannot fully separate the contribution of each.
- LLaVA's zero-shot Experiment A counting metrics are computed on a 38.6% subset and should not be treated as fully representative (flagged throughout).
- Substitution-rate data was not finalized for Qwen's 5-shot Experiment B and is omitted from Section 4's table.

---

## 10. Status

All 12 planned VLM experimental conditions are complete. Remaining: the VisDrone-mismatched-YOLO robustness check (proposed extension, not yet run) for all three models under the 5-shot condition.
