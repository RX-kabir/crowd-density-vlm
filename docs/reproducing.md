# Reproducing the experiments

## 1. Data
Follow [`data/README.md`](../data/README.md) to obtain JHU-CROWD++ and build the `Phase5_Input` folder (`train/images`, `test/images`, `support_mapping.csv`, `test.csv`, `yolo_predictions.csv`). It is not stored in this repository (about 2.6 GB).

## 2. YOLO counts and support examples (already provided)
- [`pipeline/Phase4_YOLO_Inference.ipynb`](../pipeline/Phase4_YOLO_Inference.ipynb) produced [`yolo/yolo_predictions.csv`](../yolo/yolo_predictions.csv). Note the `max_det` issue in [`yolo/README.md`](../yolo/README.md).
- [`pipeline/Phase5_Support_Mapping.ipynb`](../pipeline/Phase5_Support_Mapping.ipynb) produced [`support_mapping/support_mapping.csv`](../support_mapping/support_mapping.csv).

The notebooks contain the author's local Windows paths; adjust them for your machine.

## 3. Open-source models (Qwen, LLaVA, Gemma)
Run the notebook of the condition you want from `<model>/<condition>/` on a GPU runtime (Colab / Kaggle). Each notebook writes `*_experiment_{A|B}[...].csv` and an `_evaluated.csv`. Some notebooks are not yet in this repository (see the README's known issues).

## 4. GPT-6.1 Terra (Colab, CPU runtime is enough)
1. Put `Phase5_Input.zip` in `MyDrive/CrowdDensityResearch/`.
2. Add your key as a Colab **Secret** named `OPENAI_API_KEY` (never paste it into a cell).
3. Open the **pilot** notebook of the condition (`GPT_Experiment*_Pilot.ipynb`): 25 images, synchronous, checks image handling, prompt, parsing and cost, and prints a GO / NO-GO verdict.
4. Open the **final-run** notebook (`GPT_Experiment*.ipynb`, no pilot):
   - run the cells down to **9a-1** (builds the batch files; submits nothing);
   - set `CONFIRM_FULL_RUN = True` in **9a-2** and run it (submits as many batches as fit under the queue limit);
   - you may close Colab. Later, rerun the setup cells and 9a-1, then **9a-2** again (to submit the remaining parts) and **9b** (status, download, assemble into `gpt_experiment_*.csv`);
   - when 9b reports 1600/1600, run the evaluation cells (10–12), which save `*_evaluated.csv`.
5. Batch ids are kept in a state file on Drive, so a Colab disconnect loses nothing. Results are matched by `custom_id`, so part order does not matter.

**Queue limit:** the Batch API limits enqueued input tokens per organisation and model. For the account used here it was 1,350,000 (`QUEUE_TOKEN_LIMIT` in the notebooks; check yours under the OpenAI dashboard's limits page). Two notebooks on the same organisation share it. 5-shot requests (6 images) take about 1,500 input tokens each, so run those one experiment at a time.

## 4b. Claude Haiku 5.5 and Sonnet 5.5 (Colab, CPU runtime)
Same flow as GPT, with the Colab Secret `ANTHROPIC_API_KEY` and the Message Batches API; see [`../claude_haiku/README.md`](../claude_haiku/README.md) and [`../claude_sonnet/README.md`](../claude_sonnet/README.md) (identical notebooks, different model and prices). The batch queue limit is counted in requests (200,000 on the Start tier), so nothing is held back; the only size limit is 256 MB per batch (the notebooks split into files of at most 200 MB).

## 5. Statistics, figures and summary
- `python scripts/summarize_results.py` — headline table (`Final_Comparison/all_conditions_summary.*`).
- `python scripts/extract_prompts.py` — rewrites `prompts/*.txt` from the notebooks.
- `scripts/gpt_analysis/` — the figure and statistics scripts used for the GPT findings documents. They read the CSVs from a hard-coded `D:/Downloads` and write into the repository folders; edit the `SRC` / `OUT` constants at the top of each script first.

Requirements: Python 3.10+, `pandas`, `numpy`, `scipy`, `scikit-learn`, `matplotlib`.
