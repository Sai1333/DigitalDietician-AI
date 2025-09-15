# apps/api/app/routers/recipe.py
from __future__ import annotations

import re
from typing import List, Set, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Recipe, PantryItem
from app.schemas.recipe import RecipeCreate, RecipeOut
from app.services.ranker import nutrition_fit, time_fit, final_score
from app.services.nutrition import estimate_macros_from_string

router = APIRouter(prefix="/recipes", tags=["recipes"])


# ---------- DB session dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Helpers ----------
def _parse_ingredients(raw: str) -> Set[str]:
    """MVP parser: split comma-separated ingredients to a lowercase set."""
    if not raw:
        return set()
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def _tokens(s: str) -> Set[str]:
    return set(re.findall(r"[a-zA-Z]+", (s or "").lower()))


def _query_match_score(q: str, title: str, ingredients: str) -> float:
    """Very light text relevance: overlap between query tokens and title+ingredient tokens."""
    if not q:
        return 0.0
    qset = _tokens(q)
    tset = _tokens(title) | _tokens(ingredients)
    if not qset or not tset:
        return 0.0
    overlap = len(qset & tset)
    return round(overlap / max(1, len(qset)), 3)


def _macros_for(r: Recipe) -> Dict[str, int]:
    """
    Use DB macros if present, otherwise compute from ingredient string (fallback).
    Returns dict with calories, protein, carbs, fat (ints).
    """
    if None in (r.calories, r.protein, r.carbs, r.fat):
        est = estimate_macros_from_string(r.ingredients or "")
        return {
            "calories": est["calories"],
            "protein": est["protein"],
            "carbs": est["carbs"],
            "fat": est["fat"],
        }
    return {
        "calories": int(r.calories or 0),
        "protein": int(r.protein or 0),
        "carbs": int(r.carbs or 0),
        "fat": int(r.fat or 0),
    }


# ---------- CRUD ----------
@router.post("/add", response_model=RecipeOut)
def add_recipe(payload: RecipeCreate, db: Session = Depends(get_db)):
    recipe = Recipe(**payload.dict())
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("/list", response_model=List[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).all()


# ---------- Smart Suggest (ingredients + time + nutrition) ----------
@router.get("/suggest")
def suggest_recipes(
    max_time: int = Query(20, ge=5, le=240),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    pantry = {p.name.lower() for p in db.query(PantryItem).all()}

    rows = db.query(Recipe).all()
    scored = []
    for r in rows:
        ings = _parse_ingredients(r.ingredients)
        if not ings:
            continue
        have = len(ings & pantry)
        ing_score = round(have / len(ings), 3)

        macros = _macros_for(r)
        t_score = time_fit(r.time_minutes or 15, max_time)
        n_score = nutrition_fit({"protein": macros["protein"], "calories": macros["calories"]})

        s = final_score(ing_score, t_score, n_score)
        scored.append(
            {
                "id": r.id,
                "title": r.title,
                "ingredients": r.ingredients,
                "time_minutes": r.time_minutes,
                "macros": macros,
                "fit": {"ingredients": ing_score, "time": t_score, "nutrition": n_score},
                "score": s,
                "explanation": f"Uses {have}/{len(ings)} pantry items · {r.time_minutes or 15} min · {macros['protein']}g protein",
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"results": scored[:limit], "pantry": sorted(list(pantry)), "max_time": max_time}


# ---------- Text Search (query + filters + ranking) ----------
@router.get("/search")
def search_recipes(
    q: str = Query("", description="search text, e.g. 'high protein egg'"),
    max_time: int = Query(30, ge=5, le=240),
    min_protein: int = Query(0, ge=0, le=200),
    max_calories: int = Query(10000, ge=1, le=20000),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    pantry = {p.name.lower() for p in db.query(PantryItem).all()}
    rows = db.query(Recipe).all()

    results = []
    for r in rows:
        macros = _macros_for(r)

        # basic filters
        if macros["protein"] < min_protein:
            continue
        if macros["calories"] > max_calories:
            continue

        ings = _parse_ingredients(r.ingredients)
        have = len(ings & pantry)
        ing_score = round(have / len(ings), 3) if ings else 0.0
        t_score = time_fit(r.time_minutes or 15, max_time)
        n_score = nutrition_fit({"protein": macros["protein"], "calories": macros["calories"]})
        base_score = final_score(ing_score, t_score, n_score)

        q_score = _query_match_score(q, r.title or "", r.ingredients or "")
        total = round(0.85 * base_score + 0.15 * q_score, 4)

        results.append(
            {
                "id": r.id,
                "title": r.title,
                "ingredients": r.ingredients,
                "time_minutes": r.time_minutes,
                "macros": macros,
                "fit": {"ingredients": ing_score, "time": t_score, "nutrition": n_score, "query": q_score},
                "score": total,
                "explanation": f"q:{q_score} · ing:{ing_score} · time:{t_score} · nut:{n_score}",
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return {
        "query": q,
        "filters": {"max_time": max_time, "min_protein": min_protein, "max_calories": max_calories},
        "pantry": sorted(list(pantry)),
        "results": results[:limit],
    }
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import SessionLocal
from app.db.models import Recipe  # adjust if your Recipe model lives elsewhere

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/recipes/search", tags=["recipes"])
def search_recipes(
    q: str = "",
    max_time: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    qs = db.query(Recipe)
    if q:
        like = f"%{q}%"
        qs = qs.filter(or_(Recipe.title.ilike(like), Recipe.ingredients.ilike(like)))
    if max_time:
        qs = qs.filter((Recipe.time_minutes == None) | (Recipe.time_minutes <= max_time))  # noqa

    rows: List[Recipe] = qs.limit(limit).all()

    results = []
    for r in rows:
        macros = {
            "calories": r.calories or 0,
            "protein": r.protein or 0,
            "carbs": r.carbs or 0,
            "fat": r.fat or 0,
        }
        results.append({
            "id": r.id,
            "title": r.title,
            "ingredients": r.ingredients,
            "time_minutes": r.time_minutes or 15,
            "macros": macros,
            "fit": {
                "ingredients": 0.0,
                "time": 1.0 if (r.time_minutes or 15) <= max_time else 0.0,
                "nutrition": 0.0,
            },
            "score": 0.5,
        })
    return {"results": results}



# ---------- Maintenance: recompute & persist macros for missing ones ----------
@router.post("/recompute_macros")
def recompute_macros(db: Session = Depends(get_db)):
    """
    For any recipe missing macros, estimate from ingredients (string-based MVP),
    save back to DB, and return a summary.
    """
    rows = db.query(Recipe).all()
    updated = 0
    items = []
    for r in rows:
        if None in (r.calories, r.protein, r.carbs, r.fat):
            est = estimate_macros_from_string(r.ingredients or "")
            if sum(est.values()) == 0:
                continue
            r.calories = est["calories"]
            r.protein = est["protein"]
            r.carbs = est["carbs"]
            r.fat = est["fat"]
            db.add(r)
            db.commit()
            db.refresh(r)
            updated += 1
            items.append({"id": r.id, "title": r.title, "macros": est})
    return {"updated": updated, "items": items}
