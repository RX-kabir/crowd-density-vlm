# LLaVA-Interleave (0.5B) — Zero-Shot Experiment A: Density-Definition Prompt Test

**Status:** Complete on the full 1600-image test set. Result: the density definition measurably **worsens** this model's already-severe zero-shot reliability problems, rather than helping.

---

## 1. Headline Results

| Metric | Old Prompt (bare labels) | New Prompt (with definition) |
|---|---|---|
| MAE (valid subset) | 380.67 (n=617) | 411.84 (n=361) |
| Format-valid rate | 38.6% | **22.6%** |
| Density Accuracy | 12.71% | 14.52%* |

*\*Density accuracy is not meaningfully comparable between conditions — both are computed on very different, small, biased valid subsets (653 vs. 427 of 1600 images), not the full test set.*

---

## 2. The Central Finding: Response Reliability Got Worse, Not Better

| | Old Prompt | New Prompt |
|---|---|---|
| Correctly formatted | 617 / 1600 (38.6%) | **361 / 1600 (22.6%)** |
| Degenerate digit-repeat | 162 / 1600 (10.1%) | **408 / 1600 (25.5%)** |

Making the system prompt longer and more detailed — adding a three-part density definition — measurably **increased** LLaVA's rate of failing to follow the required output format at all, and more than doubled the rate of degenerate bare digit-repeat responses. This is the opposite of the intended effect and is a genuine, negative finding, not a null result.

Sample raw responses from the new failures show the model producing garbled fragments of the prompt's own density syntax rather than a judgment — e.g. *"The density is 0.2"*, *"0/12"*, *"0/1/2"* — consistent with the added prompt length overwhelming this very small (0.5B parameter) model's ability to track and follow instructions, rather than the added clarity helping it.

---

## 3. The Underlying Behavior Is Otherwise Unchanged

Among the (smaller) set of correctly-formatted responses, **98.3% are still an exact power of 10** (vs. 98.7% under the old prompt) — the round-number placeholder pattern documented in the original zero-shot A findings persists essentially identically. The definition did not change *what* the model outputs when it does manage to follow the format; it only made following the format less likely.

---

## 4. Density Recall (on the new, smaller, less representative valid subset)

| Density | Recall |
|---|---|
| Low | 27.9% |
| Medium | 0.0% |
| High | 0.0% |

This should not be directly compared to the old prompt's recall figures given the very different (and differently biased) valid subsets involved — but the pattern of near-total collapse away from Medium and High persists.

---

## 5. Interpretation

Unlike Qwen, where the density definition produced a small but genuine improvement, it actively harms LLaVA's zero-shot performance. The most likely explanation is model capacity: at 0.5B parameters — roughly 6–8× smaller than the other two models in this project — LLaVA appears to have limited ability to process and act on a longer, more detailed system prompt, and the added instruction volume increases rather than decreases response failures. This is a genuinely useful negative finding for the paper: **prompt engineering interventions do not transfer uniformly across model scale**, and a change that helps a 3B model can measurably hurt a 0.5B one under otherwise identical conditions.

---

## 6. Status

LLaVA's density-definition test for Experiment A is complete, showing a clear backfire. Experiment B is the next planned step — worth watching whether the presence of a concrete YOLO number (which helped counting reliability substantially in the original zero-shot B, restoring format-validity to 99.9%) offsets this prompt-length problem, or whether the same reliability drop appears there too.
