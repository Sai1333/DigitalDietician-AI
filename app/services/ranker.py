from typing import Dict

def nutrition_fit(macros: Dict[str, int], target_protein: int = 30, calorie_cap: int = 600) -> float:
    """Return 0..1 based on hitting protein target and staying under calorie cap."""
    p = macros.get("protein", 0) or 0
    c = macros.get("calories", 10**9) or 10**9
    protein_score = min(p / target_protein, 1.0)          # 1 if >= target
    calorie_score = 1.0 if c <= calorie_cap else max(0.2, 1 - (c - calorie_cap) / 1000)
    return round(0.6 * protein_score + 0.4 * calorie_score, 3)

def time_fit(time_minutes: int, max_time: int) -> float:
    if time_minutes is None:
        return 0.5
    if time_minutes <= max_time:
        return 1.0
    # linear decay beyond cap
    return round(max(0.0, 1 - (time_minutes - max_time) / max(10, max_time)), 3)

def final_score(ing: float, t: float, nut: float) -> float:
    # weights: ingredients 0.5, time 0.2, nutrition 0.3
    return round(0.5 * ing + 0.2 * t + 0.3 * nut, 4)
