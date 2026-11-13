# Claude Sonnet 5.5 (medium effort)

The Claude Haiku 5.5 counterpart (same notebooks, same conditions; already run) is in [`../claude_haiku/`](../claude_haiku/).

The same six conditions as every other model (5-shot / zero-shot / zero-shot + density definition, each as Experiment A and B), built from the GPT notebooks so that the structure, the prompts and the evaluation cells are identical.

```
claude_sonnet/
├── Five_Shot/             Sonnet_ExperimentA.ipynb, Sonnet_ExperimentB.ipynb          (+ *_Pilot.ipynb)
├── Zero_Shot/             Sonnet_ExperimentA_ZeroShot.ipynb, ..._B_ZeroShot.ipynb      (+ *_Pilot.ipynb)
└── Zero_Shot_Density/     Sonnet_ExperimentA_ZeroShot_DensityDef.ipynb, ..._B_...      (+ *_Pilot.ipynb)
```

**Status:** notebooks generated from the same generator as the Haiku ones and tested offline with a mock of the Anthropic API, then run for real. **All six conditions are done**: 5-shot A/B (`Five_Shot/`), zero-shot A/B (`Zero_Shot/`) and zero-shot + density definition A/B (`Zero_Shot_Density/`), each with findings, figures and CSVs.

## How to run (Colab, CPU runtime)
1. Put `Phase5_Input.zip` in `MyDrive/CrowdDensityResearch/` and add the Colab **Secret** `ANTHROPIC_API_KEY`.
2. Run the **pilot** notebook of a condition (25 images, synchronous). It prints a GO / NO-GO verdict and the projected cost of the full run.
3. If GO, run the **final** notebook (`Sonnet_Experiment*.ipynb`): cells down to **9a-1**, then **9a-2** with `CONFIRM_FULL_RUN = True`. Close Colab if you like.
4. Later: setup cells and 9a-1, then **9b** (status, download, assemble). When it says 1600/1600, run the evaluation cells (10–12) and send the two CSVs (`sonnet_experiment_*.csv` and `*_evaluated.csv`).
5. Never needed unless 9b still shows missing rows after every batch has ended: **9c** (synchronous re-run of just those rows).

If a notebook says a batch file is missing (Colab was reset), run 9a-1 first, then 9a-2 again.

## Settings
| | |
|---|---|
| Model | `claude-sonnet-5-5` |
| Thinking / effort | adaptive thinking, `output_config.effort = "medium"`, set explicitly: Sonnet 5.5's own default is `high` and its levels are recalibrated relative to earlier Sonnets, so `medium` is used to keep the effort the same as for Haiku 5.5 (a `high` run would be a separate, later experiment) |
| `max_tokens` | 16,000 (includes thinking; a cap, not a cost) |
| Sampling | none sent — Claude Sonnet 5.5 rejects non-default `temperature` / `top_p` / `top_k`, so runs are **not deterministic** (as for GPT; the open-source runs used greedy decoding) |
| Images | `thumbnail((512, 512))`, JPEG quality 95, base64, placed before the text in each user turn |
| Bulk API | Message Batches API: 50% of standard price; each batch file ≤ 200 MB (API limit 256 MB; 100,000 requests) |
| Prices used (Batch) | $1 / $5 per million input / output tokens ($2 / $10 standard, 50% Batch discount; Anthropic's pricing page; verify) |
| Prompt text | character-identical to the GPT / open-source prompts (checked programmatically) |

## Cost
About 20 times Haiku's price per token. Haiku's runs cost $0.10–0.17 per condition, so expect roughly **$2–4 per condition and about $15 in total** if Sonnet uses a similar number of tokens (thinking length is the unknown) — the pilot of each condition prints a projection before you commit.

## Differences from the GPT notebooks
- **Queue limit:** the Batch API limit is on the *number of requests* waiting in the queue (200,000 on the Start tier), not on tokens, so a 1,600-request experiment is never held back — no "re-run later" rounds. Only the 256 MB-per-batch size matters, so 5-shot runs are split into about 6 batch files and zero-shot runs into 1–2.
- **No separate reasoning-token count:** the API reports `output_tokens` including thinking, so the CSVs have `out_tok` (thinking included) but no `reason_tok`. Thinking text is returned empty by default and is ignored by the parser.
- **Stop reasons** are stored in the `status` column; anything other than `end_turn` (`max_tokens`, `refusal`) is also written to `incomplete`. Claude Sonnet 5.5 can decline a request on safety grounds (`refusal`). Anthropic offers a server-side fallback (beta) for Sonnet 5.5; it is deliberately **not** used, so that every answer in the CSVs comes from Sonnet 5.5 itself.
- **Results** are kept by Anthropic for 29 days after a batch is created; 9b downloads them to Drive.
- **Resubmission:** 9a-2 resubmits a batch that ended without a single success (everything expired or errored).

## Files written (to `MyDrive/CrowdDensityResearch/VLM_Results/`)
`sonnet_experiment_<A|B>[_zeroshot[_densitydef]].csv` (raw responses), the same with `_evaluated.csv` (adds ground truth), `sonnet_batch_state_<cond>_<hash>.json` (batch ids), `sonnet_raw_batch_<cond>_<hash>/` (raw results), and from the pilots `sonnet_pilot_report_<cond>.csv`.
