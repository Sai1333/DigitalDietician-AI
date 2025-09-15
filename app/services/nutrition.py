# apps/api/app/services/nutrition.py
from __future__ import annotations
from typing import Dict

# Very small per-100g defaults (MVP). Extend as you go.
NUTRITION_TABLE: Dict[str, Dict[str, float]] = {
    "egg":         {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11},
    "rice":        {"calories": 130, "protein": 2.7, "carbs": 28,  "fat": 0.3},
    "bread":       {"calories": 265, "protein": 9,   "carbs": 49,  "fat": 3.2},
    "butter":      {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81},
    "tomato":      {"calories": 18,  "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "paneer":      {"calories": 321, "protein": 21,  "carbs": 3.6, "fat": 25},
    "tofu":        {"calories": 76,  "protein": 8,   "carbs": 1.9, "fat": 4.8},
    "oats":        {"calories": 389, "protein": 17,  "carbs": 66,  "fat": 7},
    "chickpeas":   {"calories": 164, "protein": 9,   "carbs": 27,  "fat": 2.6},
    "cheese":      {"calories": 402, "protein": 25,  "carbs": 1.3, "fat": 33},
    "maggi":       {"calories": 436, "protein": 10,  "carbs": 60,  "fat": 17},
    "peanut":      {"calories": 567, "protein": 26,  "carbs": 16,  "fat": 49},
    "curd":        {"calories": 98,  "protein": 11,  "carbs": 3.4, "fat": 5},
    "milk":        {"calories": 60,  "protein": 3.2, "carbs": 5,   "fat": 3.3},
    "oil":         {"calories": 884, "protein": 0,   "carbs": 0,   "fat": 100},
    "soy":         {"calories": 446, "protein": 36,  "carbs": 30,  "fat": 20},
}

# MVP heuristic weights per ingredient mention when no grams are given.
# This keeps it simple until you switch to structured ingredients.
DEFAULT_GRAMS = {
    "egg": 50, "rice": 150, "bread": 60, "butter": 10, "tomato": 100,
    "paneer": 120, "tofu": 120, "oats": 40, "chickpeas": 120, "cheese": 40,
    "maggi": 70, "peanut": 20, "curd": 200, "milk": 200, "oil": 10, "soy": 30,
}

def estimate_macros_from_string(ingredients_str: str) -> Dict[str, int]:
    """
    Very rough estimator: splits on commas, maps tokens to known ingredients,
    applies DEFAULT_GRAMS, sums per-100g values.
    Returns rounded ints (calories, protein, carbs, fat).
    """
    parts = [p.strip().lower() for p in (ingredients_str or "").split(",") if p.strip()]
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    for p in parts:
        name = p.split()[0]  # first token as key (e.g., "egg", "rice")
        if name not in NUTRITION_TABLE:
            continue
        grams = DEFAULT_GRAMS.get(name, 100)
        factor = grams / 100.0
        macro = NUTRITION_TABLE[name]
        totals["calories"] += macro["calories"] * factor
        totals["protein"]  += macro["protein"]  * factor
        totals["carbs"]    += macro["carbs"]    * factor
        totals["fat"]      += macro["fat"]      * factor
    return {k: int(round(v)) for k, v in totals.items()}
