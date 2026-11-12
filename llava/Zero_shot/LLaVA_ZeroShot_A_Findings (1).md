# LLaVA-Interleave (0.5B) — Zero-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. No support examples — the model sees only the test image and a zero-shot system prompt (identical text to Qwen's zero-shot experiments).

---

## 1. Headline Results

**Counting** (computed only on the subset with a parseable count — see Section 2 before treating this as representative)

| Metric | Value |
|---|---|
| MAE | 380.67 |
| RMSE | 683.61 |
| MAPE | 216.31% |
| Valid predictions | 617 / 1600 (38.6%) |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 12.71% |
| Precision | 1.64% |
| Recall | 12.71% |
| F1-score | 2.90% |
| Valid predictions | 653 / 1600 (40.8%) |

---

## 2. Response Reliability Has Collapsed — Read This Before the Metrics Above

| Response type | n | % of 1600 |
|---|---|---|
| Correctly formatted (`Count:`/`Density:`) | 617 | 38.6% |
| Free-text explanation, ignoring the required format | 821 | 51.3% |
| Degenerate bare digit-repeat (e.g. a 19-digit string, no label) | 162 | 10.1% |

Only 38.6% of responses followed the required output format at all. The majority (51.3%) instead produced free-text explanatory sentences — e.g. *"1. The EXACT crowd count is 10,000. The density is 0.2."* — directly violating the system prompt's explicit "do not explain" instruction. A further 10.1% degenerated into a bare run of 10+ repeated digits with no label at all — specifically the identical literal string `1000000000000000000` in every one of these cases, regardless of the image or true count. For comparison, the original 5-shot LLaVA Experiment A had a 1.4% failure rate of any kind, and a comparable digit-repeat pattern occurred in only 0.19% of responses there.

**Note on generation settings:** this run used `min_new_tokens=18`, the same setting used for every other LLaVA experiment in this project (originally added to prevent early stopping in the 5-shot condition). A follow-up diagnostic (Section 9) confirms the specific 19-digit degenerate string is an artifact of this forced-continuation setting, not an inherent zero-shot behavior — removing it eliminates that exact pattern entirely. However, the same diagnostic shows this does not change the core finding in Section 3; it only changes which specific degenerate pattern appears. `min_new_tokens=18` was kept for this run to preserve consistency with every other LLaVA experiment in this project, and the numbers above are the ones used for reporting.

---

## 3. The Central Finding: Predictions Are Almost Entirely Powers of 10, Regardless of Format

This is more fundamental than a formatting problem. Looking at the actual *values* produced, in both response types:

- **Among the 617 correctly-formatted predictions, 98.7% are an exact power of 10** — specifically 1, 10, 100, or 1,000 (1000: 279 images; 100: 252 images; 10: 76 images; 1: 2 images). No other values appear meaningfully.
- **Among the 983 free-text failures, extracting the number stated in the sentence shows the same pattern: 93.9% are also exact powers of 10** (most commonly 100, 1, 10, 1,000, and 10,000).

Combined, this indicates that without support examples, this model is not performing meaningful visual crowd estimation in either response mode — it is selecting from a small set of round placeholder values almost independent of the image's actual content. This is a more severe finding than a format-compliance issue in isolation: the *format* differs between response types, but the underlying *behavior* — defaulting to an unanchored round-number guess — is the same in both.

---

## 4. Density-Stratified Counting Error (n=617 valid subset — small samples, interpret cautiously)

| Density | n | MAE | Bias |
|---|---|---|---|
| Low (0) | 82 | 24.8 | +8.4 |
| Medium (1) | 111 | 167.8 | +109.0 |
| High (2) | 424 | 505.2 | +219.9 |

The density distribution of the valid-count subset (13.3% Low, 18.0% Medium, 68.7% High) closely matches the full test set (13.9% / 19.7% / 66.4%), so the parsing failures do not appear to be concentrated in a particular density stratum — the collapse in Section 3 is a general behavior, not one specific to certain image types.

---

## 5. Correlation With Ground Truth (valid subset)

- **Pearson r = 0.350**
- **Spearman ρ = 0.705**

Both lower than the equivalent Qwen zero-shot Experiment A figures (Pearson 0.563, Spearman 0.794) — consistent with predictions being drawn from a small fixed set of round values rather than genuine estimates.

---

## 6. Worst-Case Examples (among "successfully parsed" predictions)

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 212 | 9,059 | 1,000 | 8,059 |
| 3539 | 6,757 | 1,000 | 5,757 |
| 2542 | 4,113 | 1,000 | 3,113 |
| 3269 | 3,928 | 1,000 | 2,928 |
| 2236 | 2,889 | 100 | 2,789 |

Every one of the worst cases — even though correctly formatted — is simply a flat placeholder value (1,000 or 100) applied to a genuinely dense scene.

---

## 7. Interpretation

Without support examples, LLaVA-Interleave-0.5B's zero-shot behavior differs sharply from Qwen's under the same conditions. Where Qwen remained fully format-compliant (0% failures) and collapsed toward a majority-class density guess while still producing count estimates with real (if imperfect) correlation to ground truth, LLaVA's output degrades on two axes simultaneously: format compliance breaks down for over 60% of responses, and — more fundamentally — the actual numeric content collapses to a small handful of round placeholder values regardless of format. This suggests that for a model this small (0.5B parameters), the support examples in the original 5-shot setup were doing more than providing values to copy (as shown by the original Experiment A's 81.7% support-echo rate) — they were likely essential scaffolding for both the required output format and for any real attempt at visual estimation at all. Without that scaffolding, the model appears to fall back on the smallest set of "safe" round-number guesses it can produce.

---

## 8. Diagnostic: Is This a `min_new_tokens` Artifact?

To check whether the degenerate pattern in Section 2 was caused by the forced-continuation setting rather than reflecting genuine zero-shot behavior, the same 30 images (10 from each response category above) were rerun with `min_new_tokens` reduced to 1, with the prompt held completely unchanged.

**Result: the specific 19-digit degenerate string disappeared entirely (0/30)** — confirming it was a `min_new_tokens=18` artifact. In its place, **20 of 30 responses (66.7%) became a single bare character, `"1"`, with no label at all** — again the identical output regardless of the true count (which ranged from 4 to 607 across these images). Of the 10 responses that did reach a complete `Count:` format, 9 were still an exact round number (four instances of 1000, two of 100, two of 10).

**Conclusion: the core finding is robust to this generation setting, not an artifact of it.** Which specific degenerate output appears changes (a 19-digit string vs. a bare "1"), but the underlying behavior — the model settling on a fixed, image-independent output rather than attempting genuine estimation — holds under both configurations. On this basis, the original `min_new_tokens=18` run was kept as the reported result, both because it preserves consistency with every other LLaVA experiment in this project and because the diagnostic shows the finding does not depend on this choice.

---

## 9. Status

Zero-shot Experiment B (test image + YOLO count, no support images) has not yet been run for LLaVA. Given how severely this model's zero-shot behavior degraded in Experiment A, the YOLO count in Experiment B may prove considerably more consequential for LLaVA than it was for Qwen — worth watching closely once that run is complete.
