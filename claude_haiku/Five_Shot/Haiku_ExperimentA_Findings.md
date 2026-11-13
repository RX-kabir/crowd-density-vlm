# Claude Haiku 5.5 — 5-Shot Experiment A: Findings

**Status:** Complete on the full 1600-image JHU-CROWD++ test set (5 labelled support examples + 1 test image per prediction, no YOLO count). Experiment B (adding the YOLO count) is analysed in `Haiku_ExperimentB_Findings.md` and `Haiku_A_vs_B_Comparison.md`.

**Setup:** `claude-haiku-5-5` through the Anthropic Messages API, adaptive thinking, effort **medium** (the model's default), images resized with `thumbnail((512, 512))` exactly as in the open-source runs, run through the Message Batches API. The prompt text is identical to the Qwen, LLaVA, Gemma and GPT 5-shot Experiment A prompt. `temperature` is not sent (Claude Haiku 5.5 rejects non-default sampling parameters), so — unlike the open-source runs, which used greedy decoding — this run is **not strictly deterministic** and was run once.

---

## 1. Headline Results

**Counting**

| Metric | Value |
|---|---|
| MAE | 341.74 |
| RMSE | 2024.21 |
| MAPE | 91.64% |
| n (valid) | 1600 / 1600 — zero parse failures |

**Density classification**

| Metric | Value |
|---|---|
| Accuracy | 74.69% |
| Precision | 75.87% |
| Recall | 74.69% |
| F1-score | 73.41% |

**Against the YOLO baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the same 1600 images): Claude is **worse on all three counting metrics** — in particular its RMSE is 2.7 times the baseline's. (GPT's 5-shot A beat the baseline on all three.)

**Against the other models' 5-shot Experiment A runs:**

| Model | MAE | RMSE | MAPE | Density acc. | Density F1 | Pearson r | Spearman ρ | Valid counts |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-VL-3B | 404.15 | 1203.67 | 329.41% | 67.5% | 63.2% | 0.243 | 0.491 | 1600 |
| LLaVA-Interleave-0.5B | 503.34 | 1184.49 | 1013.03% | 48.0% | 49.5% | −0.011 | 0.043 | 1577 |
| Gemma 3 (4B) | 264.87 | 950.48 | 104.21% | 69.0% | 67.1% | 0.225 | 0.777 | 1600 |
| GPT-6.1 Terra | **140.21** | **599.80** | **50.17%** | **77.8%** | **77.2%** | **0.774** | **0.956** | 1600 |
| **Claude Haiku 5.5** | 341.74 | 2024.21 | 91.64% | 74.7% | 73.4% | 0.520 | 0.871 | 1600 |

