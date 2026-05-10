# FitFuel CV Integration

The current CV MVP performs food/non-food detection and selected-class food classification. It does not estimate exact portion size from image geometry. Calories are estimated from mapped food item nutrition facts using default or user-confirmed serving grams.

## Model Artifacts

Copy these files from the separate `SabetAbderrahmane/fitfuel_CV` training repo into the ignored backend artifact folder:

```powershell
Copy-Item ..\fitfuel_CV\checkpoints\binary_resnet50_best.pth backend\ml_artifacts\binary_resnet50_best.pth
Copy-Item ..\fitfuel_CV\outputs\binary_class_names.json backend\ml_artifacts\binary_class_names.json
Copy-Item ..\fitfuel_CV\checkpoints\food101_subset_resnet50_best.pth backend\ml_artifacts\food101_subset_resnet50_best.pth
Copy-Item ..\fitfuel_CV\outputs\food101_subset_class_names.json backend\ml_artifacts\food101_subset_class_names.json
```

`backend/ml_artifacts/` is ignored by Git. Do not commit checkpoints or generated class-name JSON artifacts.

## Settings

Defaults are defined in `app/core/config.py` and can be overridden by environment variables:

```env
VISION_BINARY_MODEL_PATH=backend/ml_artifacts/binary_resnet50_best.pth
VISION_BINARY_CLASS_NAMES_PATH=backend/ml_artifacts/binary_class_names.json
VISION_FOOD_MODEL_PATH=backend/ml_artifacts/food101_subset_resnet50_best.pth
VISION_FOOD_CLASS_NAMES_PATH=backend/ml_artifacts/food101_subset_class_names.json
VISION_DEVICE=auto
VISION_FOOD_ACCEPT_THRESHOLD=0.90
VISION_CLASS_ACCEPT_THRESHOLD=0.75
VISION_TOP_K=5
VISION_DEFAULT_SERVING_GRAMS=100
```

`VISION_DEVICE=auto` uses CUDA when PyTorch exposes it, otherwise CPU.

## Label Mapping

Seed classifier labels and best-effort mappings to existing active food catalog rows:

```powershell
python -m app.scripts.seed_cv_label_food_maps
```

The script is idempotent and writes:

```text
backend/docs/cv-label-food-map-report.md
```

Unmapped labels are safe: prediction still returns top-k classes, but nutrition estimates are omitted until a food item mapping exists.

## Smoke Test

After copying artifacts, run one local image through both models:

```powershell
python -m app.scripts.smoke_test_cv_inference --image C:\tmp\fitfuel_external_images\external_pizza.jpg
```

The script prints the binary gate result, Food-101 subset top-k predictions, and mapping/nutrition information when the database is available.

## API Test

The integrated endpoint uploads and analyzes in one authenticated request:

```http
POST /api/v1/photos/analyze
Content-Type: multipart/form-data
```

Form fields:

- `file`: jpg, jpeg, png, or webp image
- `serving_grams`: optional, defaults to `VISION_DEFAULT_SERVING_GRAMS`
- `save_prediction`: optional, defaults to `true`
- `top_k`: optional, defaults to `VISION_TOP_K`

Existing uploaded photos can still be analyzed with:

```http
POST /api/v1/photos/{photo_upload_id}/run-inference
```

The response includes the binary food gate, selected-class food prediction, top-k candidates, mapping status, and default-serving nutrition estimate when a mapped food item has nutrition facts.
