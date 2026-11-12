# LLaVA-Interleave (0.5B) — Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image per prediction, no YOLO count). Experiment B (adding the YOLO count) is not yet run.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 503.34 |
| RMSE | 1184.49 |
| MAPE | 1013.03% |
| n (valid predictions) | 1577 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 47.96% |
| Precision | 51.53% |
| Recall | 47.96% |
| F1-score | 49.51% |

---

## 2. Response Reliability — Why 23 Rows Were Dropped

Of 1600 test images, **1577 (98.6%) produced a numerically parseable count; 23 (1.4%) did not** and were excluded from the counting metrics above. These were not truncated or empty responses — they were complete, confidently-formatted but numerically degenerate outputs:

- **20 images** returned exactly `Count: 1000000000` (one billion) — an identical value regardless of the image's actual content, in several cases paired with `Density: 1000000000` or `Density: 0`.
- **3 images** returned a bare, unlabelled run of repeated digits (e.g., a 37-digit string of `1`s; two 18–19 digit numbers) with no `Count:`/`Density:` structure at all.

The billion-value cases are consistent and reproducible rather than random noise, appearing identically across images with true counts ranging from 8 to 1030 — a stereotyped placeholder response, not a considered estimate. Both failure types plausibly stem from the same mechanism: this small model tends to end its response immediately after stating a value, and forcing it to continue generating (necessary to reliably elicit the required `Density:` line) can push it into a degenerate repetition loop once it has nothing further to say.

**Caveat:** the cutoff used to separate "valid" from "degenerate" responses (rejecting counts longer than 5 digits) is a pragmatic filter, not a perfect one. A few of the retained "valid" predictions — e.g. 21,859 and 20,371 in the worst-case table below — are very plausibly further instances of the same degenerate behavior that happened to fall within the length threshold, rather than genuine estimates. The 1.4% figure should be read as a lower bound on the model's outright failure rate on this task.

---

## 3. Central Finding: Predictions Are Mostly Echoed From the Support Examples

This is the most important and best-evidenced result from this run, and it explains most of the numbers above.

**81.7% of valid predictions (1289 of 1577) are an exact match to one of the 5 support examples' counts given in the prompt** — not a close estimate, an exact copy of a number the model was shown as a labelled example, applied to a completely different test image.

This is not simple copying of "the first thing it saw," but it is heavily biased that way:

| Support slot echoed | 1st | 2nd | 3rd | 4th | 5th |
|---|---|---|---|---|---|
| Times echoed (of 1289) | 495 | 58 | 105 | 253 | 378 |

Slot 1 accounts for 38% of all echoes — more than three times any other slot. If the model were doing something sensible like "pick whichever support example looks most similar to the test image," the echoed value should usually be the numerically closest support count to the true answer. It isn't: **only 21.7% of echoes are the nearest of the 5 support counts to the true value** — barely better than the ~20% expected from picking one of five values at random.

Consistent with this, **correlation between predictions and ground truth is essentially zero (r = −0.01)** — the model's output carries almost no information about the actual image content.

This also explains the density-stratified pattern below: the support-example counts happen to cluster in a low-to-medium range, so echoing one of them overestimates sparse (Low-density) scenes very badly, while landing closer to correct — partly by chance — on genuinely dense scenes.

---

## 4. Density-Stratified Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 220 | 472.8 | 1613.6 | +437.9 |
| Medium (1) | 309 | 380.9 | 722.1 | +276.5 |
| High (2) | 1048 | 545.9 | 1187.8 | −35.5 |

*(bias = mean signed error, predicted − ground truth; positive = overcounts.)*

Error is worst on Low-density images, not High — the opposite of the usual pattern in this task, and a direct consequence of echoing support-example counts that are frequently far larger than the true (small) count of a sparse scene.

---

## 5. Worst-Case Examples

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 1648 | 9 | 21,859 | 21,850 |
| 2273 | 85 | 20,371 | 20,286 |
| 212 | 9,059 | 152 | 8,907 |
| 814 | 8,994 | 279 | 8,715 |
| 3178 | 7,560 | 132 | 7,428 |

The two largest errors (1648, 2273) are on genuinely sparse images given absurdly large predictions — likely further degenerate outputs that slipped past the length filter (Section 2). The remaining large errors are on very dense scenes (7,000–9,000 people) where the model's answer lands in the range of a typical support example (100–350) rather than anywhere near the true count — consistent with the echoing behavior rather than a genuine attempt at estimating a crowd of that size.

---

## 6. Interpretation

Experiment A's results should not be characterized primarily as "poor counting accuracy." The evidence supports a more specific and more useful claim: **at this model size, the few-shot setup is largely eliciting example-copying behavior rather than independent visual crowd estimation**, with a measurable primacy bias toward the first support example and near-zero correlation with the true count. The 1.4% outright degenerate-response rate is a secondary, related finding about output stability under this prompting setup, not the main story.

This is a legitimate, citable capability-limitation finding, not merely "the model is noisier."

---

## 7. Status

Experiment B (adding the YOLO count) has not yet been run. Given the echoing behavior found here, Experiment B should specifically check whether the model echoes the support examples, the YOLO count, or neither.
