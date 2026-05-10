# FitFuel Database Content Audit

Audit date: 2026-05-08  
Database source: `settings.database_url` from `backend/app/core/config.py`  
Connection used: live PostgreSQL database configured for the backend, not SQLite

## Executive summary

The current Docker/PostgreSQL database is not empty. It contains a real food catalog with 331 `food_items`, all active, and all linked to `nutrition_facts`. Most of that catalog comes from USDA FDC import data, with 326 foods from `usda_fdc` and 5 manual foods.

The meal generator can currently select real food items from the database. Using the same validity rules as the generator, 320 active foods look usable: active, non-placeholder, with nutrition facts, calories in range, macros in range, and macro sum within the generator's sanity limit.

The catalog is usable but still weak for a polished meal-planning product. It is mostly individual foods and ingredients, not complete meals. There is only 1 recipe, 3 recipe ingredients, and 2 meal templates. Existing generated meal plans are food-item-based plans, not recipe- or template-composed meal plans.

Allergy and dietary preference data exists but is thin. There are 2 active allergy records and 18 active dietary preference records, enough to test basic filtering, but not enough to represent diverse real personalization cases.

Vision/catalog mapping is not ready. There are 5 classifier labels and 13 photo predictions, but 0 classifier-to-food mappings. Current photo prediction candidates are mostly unmapped and do not point to food items.

## Table-by-table counts

| Area | Metric | Count |
| --- | ---: | ---: |
| Food catalog | `food_items` total | 331 |
| Food catalog | active `food_items` | 331 |
| Food catalog | `food_items` with `nutrition_facts` | 331 |
| Food catalog | `food_items` missing `nutrition_facts` | 0 |
| Food catalog | placeholder-name foods | 1 |
| Generator readiness | valid active foods for current generator rules | 320 |
| Nutrition | `nutrition_facts` rows | 331 |
| Nutrition | rows with fiber | 184 |
| Nutrition | rows with sugar | 129 |
| Nutrition | rows with sodium | 326 |
| Nutrition | rows with `micronutrients_json` | 326 |
| Nutrition | rows with non-empty `micronutrients_json` | 323 |
| Search | `food_aliases` rows | 652 |
| Search | foods with at least one alias | 326 |
| Search | empty alias rows | 0 |
| Users | `users` | 21 |
| Users | `user_profiles` | 14 |
| Users | active `user_goals` | 13 |
| Personalization | `allergies` | 2 |
| Personalization | active `allergies` | 2 |
| Personalization | `dietary_preferences` | 18 |
| Personalization | active `dietary_preferences` | 18 |
| Meals | `recipes` | 1 |
| Meals | `recipe_ingredients` | 3 |
| Meals | `meal_templates` | 2 |
| Meals | `meal_plans` | 9 |
| Meals | `meal_plan_items` | 36 |
| Vision | `classifier_labels` | 5 |
| Vision | `classifier_label_food_maps` | 0 |
| Vision | `photo_predictions` | 13 |
| Vision | `photo_prediction_candidates` | 9 |
| Vision | mappings to active foods | 0 |
| Vision | mappings to active foods with nutrition | 0 |

## Food catalog content

### Category distribution

| Category | Count |
| --- | ---: |
| `usda_import` | 326 |
| `protein` | 2 |
| `carb` | 1 |
| `fat` | 1 |
| `string` | 1 |

### Source distribution

| Source | Count |
| --- | ---: |
| `usda_fdc` | 326 |
| `manual` | 5 |

### Sample food rows

| id | name | category | serving g | source | active | kcal/100g | protein | carbs | fat |
| --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| `d4e0f097-f2f3-4bf2-b644-d6631a25b11f` | Almond butter, creamy | `usda_import` | 100.0 | `usda_fdc` | true | 645.0 | 20.8 | 21.2 | 53.0 |
| `641efec2-7832-49b1-b313-7a26de949a2a` | Almond milk, unsweetened, plain, refrigerated | `usda_import` | 100.0 | `usda_fdc` | true | 19.3 | 0.656 | 0.671 | 1.56 |
| `dbe32dad-ea95-49c7-b195-659b96ab1f96` | Almond milk, unsweetened, plain, shelf stable | `usda_import` | 100.0 | `usda_fdc` | true | 14.6 | 0.555 | 0.337 | 1.22 |
| `60d6a28f-863c-4564-8bdc-9a4e5efc8968` | Anchovies, canned in olive oil, with salt, drained | `usda_import` | 100.0 | `usda_fdc` | true | 206.0 | 26.9 | 2.41 | 9.85 |
| `fbcd38d3-70b7-42ac-8391-c70b62e266a5` | Apple juice, with added vitamin C, from concentrate, shelf stable | `usda_import` | 100.0 | `usda_fdc` | true | 48.4 | 0.086 | 11.4 | 0.286 |
| `dacb5142-32e4-4c24-be08-c7505ac83e02` | Apples, fuji, with skin, raw | `usda_import` | 100.0 | `usda_fdc` | true | 64.7 | 0.148 | 15.7 | 0.162 |
| `70ac3258-d326-482b-85ae-a73c35b8b854` | Apples, gala, with skin, raw | `usda_import` | 100.0 | `usda_fdc` | true | 61.0 | 0.133 | 14.8 | 0.15 |
| `1707073c-4fed-48af-9065-5e6a04bb12a4` | Apples, granny smith, with skin, raw | `usda_import` | 100.0 | `usda_fdc` | true | 58.9 | 0.266 | 14.1 | 0.138 |

