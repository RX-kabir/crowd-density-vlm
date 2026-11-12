# LLaVA-Interleave (0.5B) — Experiment B: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set. Same prompt as Experiment A, with one addition: a two-line statement giving the YOLO-predicted count for the test image.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 321.11 |
| RMSE | 784.55 |
| MAPE | 524.81% |
| n (valid predictions) | 1597 / 1600 |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 37.75% |
| Precision | 50.26% |
| Recall | 37.75% |
| F1-score | 41.40% |

---

## 2. Response Reliability

**3 of 1600 images (0.2%) produced an unparseable count** — all three were the identical degenerate placeholder `Count: 1000000000`, `Density: 0`. Notably, all three occurred on images where the supplied YOLO count was very low (10 in all three cases) against true counts of 11, 187, and 6660 — suggesting this specific failure is triggered when the YOLO input looks implausible relative to the image, not a random malfunction.

**Density parsing was fully reliable this time — 0 unparseable densities** (Experiment A had a small number tied to the same degenerate responses; here the density field defaulted to a parseable "0" even in the 3 failed-count cases).

**A separate data-quality issue, not previously checked:** of 1513 responses that included a bracketed density word (e.g. "Density: 1 (Medium)"), **352 (23.3%) have a word that doesn't match its own digit** — e.g. stating "Density: 1 (Low)" when 1 should read "Medium" per the prompt's own key. This doesn't affect the metrics above (parsing uses the digit, not the word), but it's a further sign of unreliable internal consistency in the model's output, worth noting separately from the counting/density accuracy numbers themselves.

---

## 3. Where the Predicted Count Actually Comes From

| Source | n | % of valid | MAE | Bias |
|---|---|---|---|---|
| Echoes the YOLO count exactly | 999 | 62.6% | 235.2 | −234.7 |
| Echoes a support example's count (not YOLO) | 386 | 24.2% | 489.8 | +64.9 |
| Matches neither (a genuinely independent answer) | 212 | 13.3% | 418.9 | +69.1 |

*(27 additional images had a support count that happened to equal the YOLO count for that row, coincidentally — counted here under "echoes YOLO.")*

The majority behavior in Experiment B is deferring to the YOLO number, not the support-example copying that dominated Experiment A — and this is also the model's *most accurate* mode (MAE 235.2, lower than either alternative). When it instead echoes a support example, accuracy is worst (MAE 489.8) — consistent with Experiment A's finding that support-example values carry no real information about the test image. The 13.3% of cases producing an independent answer land in between.

---

## 4. Density-Stratified Error

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 243.7 | 580.7 | +193.1 |
| Medium (1) | 314 | 168.5 | 391.2 | +33.4 |
| High (2) | 1061 | 382.5 | 900.3 | −233.9 |

*(bias = mean signed error, predicted − ground truth; positive = overcounts.)*

The bias flips sign across the density range: sparse scenes are substantially overcounted (+193.1), dense scenes substantially undercounted (−233.9). This is consistent with the YOLO-echoing behavior in Section 3 — YOLO's own count tends to undercount severely-occluded dense crowds, which gets carried through directly when the model defers to it.

---

## 5. Correlation With Ground Truth — Note on Which Statistic to Report

Pearson correlation between predicted and true count is low (r = 0.07) — but this figure is heavily distorted by a small number of extreme-magnitude errors (see Section 6) rather than reflecting the typical case. **Spearman rank correlation, which is far less sensitive to a few outliers, is substantially higher: ρ = 0.40 with ground truth, ρ = 0.45 with the YOLO count.** Both statistics are legitimate; the large gap between them is itself informative — it indicates a real, moderate rank-order relationship for most images, undermined by a handful of very large misses. Reporting only the Pearson figure would understate the model's typical-case behavior; reporting only Spearman would understate the impact of its worst failures. Both are included here for that reason.

---

## 6. Worst-Case Examples

| test_filename | true count | predicted | YOLO count | abs. error | density |
|---|---|---|---|---|---|
| 212 | 9,059 | 152 | 1 | 8,907 | High |
| 814 | 8,994 | 279 | 6 | 8,715 | High |
| 3178 | 7,560 | 1,000 | 9 | 6,560 | High |
| 3539 | 6,757 | 300 | 300 | 6,457 | High |
| 4159 | 6,210 | 100 | 55 | 6,110 | High |
| 2893 | 47 | 4,813 | 48 | 4,766 | Low |

The first five are all severe undercounts on very dense scenes, tracking YOLO's own undercounting on those same images (note how close most predictions are to the YOLO count). Row 3178 shows the "guess ~1000" pattern also seen elsewhere in this project when the YOLO input looks unreliable. Row 2893 is the reverse case — a wild overcount (4,813) on a sparse, Low-density scene where YOLO's own count (48) was accurate — one clear case where deferring to YOLO would have been the right call and the model didn't.

---

## 7. Interpretation

Experiment B's behavior differs meaningfully from Experiment A's. Where Experiment A predominantly echoed an arbitrary support example (81.7% of the time, weighted heavily toward the first one shown), Experiment B predominantly defers to the YOLO count instead (62.6%) — and this is its most accurate mode. The model appears to treat the YOLO number as a more trustworthy anchor than the support examples, which is a reasonable strategy in the aggregate (YOLO's count, while imperfect, correlates with truth far better than an unrelated example does) — but this also means Experiment B's accuracy is substantially bounded by YOLO's own accuracy and characteristic failure mode (severe undercounting on very dense, occluded scenes), rather than reflecting independent visual estimation by the VLM.

---

## 8. Status

Experiment A and B are both complete for LLaVA-Interleave-0.5B. Remaining work: Gemma (Experiments A and B), then the final cross-model comparison.
