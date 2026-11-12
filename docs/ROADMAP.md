# Roadmap

## Done
- [x] YOLO baseline and the five-example support mapping for all 1,600 test images.
- [x] Qwen2.5-VL-3B, LLaVA-Interleave-0.5B, Gemma 3 (4B): all six conditions, findings written, cross-model report for the three models (12 conditions) and the density-definition synthesis.
- [x] GPT-6.1 Terra (medium reasoning, Batch API): all six conditions with pilot and final-run notebooks, figures and findings.

## Next
- [ ] **Update the cross-model reports with GPT-6.1 Terra** — `Final_Comparison` (12 → 16 conditions: chart, report `.md` / `.docx` / `.pdf`) and `DensityDef_CrossModel_Synthesis.md`. (The headline table in the README already includes GPT.)
- [ ] **Claude Haiku 5.5** (medium effort) — the same six conditions, pilot first, then the batch API.
- [ ] **Gemini 3.8** — same design; variant to be decided.
- [ ] **Fine-tune a VLM for density estimation** (model to be chosen) and evaluate it on the same 1,600 test images with the same prompt and metrics, to test whether a fine-tuned model beats the prompted ones. Keep the test images out of the fine-tuning data (the 5-shot support images already come from the training split).

## Open questions / checks
- [ ] **Confirm and, if needed, fix the 300 cap in the YOLO counts** (see [`../yolo/README.md`](../yolo/README.md)); decide whether Experiment B runs must be repeated.
- [ ] Measure run-to-run variance of the closed models (repeat one condition) so that small differences can be judged.
- [ ] Verify the token prices used for the cost figures against the providers' pricing pages.
- [ ] VisDrone-mismatched-YOLO robustness check (5-shot, planned earlier).
- [ ] Clean-up: add the missing notebooks (see the README's known issues), the missing `qwen/Zero_Shot_Density/*A*_evaluated.csv`, and choose a licence.