### Suspicious nutrition values

| Issue | Count |
| --- | ---: |
| calories <= 0 | 0 |
| calories > 900 | 1 |
| protein/carbs/fat < 0 | 10 |
| protein/carbs/fat > 100 | 1 |
| protein + carbs + fat > 102 | 1 |

Sample suspicious rows:

| Food | Issue | kcal/100g | protein | carbs | fat |
| --- | --- | ---: | ---: | ---: | ---: |
| Bison, ground, raw | negative macro | 159.0 | 19.9 | -0.15 | 8.88 |
| Chicken, breast, meat and skin, raw | negative macro | 127.0 | 21.4 | -0.428 | 4.78 |
| Chicken, drumstick, meat and skin, raw | negative macro | 125.0 | 18.4 | -0.475 | 5.94 |
| Chicken, thigh, meat and skin, raw | negative macro | 188.0 | 17.1 | -0.173 | 13.4 |
| Chicken, wing, meat and skin, raw | negative macro | 168.0 | 18.4 | -0.459 | 10.6 |
| Halibut, frozen, wild caught | negative macro | 81.3 | 19.1 | -0.06 | 0.592 |
| Lamb, ground, raw | negative macro | 237.0 | 17.5 | -0.251 | 18.6 |
| Pork, belly, with skin, raw | negative macro | 380.0 | 15.2 | -0.705 | 35.8 |
| Pork, chop, center cut, raw | negative macro | 138.0 | 22.8 | -0.562 | 5.48 |
| Tuna, ahi or yellowfin, frozen, wild caught | negative macro | 102.0 | 24.7 | -0.104 | 0.388 |
| string | calories > 900, macro > 100, macro sum > 102 | 2000.0 | 1000.0 | 1000.0 | 1000.0 |

## Nutrition depth

The nutrition table is better populated than a minimal macro-only seed. There are 331 nutrition rows, 326 sodium-populated rows, and 326 rows with `micronutrients_json`. Of those, 323 are non-empty JSON blobs.

Sample micronutrient depth:

| Food | Micronutrient key count | Sample keys |
| --- | ---: | --- |
| Almond butter, creamy | 53 | alanine_g, ash_g, glycine_g, leucine_g, lysine_g, serine_g, valine_g, water_g |
| Almond milk, unsweetened, plain, refrigerated | 52 | alanine_g, ash_g, glucose_g, glycine_g, lysine_g, serine_g, valine_g, water_g |
| Almond milk, unsweetened, plain, shelf stable | 117 | ash_g, glucose_g, lactose_g, maltose_g, niacin_mg, sfa_4:0_g, sfa_5:0_g, water_g |
| Anchovies, canned in olive oil, with salt, drained | 14 | ash_g, calcium,_ca_mg, copper,_cu_mg, iron,_fe_mg, nitrogen_g, potassium,_k_mg, water_g, zinc,_zn_mg |
| Apple juice, with added vitamin C, from concentrate, shelf stable | 29 | ash_g, fructose_g, glucose_g, lactose_g, maltose_g, niacin_mg, sucrose_g, water_g |

Verdict: micronutrient data is actually populated for most imported foods. It is not mostly empty.

## Alias/search content

There are 652 aliases across 326 foods, and no empty alias rows. The aliases are useful for exact/source-name matching, but the sample shows they are mostly duplicate exact aliases rather than broader synonym coverage.

Sample alias rows:

