# Data

The images are **not** in this repository.

## Source
**JHU-CROWD++** — V. A. Sindagi, R. Yasarla, V. M. Patel, "JHU-CROWD++: Large-Scale Crowd Counting Dataset and A Benchmark Method", IEEE TPAMI, 2020. Download it from the authors' site and follow its terms of use.

## What is included here
| File | Content |
|---|---|
| `test_labels.csv` | one row per test image (1,600): `test_filename`, `total_count` (people), `crowd_density` (0 = Low, 1 = Medium, 2 = High), `yolo_predicted_count` |
| `../support_mapping/support_mapping.csv` | for every test image, the five training images (filename, count, density) used as 5-shot support examples |
| `../yolo/yolo_predictions.csv` | YOLO count per test image |

The density labels are the project's manually annotated, cross-verified three-class labels.

## Folder expected by the notebooks (`Phase5_Input`)
```
Phase5_Input/
├── train/images/        training images, named 0001.jpg, 0002.jpg, ... (support examples come from here)
├── test/images/         the 1,600 test images, named {:04d}.jpg
├── support_mapping.csv  see above
├── test.csv             test labels (filename, total_count, crowd_density)
└── yolo_predictions.csv
```
The GPT notebooks expect `Phase5_Input.zip` in `MyDrive/CrowdDensityResearch/` and unzip it to `/content/Phase5_Input`. See [`../docs/reproducing.md`](../docs/reproducing.md).
