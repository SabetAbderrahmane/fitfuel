# RecipeNLG Import Report

RecipeNLG-derived data is thesis/demo-only and must be removed or replaced before commercialization.

## Run configuration

- File: `C:\Users\Administrator\Desktop\work\mibchar\fitfuel\backend\data\raw\recipenlg\RecipeNLG_dataset.csv`
- Dry run: `False`
- Target count: `1000`
- Target breakfast count: `150`
- Target lunch count: `350`
- Target dinner count: `350`
- Target snack count: `150`
- Scan limit: `None`
- Source filter: `Gathered`
- Min match ratio: `0.7`
- Fuzzy threshold: `85`
- Exclude desserts from meals: `True`
- Allow dessert snacks: `False`
- Slot calorie ranges: `breakfast 250-700 kcal, lunch 350-850 kcal, dinner 350-900 kcal, snack 100-400 kcal`
- High protein thresholds: `25g` and `0.25` protein-calorie ratio
- Strict: `False`
- Force updates: `False`

## Summary

- Rows scanned: 291000
- Recipes considered: 154846
- Recipes imported: 1000
- Recipes skipped: 289943
- Average match ratio: 0.809

## Slot quota results

| Slot | Target | Achieved | Deficit |
| --- | ---: | ---: | ---: |
| breakfast | 150 | 150 | 0 |
| lunch | 350 | 350 | 0 |
| dinner | 350 | 350 | 0 |
| snack | 150 | 150 | 0 |

## Slot quota examples

### Breakfast

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 569.15 | 43.1 | 34.12 | 0.714 | 23.49 | Breakfast Quiche |
| 294.71 | 40.22 | 4.67 | 1.0 | 22.65 | Buttermilk Pancakes |
| 477.25 | 48.12 | 18.55 | 0.8 | 29.13 | Baked French Toast |
| 602.62 | 125.17 | 3.56 | 0.75 | 17.89 | Potato Pancakes |
| 251.01 | 1.3 | 11.41 | 0.75 | 33.85 | Cinnamon Swirl Breakfast Muffins |

### Lunch

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 767.05 | 37.82 | 63.93 | 0.8 | 10.4 | Strawberry Salad |
| 428.49 | 56.41 | 3.65 | 0.714 | 41.04 | Cranberry Salad |
| 756.19 | 58.94 | 36.16 | 1.0 | 48.67 | Potato Tuna Chowder |
| 645.9 | 73.25 | 20.51 | 1.0 | 42.28 | Pork Chops And Rice For Two |
| 407.03 | 5.89 | 21.33 | 1.0 | 46.19 | Spaghetti Parmesan |

### Dinner

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 741.54 | 52.3 | 18.57 | 0.7 | 86.31 | Chicken-Rice Casserole |
| 890.5 | 42.72 | 56.27 | 1.0 | 51.21 | Potato-Beef Casserole(Microwave) |
| 755.64 | 90.06 | 34.0 | 0.833 | 23.34 | Broccoli Casserole |
| 611.4 | 20.3 | 50.22 | 0.833 | 20.09 | Twice-Baked Potato Casserole |
| 872.07 | 164.64 | 14.69 | 0.75 | 22.41 | Easy Oven Stew |

### Snack

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 196.8 | 11.74 | 2.81 | 0.8 | 29.41 | Cinnamon Apple Mold Salad |
| 277.99 | 17.66 | 17.76 | 0.75 | 12.35 | Cherry Delight |
| 314.23 | 44.26 | 2.6 | 1.0 | 27.5 | Blueberry Yogurt Shake |
| 379.14 | 28.96 | 22.77 | 1.0 | 15.11 | Frozen Bananas |
| 295.48 | 16.75 | 20.41 | 1.0 | 11.55 | Apple Pizza |

## Quality-control rejects

- Rejected dessert/junk recipes: 123746
- Rejected calorie range recipes: 29936
- Ignored minor unmatched ingredients: 58724

## Bucket counts

| Item | Count |
| --- | ---: |
| breakfast | 150 |
| lunch | 350 |
| dinner | 350 |
| high_protein | 306 |
| vegetarian_candidate | 537 |
| halal_candidate | 897 |
| gluten_free_candidate | 697 |
| dairy_free_candidate | 292 |
| egg_free_candidate | 628 |
| peanut_free_candidate | 681 |
| low_carb | 266 |
| snack | 150 |
| general_balanced | 215 |
| vegan_candidate | 67 |

