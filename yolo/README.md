# YOLO baseline

The YOLO count serves two purposes: it is the **counting baseline** (MAE 241.87, RMSE 737.65, MAPE 50.64% on the 1,600 test images) and it is the **auxiliary number shown to the model in every Experiment B**.

| File | Content |
|---|---|
| `yolo_predictions.csv` | `image_id`, `predicted_count` — the number of boxes the detector returned for each test image |
| `yolo_evaluation.csv` | the same plus `ground_truth`, `error`, `absolute_error` |

Produced by [`../pipeline/Phase4_YOLO_Inference.ipynb`](../pipeline/Phase4_YOLO_Inference.ipynb): `model.predict(source=<image>, conf=0.25)`, count = `len(result.boxes)`. The weights (`best.pt`, 22 MB) are not stored in this repository; add them as a GitHub Release asset or with Git LFS if you want them shared.

## Known issue: the counts look capped at 300

- No test image has a YOLO count above **300**; **135** images (8.4%) have exactly 300; **99.3%** of those have a true count above 300 (median 759).
- The notebook calls `predict` **without** `max_det`. To my knowledge the Ultralytics default is `max_det = 300` detections per image, which would explain the wall at 300. (Please confirm against the Ultralytics version you used.)
- **Consequences:** the YOLO baseline under-counts dense scenes more than a detector without the cap would, and the number shown to the models in every Experiment B is wrong (too low) for those 135 images. In the GPT experiments those images carry about 20–25% of the total absolute error from 8.4% of the data, and the models mostly (but not always) reject the capped value.
- **Not fixed / not re-run.** A fix would be to re-run the inference with a larger `max_det` (for example 3000), recompute the baseline, and decide whether the Experiment B runs need repeating.