(Open-source and GPT figures recomputed from the saved `*_experiment_A_evaluated.csv` files.) Claude is **second best on density** (74.7%, above every open-source run) and on correlation, and has a lower MAPE than every open-source run (91.64% vs Gemma's 104.21%) — but its MAE (341.74) is worse than Gemma's (264.87) and its RMSE is the worst of all five models: the average case is good, the tail is bad (Section 6). Caveat: Claude Haiku 5.5 differs from the open models in scale, architecture and API serving, and from GPT in running almost without thinking (Section 3); this experiment cannot attribute differences to any single factor.

---

## 2. Response Reliability: Perfect

| Check | Result |
|---|---|
| Responses with stop reason `end_turn` | 1600 / 1600 |
| Truncated (`max_tokens`) / refused responses | 0 |
| API errors | 0 |
| Count and density parsed | 1600 / 1600 each |
| Longest response | 24 characters |

Every response is exactly `Count: <n>` and `Density: <d>` (1393 with a blank line between them, 207 with a single line break — both parse correctly). No explanations, no bracketed density words, no degenerate placeholder strings; LLaVA's 5-shot Experiment A produced only 1577 of 1600 valid counts.

---

## 3. "Medium Effort" Meant Almost No Thinking

Claude Haiku 5.5 thinks adaptively, and the API reports thinking tokens inside `output_tokens`. A bare answer (`Count: N` + `Density: D`) is about 13 output tokens, so output length shows when the model thought:

| Output tokens per request | Requests |
|---|---|
| 13–14 (answer only) | **1509 (94.3%)** |
| more than 15 | 91 (5.7%) |
| more than 100 | 83 |

Mean 25.7, median 13, maximum 747 tokens. So at effort `medium` the model answered **directly, without visible thinking, on about 94% of images**; this run is effectively a non-reasoning evaluation, in contrast to GPT-6.1 Terra, which reasoned for a mean of 335 tokens per request. The requests that did produce longer output are not easier: their MAE is 453.8 against 335.0 for the rest, and their density accuracy 70.3% against 75.0% — but they are also the harder images (output length correlates with the true count, Spearman ρ = 0.38), so this is selection, not a measured effect of thinking. Thinking text is not returned by default, so the content of the reasoning is not available. Effort levels above `medium` were not tested.

---

## 4. A Small Repertoire of Stock Numbers

The count predictions repeat a small set of values far more than real counts do:

| Most frequent predictions | Times |
|---|---|
| 412 | 73 |
| 1200 | 70 |
| 180 | 58 |
| 62 | 57 |
| 38 / 118 | 50 each |
| 58 / 120 | 49 each |
| 42 | 42 |

- **Multiples of 100:** 15.9% of predictions against 0.9% of true counts; of the 189 predictions of 1,000 or more, 168 (89%) are multiples of 100. Multiples of 10: 43.1% against 10.4%; of 1,000: 3.2% against 0.2%. (GPT-6.1 Terra's 5-shot A: 11.2% multiples of 10, 4 multiples of 1,000.)
- **1200 is a default for "very dense":** 70 images are answered exactly 1,200, with a median true count of 557 and an MAE of 642.9 on them. The scatter plot (Figure 1) shows the repeated values as horizontal stripes.
- **No placeholder copying from the examples:** only 5 of 1600 predictions (0.3%) equal one of the five support counts, and the rank correlation between the prediction and the mean support count is ρ = 0.09 (truth: 0.02). The stock numbers come from the model, not from the support examples.
- **Large placeholder-style values appear, but rarely:** 26 predictions are 5,000 or more, 5 exceed 10,000, and the maximum is **60,000** (the true count of that image is 3,641). Qwen and Gemma reached 50,000–75,000 in zero-shot; GPT's maximum in 5-shot A was 18,472.

---

## 5. Density Classification: Second Best, Biased Toward Denser Classes

Always predicting "High" scores **66.44%**; Claude's 74.69% (1195 / 1600) is clearly above it (one-sided binomial p ≈ 5×10⁻¹³).

| Density | n | Recall |
|---|---|---|
| Low | 222 | 31.5% (70 / 222) |
| Medium | 315 | 45.4% (143 / 315) |
| High | 1063 | 92.4% (982 / 1063) |

Confusion matrix (rows = ground truth, columns = predicted):

| | Pred Low | Pred Medium | Pred High |
|---|---|---|---|
| **True Low** | 70 | 134 | 18 |
| **True Medium** | 9 | 143 | 163 |
| **True High** | 3 | 78 | 982 |

Predicted shares are Low 5.1% / Medium 22.2% / High 72.7% (truth: 13.9% / 19.7% / 66.4%). The errors lean denser (315 predictions denser than the truth, 90 sparser): 163 of 315 Medium images (52%) are called High and 134 of 222 Low images (60%) are called Medium. Per-class recall (Low / Medium / High) of the 5-shot A runs: Qwen 15.3 / 22.9 / 91.6, LLaVA 20.7 / 25.6 / 60.3, Gemma 6.8 / 60.3 / 84.6, GPT 60.4 / 44.4 / 91.3, **Claude 31.5 / 45.4 / 92.4**. Claude's Medium recall is similar to GPT's, but its Low recall is about half.

---

## 6. Counting Error: Systematic Over-Count and a Heavy Tail

| Density | n | MAE | RMSE | Bias |
|---|---|---|---|---|
| Low (0) | 222 | 22.5 | 116.1 | −10.0 |
| Medium (1) | 315 | 69.5 | 268.4 | −1.6 |
| High (2) | 1063 | 489.1 | 2478.5 | **+324.2** |

*(bias = mean signed error, predicted − ground truth; positive = over-counts.)*

By ground-truth count:

| True count | n | MAE | Mean bias |
|---|---|---|---|
| 0–10 | 58 | 7.9 | +7.6 |
| 11–50 | 378 | 23.4 | +20.8 |
| 51–100 | 301 | 64.5 | +56.1 |
| 101–500 | 625 | 200.2 | +150.0 |
| 501–1,000 | 126 | 819.9 | +561.6 |
| 1,001+ | 112 | 2,585.7 | +1,359.4 |

Over-counting grows with crowd size and is present in every band: 1095 images are over-counted, 462 under-counted and 43 exact; the mean signed error is **+213.7** per image (GPT 5-shot A: +51.8); the median absolute error is 47.0 and only 15.4% of predictions are within ±10% of the truth (GPT: 27.2%). The mean is dominated by a few huge errors: **the 10 worst predictions account for 33% of the total absolute error**, and removing the 5 worst lowers MAE from 341.74 to 249.24.

**Worst cases**

| test_filename | true count | predicted | abs. error |
|---|---|---|---|
| 1510 | 3,641 | **60,000** | 56,359 |
| 212 | 9,059 | **50,000** | 40,941 |
| 2542 | 4,113 | 25,000 | 20,887 |
| 3342 | 1,477 | 18,432 | 16,955 |
| 3015 | 895 | 15,000 | 14,105 |
| 814 | 8,994 | 610 | 8,384 |
| 2967 | 995 | 8,500 | 7,505 |
| 970 | 193 | 6,500 | 6,307 |

All but one are over-counts, many on round numbers (60,000; 50,000; 25,000; 15,000). Images 212 and 2542 are images on which Qwen also produced 50,000 in the open-source runs; GPT answered them 6,824 and 5,100. **Test image 3411 (true count 105)**, which produced the identical value 21,482 in eight Qwen and Gemma conditions, is answered **100**: the anomaly does not reproduce.

---

## 7. Against GPT-6.1 Terra, 5-Shot Experiment A

Same prompt, same images (paired comparison):

| Metric | GPT-6.1 Terra | Claude Haiku 5.5 |
|---|---|---|
| MAE | **140.21** | 341.74 |
| RMSE | **599.80** | 2024.21 |
| MAPE | **50.17%** | 91.64% |
| Density accuracy | **77.81%** | 74.69% |
| Density F1 | **77.25%** | 73.41% |
| Pearson r / Spearman ρ | **0.774 / 0.956** | 0.520 / 0.871 |
| Mean output tokens / request | 350 (reasoning 335) | 26 |
| Mean input tokens / request | 1,525 | 1,858 |
| Actual cost at Batch prices | ≈ $2.62 | **≈ $0.16** |

GPT's absolute error is lower on 1091 images, Claude's on 457 (52 ties); Wilcoxon p = 2×10⁻⁶⁵. On density, GPT alone is right on 164 images and Claude alone on 114 (McNemar p = 0.003). The two models' count predictions are strongly rank-correlated (ρ = 0.91) but agree exactly on only 40 images. Claude costs about **one sixteenth** as much — at the price of a much worse error tail. Cost uses Anthropic's published Batch prices for Claude Haiku 5.5 ($0.05 / $0.25 per million input / output tokens for prompts up to 100K tokens; verify) on 2,972,151 input and 41,074 output tokens.

---

## 8. Interpretation

Claude Haiku 5.5 at medium effort behaves like a fast, almost non-reasoning estimator: perfect formatting, good ranking of crowd sizes (Spearman 0.87) and the second-best density accuracy in the project (74.7%), at a fraction of GPT's cost — but with a systematic over-count that grows with crowd size, a habit of falling back on stock values (412, 1200, multiples of 100) and a heavy tail of placeholder-like errors (up to 60,000) that makes its RMSE the worst among the five models and its counting worse than the YOLO baseline on every metric. Its weaknesses are the same family seen in the open-source models (large round-number hallucinations on a few hard images), much attenuated; its strengths on density and correlation are closer to GPT's than to theirs.

---

## 9. Limitations

- One run, not deterministic (no temperature control); run-to-run variation was not measured.
- Only effort `medium` was tested, and at that setting the model rarely thought (about 6% of requests produced more than a bare answer). Whether higher effort would reduce the tail errors is untested.
- Compared with open models that differ in scale, architecture and decoding.
- Thinking tokens are not reported separately by the API, so the figures above infer thinking from total output length.
- Prices are Anthropic's published figures and should be re-checked before being quoted.

---

## 10. Status

5-shot Experiment A is complete for Claude Haiku 5.5, and so is Experiment B (see `Haiku_ExperimentB_Findings.md`). The zero-shot and density-definition conditions have not been run yet.