## Allergen flag counts

| Item | Count |
| --- | ---: |
| contains_alcohol | 7 |
| contains_dairy | 708 |
| contains_egg | 372 |
| contains_fish | 209 |
| contains_gluten | 303 |
| contains_peanut | 319 |
| contains_pork | 96 |
| contains_sesame | 3 |
| contains_shellfish | 16 |
| contains_soy | 4 |
| contains_tree_nuts | 564 |

## Diet tag counts

| Item | Count |
| --- | ---: |
| balanced | 215 |
| dairy_free_candidate | 292 |
| egg_free_candidate | 628 |
| gluten_free_candidate | 697 |
| halal_candidate | 897 |
| high_protein | 306 |
| kosher_candidate | 891 |
| low_carb | 266 |
| nut_free_candidate | 307 |
| peanut_free_candidate | 681 |
| vegan_candidate | 67 |
| vegetarian_candidate | 537 |

## Skip reasons

| Item | Count |
| --- | ---: |
| dessert or junk title | 123746 |
| low ingredient match ratio | 108095 |
| slot calorie range failed | 29936 |
| bucket temporarily saturated | 14758 |
| ingredient count outside limits | 9997 |
| missing or unclear directions | 2411 |
| duplicate RecipeNLG recipe | 1000 |

## Top unmatched ingredients

| Item | Count |
| --- | ---: |
| too few distinct matched food items | 16587 |
| margarine | 10992 |
| mayonnaise | 8217 |
| brown sugar | 7899 |
| green pepper | 7517 |
| lemon juice | 7306 |
| cream of mushroom soup | 7095 |
| vinegar | 6665 |
| cream of chicken soup | 6504 |
| worcestershire sauce | 5496 |
| bread crumbs | 4095 |
| soy sauce | 3517 |
| green onions | 3428 |
| hamburger | 3398 |
| chicken broth | 3161 |
| garlic powder | 3135 |
| oregano | 3106 |
| black pepper | 3064 |
| clove garlic | 2890 |
| oleo | 2760 |
| chili powder | 2756 |
| bell pepper | 2715 |
| marshmallows | 2667 |
| vegetable oil | 2580 |
| powdered sugar | 2550 |
| pineapple juice | 2384 |
| catsup | 2365 |
| cornstarch | 2336 |
| garlic salt | 2282 |
| dry mustard | 2089 |

## Ignored minor unmatched ingredients

| Item | Count |
| --- | ---: |
| pepper | 18538 |
| vanilla | 8159 |
| cinnamon | 6390 |
| parsley | 6108 |
| baking powder | 5771 |
| boiling water | 3766 |
| paprika | 3721 |
| baking soda | 3493 |
| nutmeg | 2778 |

## Suspicious high-protein rejects

_None._

## Accepted examples by slot

### Breakfast

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 569.15 | 43.1 | 34.12 | 0.714 | 23.49 | Breakfast Quiche |
| 294.71 | 40.22 | 4.67 | 1.0 | 22.65 | Buttermilk Pancakes |
| 477.25 | 48.12 | 18.55 | 0.8 | 29.13 | Baked French Toast |
| 602.62 | 125.17 | 3.56 | 0.75 | 17.89 | Potato Pancakes |
| 251.01 | 1.3 | 11.41 | 0.75 | 33.85 | Cinnamon Swirl Breakfast Muffins |

### Lunch

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 767.05 | 37.82 | 63.93 | 0.8 | 10.4 | Strawberry Salad |
| 428.49 | 56.41 | 3.65 | 0.714 | 41.04 | Cranberry Salad |
| 756.19 | 58.94 | 36.16 | 1.0 | 48.67 | Potato Tuna Chowder |
| 645.9 | 73.25 | 20.51 | 1.0 | 42.28 | Pork Chops And Rice For Two |
| 407.03 | 5.89 | 21.33 | 1.0 | 46.19 | Spaghetti Parmesan |

### Dinner

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 741.54 | 52.3 | 18.57 | 0.7 | 86.31 | Chicken-Rice Casserole |
| 890.5 | 42.72 | 56.27 | 1.0 | 51.21 | Potato-Beef Casserole(Microwave) |
| 755.64 | 90.06 | 34.0 | 0.833 | 23.34 | Broccoli Casserole |
| 611.4 | 20.3 | 50.22 | 0.833 | 20.09 | Twice-Baked Potato Casserole |
| 872.07 | 164.64 | 14.69 | 0.75 | 22.41 | Easy Oven Stew |