| Food | alias_text | normalized_alias | alias_type | confidence |
| --- | --- | --- | --- | ---: |
| Almond butter, creamy | Almond butter, creamy | almond butter, creamy | exact | 1.0 |
| Almond butter, creamy | Almond butter, creamy | almond butter, creamy | source_name | 1.0 |
| Almond milk, unsweetened, plain, refrigerated | Almond milk, unsweetened, plain, refrigerated | almond milk, unsweetened, plain, refrigerated | exact | 1.0 |
| Almond milk, unsweetened, plain, refrigerated | Almond milk, unsweetened, plain, refrigerated | almond milk, unsweetened, plain, refrigerated | source_name | 1.0 |
| Apple juice, with added vitamin C, from concentrate, shelf stable | Apple juice, with added vitamin C, from concentrate, shelf stable | apple juice, with added vitamin c, from concentrate, shelf stable | exact | 1.0 |
| Apples, fuji, with skin, raw | Apples, fuji, with skin, raw | apples, fuji, with skin, raw | exact | 1.0 |

## User personalization data

| Metric | Count |
| --- | ---: |
| users | 21 |
| user_profiles | 14 |
| active_user_goals | 13 |
| allergies | 2 |
| active allergies | 2 |
| dietary_preferences | 18 |
| active dietary_preferences | 18 |

Sample active allergies:

| user prefix | allergen | severity | active |
| --- | --- | --- | --- |
| `0c14c48c...` | shellfish | moderate | true |
| `cc24c9a5...` | peanuts | moderate | true |

Sample active dietary preferences:

| user prefix | preference_type | value | active |
| --- | --- | --- | --- |
| `0c10ecc3...` | diet_type | Halal | true |
| `0c10ecc3...` | restriction | egg | true |
| `d9f0a1a7...` | diet_type | Halal | true |
| `9f83e282...` | diet_type | Halal | true |
| `8dfc028a...` | restriction | peanuts | true |
| `af193ce8...` | diet_type | Halal | true |
| `1d3c0f7a...` | diet_type | Vegetarian | true |
| `1d3c0f7a...` | diet_type | Low Carb | true |
| `3bab95f6...` | restriction | peanuts | true |

No password hashes, tokens, email addresses, or other secrets were included in this report.

## Meal-generation readiness verdict

### Can `/api/v1/meal-plans/generate` currently select real foods from the database?

Yes. There are 331 active food rows with nutrition facts, and 320 pass the current generator-style sanity checks.

### Are there enough active foods with valid nutrition facts?

Yes for a deterministic food-item generator. The usable pool is large enough for basic plans. However, the category data is weak: 326 of 331 foods are categorized only as `usda_import`, so slot suitability depends heavily on food names rather than curated meal categories.

### Does the database contain enough allergy/diet preference data to test filtering?

Barely, but yes for basic tests. There are active allergies for shellfish and peanuts, plus active preferences/restrictions such as Halal, Vegetarian, Low Carb, peanuts, and egg. This is enough to test matching behavior, but not enough to validate robust personalization.

### Does the database contain real meals/recipes/meal_templates, or only individual food items?

It contains mostly individual food items. There is 1 real recipe, 3 recipe ingredient rows, and 2 meal templates. The existing generator is therefore operating mainly on food items, not composed recipes or meal templates.

### Is the generator currently operating on a real catalog or basically an empty/weak catalog?

It is operating on a real but uneven catalog. The USDA imported foods and nutrition depth are real. The weakness is not emptiness; the weakness is product readiness: generic `usda_import` categories, limited user personalization, almost no composed meals, and no classifier-to-food mappings.

## Meal/recipe/template data

| Table | Count |
| --- | ---: |
| recipes | 1 |
| recipe_ingredients | 3 |
| meal_templates | 2 |
| meal_plans | 9 |
| meal_plan_items | 36 |

Recipe sample:

| id | name | category | diet_type | servings | calories | protein | carbs | fat |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `244eb211-8dff-43ab-93fc-a27f8c3a1156` | Chicken Rice Bowl | lunch | high_protein | 1 | 569.9 | 51.36 | 50.76 | 15.94 |

Recipe ingredient samples:

| recipe | ingredient | quantity | grams | position |
| --- | --- | --- | ---: | ---: |
| Chicken Rice Bowl | Chicken breast | 150 g | 150.0 | 1 |
| Chicken Rice Bowl | White rice | 180 g | 180.0 | 2 |
| Chicken Rice Bowl | Olive oil | 10 g | 10.0 | 3 |

Meal template samples:

| name | slot | category | diet_type | estimated calories | protein | carbs | fat |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| High Protein Breakfast Template | breakfast | breakfast | high_protein | 450.0 | 35.0 | 30.0 | 15.0 |
| Chicken Rice Bowl Template | lunch | lunch | high_protein | 650.0 | 55.0 | 58.0 | 18.0 |

