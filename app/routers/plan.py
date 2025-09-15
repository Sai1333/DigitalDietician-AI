# apps/api/app/routers/plan.py
from fastapi import APIRouter, Query
from typing import Dict, Any, List

router = APIRouter(tags=["planner"])

# Minimal local fallback so we don't depend on recipe.py internals.
# You can swap this later for your real nutrition service.
def _macros_for(ingredients_text: str) -> Dict[str, float]:
    text = (ingredients_text or "").lower()
    cal = 0.0; p = 0.0; c = 0.0; f = 0.0

    # very rough heuristics just to keep the endpoint alive
    if "egg" in text:
        cal += 155; p += 13; c += 1.1; f += 11
    if "rice" in text:
        cal += 130; p += 2.7; c += 28; f += 0.3
    if "tomato" in text:
        cal += 18; p += 0.9; c += 3.9; f += 0.2
    if "milk" in text:
        cal += 60; p += 3.2; c += 5; f += 3.3

    return {
        "calories": round(cal, 1),
        "protein": round(p, 1),
        "carbs": round(c, 1),
        "fat": round(f, 1),
    }

@router.get("/plan/day")
def plan_day(
    protein_target: int = Query(120, ge=10, le=300),
    calorie_cap: int = Query(1800, ge=500, le=4000),
) -> Dict[str, Any]:
    """
    Very simple placeholder planner that returns an empty meal list
    but keeps the API contract alive. Replace with your deterministic
    planner when ready.
    """
    return {
        "meals": [],
        "totals": {"calories": calorie_cap, "protein": protein_target, "carbs": 0, "fat": 0},
    }
