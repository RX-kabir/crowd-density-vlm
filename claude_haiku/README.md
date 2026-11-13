# Claude Haiku 5.5 (medium effort)

The Claude Sonnet 5.5 counterpart (same notebooks, same conditions) is in [`../claude_sonnet/`](../claude_sonnet/).

The same six conditions as every other model (5-shot / zero-shot / zero-shot + density definition, each as Experiment A and B), built from the GPT notebooks so that the structure, the prompts and the evaluation cells are identical.

```
claude_haiku/
├── Five_Shot/             Haiku_ExperimentA.ipynb, Haiku_ExperimentB.ipynb          (+ *_Pilot.ipynb)
├── Zero_Shot/             Haiku_ExperimentA_ZeroShot.ipynb, ..._B_ZeroShot.ipynb      (+ *_Pilot.ipynb)
└── Zero_Shot_Density/     Haiku_ExperimentA_ZeroShot_DensityDef.ipynb, ..._B_...      (+ *_Pilot.ipynb)
```

**Status:** notebooks built and tested offline with a mock of the Anthropic API, then run for real. **All six conditions are done**: 5-shot A/B (`Five_Shot/`), zero-shot A/B (`Zero_Shot/`) and zero-shot + density definition A/B (`Zero_Shot_Density/`), each with findings, figures and CSVs.

**Note (fixed):** the first notebook version did not write the `yolo_predicted_count` column into the Experiment B CSV. The notebooks are fixed; the repository copy of `haiku_experiment_B*.csv` had the column added by merging `yolo/yolo_predictions.csv`. If you re-run an Experiment B notebook from an older copy, download the regenerated one first.

## How to run (Colab, CPU runtime)
1. Put `Phase5_Input.zip` in `MyDrive/CrowdDensityResearch/` and add the Colab **Secret** `ANTHROPIC_API_KEY`.
2. Run the **pilot** notebook of a condition (25 images, synchronous). It prints a GO / NO-GO verdict and the projected cost of the full run.
3. If GO, run the **final** notebook (`Haiku_Experiment*.ipynb`): cells down to **9a-1**, then **9a-2** with `CONFIRM_FULL_RUN = True`. Close Colab if you like.
4. Later: setup cells and 9a-1, then **9b** (status, download, assemble). When it says 1600/1600, run the evaluation cells (10–12) and send the two CSVs (`haiku_experiment_*.csv` and `*_evaluated.csv`).
5. Never needed unless 9b still shows missing rows after every batch has ended: **9c** (synchronous re-run of just those rows).

If a notebook says a batch file is missing (Colab was reset), run 9a-1 first, then 9a-2 again.

## Settings
| | |
|---|---|
| Model | `claude-haiku-5-5` |
| Thinking / effort | adaptive thinking, `output_config.effort = "medium"` (the model's default) |
| `max_tokens` | 16,000 (includes thinking; a cap, not a cost) |
| Sampling | none sent — Claude Haiku 5.5 rejects non-default `temperature` / `top_p` / `top_k`, so runs are **not deterministic** (as for GPT; the open-source runs used greedy decoding) |
| Images | `thumbnail((512, 512))`, JPEG quality 95, base64, placed before the text in each user turn |
| Bulk API | Message Batches API: 50% of standard price; each batch file ≤ 200 MB (API limit 256 MB; 100,000 requests) |
| Prices used (Batch) | $0.05 / $0.25 per million input / output tokens for prompts up to 100K tokens (Anthropic's pricing page; verify) |
| Prompt text | character-identical to the GPT / open-source prompts (checked programmatically) |

## Differences from the GPT notebooks
- **Queue limit:** the Batch API limit is on the *number of requests* waiting in the queue (200,000 on the Start tier), not on tokens, so a 1,600-request experiment is never held back — no "re-run later" rounds. Only the 256 MB-per-batch size matters, so 5-shot runs are split into about 6 batch files and zero-shot runs into 1–2.
- **No separate reasoning-token count:** the API reports `output_tokens` including thinking, so the CSVs have `out_tok` (thinking included) but no `reason_tok`. Thinking text is returned empty by default and is ignored by the parser.
- **Stop reasons** are stored in the `status` column; anything other than `end_turn` (`max_tokens`, `refusal`) is also written to `incomplete`. Claude Haiku 5.5 can decline a request on safety grounds (`refusal`); there is no server-side fallback for it.
- **Results** are kept by Anthropic for 29 days after a batch is created; 9b downloads them to Drive.
- **Resubmission:** 9a-2 resubmits a batch that ended without a single success (everything expired or errored).

## Files written (to `MyDrive/CrowdDensityResearch/VLM_Results/`)
`haiku_experiment_<A|B>[_zeroshot[_densitydef]].csv` (raw responses), the same with `_evaluated.csv` (adds ground truth), `haiku_batch_state_<cond>_<hash>.json` (batch ids), `haiku_raw_batch_<cond>_<hash>/` (raw results), and from the pilots `haiku_pilot_report_<cond>.csv`.