Meal plan samples show persisted generated plans, but they are food-item based:

| generation_mode | item_count | sample item names |
| --- | ---: | --- |
| rule_based | 4 | Egg, white, dried; Chicken breast; Flour, soy, full-fat; Yogurt, Greek, plain, whole milk |
| rule_based | 4 | Oats, whole grain, rolled, old fashioned; Wild rice, dry, raw; Lentils, dry; Egg |
| manual | 4 | existing manual plan items present |

Conclusion: the system can persist meal plans, but generation currently creates food-item-based daily plans rather than actual recipe-based meals.

## Vision/catalog mapping readiness

| Metric | Count |
| --- | ---: |
| classifier_labels | 5 |
| classifier_label_food_maps | 0 |
| photo_predictions | 13 |
| photo_prediction_candidates | 9 |
| maps to active food items | 0 |
| maps to active food items with nutrition | 0 |

Classifier label samples:

| label_set | raw_label | normalized_label | display_label | active |
| --- | --- | --- | --- | --- |
| food101 | apple_pie | apple pie | apple pie | true |
| food101 | banana | banana | banana | true |
| food101 | fried_rice | fried rice | fried rice | true |
| food101 | grilled_salmon | grilled salmon | grilled salmon | true |
| food101 | omelette | omelette | omelette | true |

Recent photo prediction samples:

| model | status | predicted_label | confidence | mapped food |
| --- | --- | --- | ---: | --- |
| resnet50_pretrained:ResNet50_Weights.DEFAULT | completed | eggnog | 0.187622 | null |
| resnet50_pretrained:ResNet50_Weights.DEFAULT | completed | mashed potato | 0.161255 | null |
| manual_test | confirmed | test-food | 0.99 | `32b17c70-a46c-450c-9633-75fc94047cf1` |
| resnet50_pretrained:ResNet50_Weights.DEFAULT | completed | web site | 0.582031 | null |

Candidate samples are mostly unmapped, with `food_item_id = null` and `match_strategy = unmapped`.

Verdict: image predictions cannot reliably map to real food items yet. The bridge table is empty.

## Data quality problems

1. One placeholder food row exists: `name = string`, `category = string`, with impossible nutrition values of 2000 calories and 1000 g each for protein/carbs/fat per 100 g.
2. Ten USDA-imported protein foods have slightly negative carb values. These are likely import normalization artifacts, but the current generator treats negative macros as unusable.
3. Category quality is poor for meal planning. `usda_import` is a source/import category, not a meal-planning category like protein, carb, vegetable, fruit, dairy, breakfast, or snack.
4. Alias rows are present and non-empty, but mostly exact/source-name duplicates. They are useful for exact matching, not for broad user-friendly synonym matching.
5. Personalization data exists but is too sparse for realistic coverage.
6. Meal composition data is minimal: only 1 recipe and 2 templates.
7. Vision mapping data is missing: `classifier_label_food_maps` has 0 rows.
8. Existing generated plans show odd choices such as dried egg whites, soy flour, dry wild rice, and dry lentils. That suggests the generator is selecting catalog ingredients as meal items, not prepared foods or recipes.

## What is missing

- Curated food categories suitable for meal planning.
- Prepared-food or ready-to-eat variants where needed, not only raw/dry ingredients.
- A larger recipe library with `recipe_ingredients`.
- More meal templates across breakfast, lunch, dinner, and snack.
- Allergy and dietary preference fixtures for major common cases.
- Richer aliases and synonyms, including simple names like `chicken`, `rice`, `salmon`, `oats`, and plural/singular variants.
- Classifier label to food item mappings for photo workflows.
- Data cleanup for impossible placeholder/manual rows and negative macro import artifacts.

## What should be seeded next

1. Clean or remove the placeholder `string` food row.
2. Normalize small negative macro values to zero during import cleanup, or quarantine those rows from generation.
3. Add curated meal-planning categories to the USDA catalog: protein, carb, vegetable, fruit, dairy, fat, condiment, snack, breakfast.
4. Seed 30-50 prepared, realistic foods with strong categories and default serving sizes.
5. Seed 20-30 recipes with ingredients and rolled-up nutrition.
6. Seed 12-20 meal templates across common slots and diet types.
7. Seed representative allergy and preference records for filtering tests: peanuts, shellfish, dairy, gluten, vegetarian, vegan, halal, kosher, disliked_food, preferred_food.
8. Seed classifier label mappings from common labels to food items, starting with existing labels: banana, grilled salmon, omelette, fried rice, apple pie.
9. Add alias synonyms for common foods and classifier labels, not just exact/source-name duplicates.