### Snack

| calories | carbs_g | fat_g | match_ratio | protein_g | title |
| --- | --- | --- | --- | --- | --- |
| 196.8 | 11.74 | 2.81 | 0.8 | 29.41 | Cinnamon Apple Mold Salad |
| 277.99 | 17.66 | 17.76 | 0.75 | 12.35 | Cherry Delight |
| 314.23 | 44.26 | 2.6 | 1.0 | 27.5 | Blueberry Yogurt Shake |
| 379.14 | 28.96 | 22.77 | 1.0 | 15.11 | Frozen Bananas |
| 295.48 | 16.75 | 20.41 | 1.0 | 11.55 | Apple Pizza |

## Examples of imported recipes

| buckets | calories | carbs_g | fat_g | match_ratio | meal_slot | protein_g | title |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ['egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'kosher_candidate', 'lunch', 'peanut_free_candidate', 'vegetarian_candidate'] | 767.05 | 37.82 | 63.93 | 0.8 | lunch | 10.4 | Strawberry Salad |
| ['dairy_free_candidate', 'egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'lunch', 'nut_free_candidate', 'peanut_free_candidate'] | 428.49 | 56.41 | 3.65 | 0.714 | lunch | 41.04 | Cranberry Salad |
| ['balanced', 'egg_free_candidate', 'general_balanced', 'gluten_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'lunch'] | 756.19 | 58.94 | 36.16 | 1.0 | lunch | 48.67 | Potato Tuna Chowder |
| ['balanced', 'dairy_free_candidate', 'egg_free_candidate', 'general_balanced', 'gluten_free_candidate', 'high_protein', 'lunch', 'nut_free_candidate', 'peanut_free_candidate'] | 645.9 | 73.25 | 20.51 | 1.0 | lunch | 42.28 | Pork Chops And Rice For Two |
| ['egg_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'low_carb', 'lunch'] | 407.03 | 5.89 | 21.33 | 1.0 | lunch | 46.19 | Spaghetti Parmesan |
| ['dairy_free_candidate', 'egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'lunch', 'peanut_free_candidate'] | 828.65 | 73.44 | 20.02 | 1.0 | lunch | 83.32 | Chicken Rice Soup |
| ['balanced', 'general_balanced', 'gluten_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'lunch', 'peanut_free_candidate', 'vegetarian_candidate'] | 466.05 | 43.29 | 19.55 | 1.0 | lunch | 29.17 | Egg Custard |
| ['dairy_free_candidate', 'egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'high_protein', 'kosher_candidate', 'lunch', 'peanut_free_candidate'] | 678.5 | 58.53 | 12.78 | 0.857 | lunch | 76.31 | Goup |
| ['egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'kosher_candidate', 'lunch', 'vegetarian_candidate'] | 416.9 | 36.05 | 28.18 | 0.857 | lunch | 7.26 | Okra And Tomatoes |
| ['egg_free_candidate', 'gluten_free_candidate', 'halal_candidate', 'kosher_candidate', 'lunch', 'vegetarian_candidate'] | 818.78 | 61.11 | 50.8 | 0.857 | lunch | 30.99 | Potato Soup |

## Examples of skipped recipes

| reason | title |
| --- | --- |
| dessert or junk title | No-Bake Nut Cookies |
| slot calorie range failed | Jewell Ball'S Chicken |
| low ingredient match ratio | Creamy Corn |
| low ingredient match ratio | Chicken Funny |
| low ingredient match ratio | Reeses Cups(Candy) |
| low ingredient match ratio | Cheeseburger Potato Soup |
| dessert or junk title | Rhubarb Coffee Cake |
| low ingredient match ratio | Scalloped Corn |
| slot calorie range failed | Nolan'S Pepper Steak |
| dessert or junk title | Millionaire Pie |

## Notes

- Importer only matches ingredients to existing active `FoodItem` rows.
- Importer does not create `FoodItem`, `NutritionFact`, `food_logs`, meal logs, users, or meal plans.
- Nutrition totals are estimated from matched `NutritionFact` macros and conservative gram defaults.
- Allergen and diet classifications are ingredient-based heuristic flags, not medical certification.