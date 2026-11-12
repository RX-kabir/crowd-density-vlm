# Density-Definition Prompt Study — Cross-Model Synthesis

**Scope:** All three models (Qwen2.5-VL-3B, LLaVA-Interleave-0.5B, Gemma 3 4B), both zero-shot experiments (A and B), testing whether adding an explicit visual definition of Low/Medium/High density — in place of bare, undefined labels — changes model behavior. Requested by supervisor following review of the proposed prompt change; the full 1600-image test set was used for every comparison after an initial 25-image sample check proved unreliable (see Qwen Experiment A findings for that methodological note).

---

## 1. Headline Result: The Same Prompt Change Produces Three Different Outcomes

| Model | Experiment A | Experiment B |
|---|---|---|
| Qwen | 66.75% → **68.00%** (p=0.0008, significant improvement) | 65.81% → 66.69% (p=0.098, not significant) |
| LLaVA | 12.71% → 14.52%* (reliability collapsed 38.6%→22.6%, not comparable) | 14.56% → 14.20% (p=0.031, small significant decline) |
| Gemma | 64.69% → **42.50%** (p=1.1×10⁻⁵⁶, severe decline) | 64.69% → **37.44%** (p=7.4×10⁻⁷⁶, severe decline) |

*\*LLaVA's Experiment A accuracy figures are not meaningfully comparable — see Section 3.*

No single narrative — "definitions help," "definitions don't matter," or "definitions hurt" — fits all three models. The identical text produces a real (if modest) improvement in one model, a roughly neutral-to-mildly-negative effect in another, and the most severe accuracy collapse observed anywhere in this project in the third.

---

## 2. Qwen: A Small, Genuine Improvement

Adding the definition produced a statistically significant, if modest, improvement in Experiment A (driven by roughly tripled recall on Low and Medium density images), with a similar but non-significant trend in Experiment B. The most likely explanation: Qwen had no strong prior density judgment to override, so the definition filled a genuine informational gap. Counting was unaffected in both conditions, as expected. A secondary finding: the YOLO-substitution rate increased under the longer prompt (46.2%→57.9% in B), suggesting some interaction between prompt length and reliance on auxiliary information — worth noting but not a primary result.

---

## 3. LLaVA: A Reliability Backfire, Not a Judgment Change

The definition's dominant effect on LLaVA was on response *format reliability*, not density judgment content. In Experiment A (no YOLO anchor), the longer prompt nearly halved the model's already-poor format-compliance rate (38.6%→22.6%), with the degenerate digit-repeat failure rate more than doubling. In Experiment B, the YOLO count's stabilizing effect (well-established in the original, non-modified prompt) held even under the longer prompt, keeping reliability at 99.9% — but density accuracy still showed a small, statistically significant decline (p=0.031). At 0.5B parameters — the smallest model in this project by a wide margin — LLaVA appears to have limited capacity to reliably process additional prompt length at all, regardless of what that additional content says.

---

## 4. Gemma: Overriding an Already-Good Judgment

Gemma showed the most severe and most statistically extreme effect of any model — a 22-point accuracy collapse in Experiment A (64.69%→42.50%, p=1.1×10⁻⁵⁶) and an even larger 27-point collapse in Experiment B (64.69%→37.44%, p=7.4×10⁻⁷⁶). The mechanism is clear and consistent across both experiments: predictions shifted heavily toward "Medium" (up to 79.75% of all predictions in B), specifically at the expense of correctly identifying High-density scenes — every image that flipped from correct to incorrect in Experiment A was reclassified as Medium, not Low.

This is mechanistically different from LLaVA's failure. Gemma's original zero-shot behavior was the only one of the three models showing genuine, functional Medium/High discrimination without any definition at all. The explicit definition did not fill a gap for this model — it overrode an already-reasonable internal judgment with a stricter written rule (particularly the Medium description's "gaps and open space still visible" wording) that doesn't match where Gemma had already learned to draw the boundary.

---

## 5. What This Means, Synthesized

Three distinct failure/success modes emerged from testing one intervention across three models:

1. **Filling a genuine gap** (Qwen) — a model with no strong prior benefits from explicit guidance.
2. **Overloading limited capacity** (LLaVA) — a very small model's reliability degrades from added prompt length, independent of content quality.
3. **Overriding good behavior** (Gemma) — a model with an already-reasonable implicit judgment gets actively worse when that judgment is replaced by an explicit rule that doesn't match its internal calibration.

**The core methodological lesson:** whether a clearer prompt helps depends entirely on what the model was already doing before the change — information invisible without testing directly, and not predictable from model scale alone (the middle-sized model improved; the largest model got dramatically worse). This is a stronger, more general finding for a paper than any single model's result would be — it directly argues against "more explicit instructions are always better" as a blanket prompt-engineering heuristic, with three independent, well-evidenced cases supporting the argument.

---

## 6. Recommendation

Given these results, the density definition should **not** replace the original bare-label prompt across the project's main results — its effect is inconsistent and, for two of three models, negative. It is, however, a genuinely valuable standalone finding: a controlled ablation showing that identical prompt clarity improvements interact unpredictably with different models' pre-existing behavior, worth reporting as its own contribution rather than as a proposed replacement for the main experimental prompt.

---

## 7. Status

The density-definition study is complete for all three models, both zero-shot conditions. This concludes the planned prompt-ablation work; remaining project items are the VisDrone-mismatched-YOLO robustness check (5-shot condition, all three models) and the final paper write-up.
