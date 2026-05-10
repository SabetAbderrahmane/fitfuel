# Dataset Licensing Notes

## RecipeNLG

RecipeNLG-derived data in this project is for thesis/demo testing only.

Any rows imported by `python -m app.scripts.import_recipenlg_recipes` are marked with:

- `Recipe.source = "recipenlg_thesis"`
- `MealTemplate.source = "recipenlg_thesis"`
- `Recipe.description` containing `Imported from RecipeNLG for thesis/demo use only.`

Before any commercial launch, remove or replace all RecipeNLG-derived recipes, recipe ingredients, and meal templates. Do not treat RecipeNLG as a commercial production recipe source unless the project separately obtains and documents appropriate rights.

## USDA nutrition data

USDA-derived nutrition facts remain the preferred commercial-safe nutrition base for this project. The RecipeNLG importer does not create new `FoodItem` or `NutritionFact` rows; it only links recipe ingredients to existing active food catalog rows and calculates recipe totals from those stored nutrition facts.

## Operational commands

Dry-run scan:

```powershell
python -m app.scripts.import_recipenlg_recipes --file data/raw/recipenlg/RecipeNLG_dataset.csv --target-count 1000 --dry-run
```

Import selected thesis/demo subset:

```powershell
python -m app.scripts.import_recipenlg_recipes --file data/raw/recipenlg/RecipeNLG_dataset.csv --target-count 1000 --min-match-ratio 0.7
```

