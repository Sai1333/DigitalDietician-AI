# apps/api/app/routers/llm_recipes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.ml.llm import LLMProvider
import re

router = APIRouter(prefix="/recipes", tags=["llm"])
llm = LLMProvider()


class RecipeRequest(BaseModel):
    ingredients: List[str]
    cuisine: Optional[str] = None
    calorie_cap: Optional[int] = None
    count: int = 2


class LlmRecipe(BaseModel):
    title: str
    cuisine: Optional[str] = None
    ingredients: List[str]
    instructions: List[str]
    macros: Dict[str, float]


# ---- Stronger, step-focused “system” rules ----
SYSTEM_RULES = (
    "You are a careful dietician and chef. "
    "Return STRICT JSON ONLY with keys: "
    "title (string), cuisine (string), ingredients (array of strings), "
    "instructions (array of strings), macros (object with numbers: calories, protein, carbs, fat). "
    "No prose, no extra keys, no code blocks, no markdown. "
    "Write instructions as a SHORT, NUMBERED, STEP-BY-STEP LIST (5–8 steps), "
    "one action per step (<= 180 chars each), food-safe (no raw eggs). "
    "Each step MUST start with a verb and include a concrete time OR temperature when applicable. "
    "Forbidden phrases: 'to taste', 'cook to taste', 'prep ingredients', 'serve'."
)


def build_prompt(ingredients: List[str], cuisine: Optional[str], cal_cap: Optional[int], n: int) -> str:
    ing_str = ", ".join(ingredients)
    cuisine_rule = (
        f"CUISINE HARD RULE: The recipe MUST be {cuisine} cuisine. "
        f"Title MUST include '{cuisine}'. Use common {cuisine} flavors/techniques."
        if cuisine
        else "If a cuisine is not specified, pick an appropriate cuisine and set the cuisine field accordingly."
    )
    cal_rule = (
        f"Keep total calories <= {cal_cap} if possible; otherwise stay close."
        if cal_cap
        else "Set macros to a reasonable estimate."
    )
    schema_hint = (
        'If generating multiple, return JSON with key "recipes" as an array of those objects. '
        'Example (single): '
        '{"title":"<title>","cuisine":"<cuisine>",'
        '"ingredients":["..."],'
        '"instructions":["1. step","2. step","3. step","4. step","5. step"],'
        '"macros":{"calories":<num>,"protein":<num>,"carbs":<num>,"fat":<num>}}'
    )
    return (
        f"{SYSTEM_RULES}\n"
        f"Generate exactly {n} recipe(s).\n"
        f"{cuisine_rule}\n"
        f"{cal_rule}\n"
        f"Ingredients available: {ing_str}\n"
        f"{schema_hint}"
    )
import re
BAD_PHRASES = {"to taste", "cook to taste", "prep ingredients", "serve"}

def _normalize_instructions(x) -> List[str]:
    if isinstance(x, list):
        parts = [str(p).strip() for p in x]
    elif isinstance(x, str):
        parts = re.split(r"(?:\n+|(?<=[.!?])\s+)", x.strip())
    else:
        parts = []
    parts = [p for p in parts if p and len(p) >= 4]

    if len(parts) < 5:
        alt = []
        for p in parts:
            alt.extend([s.strip() for s in re.split(r";\s*", p) if s.strip()])
        if len(alt) >= 5:
            parts = alt

    parts = parts[:12]

    # add numbering if missing
    numbered = []
    for i, p in enumerate(parts, 1):
        if re.match(r"^\d+[\.)]\s", p):
            numbered.append(p)
        else:
            numbered.append(f"{i}. {p}")

    if len(numbered) < 5:
        while len(numbered) < 5:
            numbered.append(f"{len(numbered)+1}. Finish cooking and plate.")
        numbered = numbered[:12]
    return numbered

def _is_vague_step(s: str) -> bool:
    s_low = s.lower()
    if any(bp in s_low for bp in BAD_PHRASES):
        return True
    # Reject steps with no verbs or purely generic words
    if not re.match(r"^\d+[\.)]\s*[A-Za-z]", s):
        return True
    # Encourage presence of time/heat words (min, sec, heat, °, medium, simmer)
    if not re.search(r"\b(min|sec|seconds|minutes|medium|low|high|simmer|boil|°|degree|heat)\b", s_low):
        # Not strictly an error, but helps filter very generic steps
        # Treat as vague if the sentence is very short
        return len(s) < 20
    return False

def _fix_instructions(steps: List[str]) -> List[str]:
    steps = _normalize_instructions(steps)
    cleaned = []
    for s in steps:
        if _is_vague_step(s):
            # nudge with a default pattern if it’s too vague
            s = re.sub(r"^\d+[\.)]\s*", "", s).strip()
            if len(s) < 20:
                s = "Add and cook on medium heat for 2–3 min."
        cleaned.append(s)
    # re-number
    return [f"{i}. {re.sub(r'^\d+[\.)]\s*','',t)}" for i, t in enumerate(cleaned, 1)]



def cuisine_matches(resp: Dict[str, Any], desired: str) -> bool:
    if not desired:
        return True
    desired_l = desired.strip().lower()
    title = str(resp.get("title", "")).lower()
    rcuisine = str(resp.get("cuisine", "")).lower()
    # accept if cuisine field matches or title contains keyword like 'thai-style'
    return desired_l in rcuisine or desired_l in title


# ---- Instruction normalizer: ensures numbered 5–12 steps ----
def _normalize_instructions(x) -> List[str]:
    """
    Accepts a list of strings and returns
    a numbered 10–20 step list with concise, trimmed steps.
    """
    if isinstance(x, list):
        parts = [str(p).strip() for p in x]
    elif isinstance(x, str):
        # split by newlines or sentence boundaries
        parts = re.split(r"(?:\n+|(?<=[.!?])\s+)", x.strip())
    else:
        parts = []

    # basic cleanup
    parts = [p for p in parts if p and len(p) >= 4]

    # If still too short, try splitting by semicolons
    if len(parts) < 5:
        alt = []
        for p in parts:
            alt.extend([s.strip() for s in re.split(r";\s*", p) if s.strip()])
        if len(alt) >= 5:
            parts = alt

    # Limit to 12 steps max
    parts = parts[:12]

    # If still fewer than 5 steps, try to create reasonable splits
    if len(parts) < 5 and len(parts) > 0:
        # As a last resort, split long items by ' and ' or ', then '
        expanded: List[str] = []
        for p in parts:
            chunks = re.split(r"\s+(?:and|then)\s+", p)
            expanded.extend([c.strip() for c in chunks if c.strip()])
        parts = [p for p in expanded if p][:12]

    # Number them if not already
    numbered: List[str] = []
    for i, p in enumerate(parts, 1):
        if re.match(r"^\d+[\.)]\s", p):
            numbered.append(p)
        else:
            numbered.append(f"{i}. {p}")

    # Ensure we have 5–12
    if len(numbered) < 5:
        # pad with generic safe end-steps if absolutely necessary
        while len(numbered) < 5:
            numbered.append(f"{len(numbered)+1}. Serve and enjoy.")
        numbered = numbered[:12]

    return numbered


@router.post("/llm_generate")
def llm_generate(body: RecipeRequest):
    if not body.ingredients:
        raise HTTPException(status_code=400, detail="ingredients required")

    # 1) Build prompt + call
    prompt = build_prompt(body.ingredients, body.cuisine, body.calorie_cap, body.count)
    data = llm.generate_json(prompt)

    # Accept either a single-recipe dict or {"recipes":[...]}
    recipes: List[Dict[str, Any]] = []
    if isinstance(data, dict) and "recipes" in data and isinstance(data["recipes"], list):
        recipes = data["recipes"]
    elif isinstance(data, dict):
        recipes = [data]
    else:
        raise HTTPException(status_code=500, detail=f"Invalid LLM output: {data!r}")

    # If cuisine strict and some items fail, try one retry
    if body.cuisine and not all(cuisine_matches(r, body.cuisine) for r in recipes):
        retry_prompt = (
            build_prompt(body.ingredients, body.cuisine, body.calorie_cap, body.count)
            + "\nYou DID NOT follow the cuisine rule. Regenerate. "
              "The 'cuisine' field MUST be exactly the requested cuisine, "
              "and each 'title' MUST include that cuisine keyword."
        )
        data2 = llm.generate_json(retry_prompt)
        if isinstance(data2, dict) and "recipes" in data2 and isinstance(data2["recipes"], list):
            recipes = data2["recipes"]
        elif isinstance(data2, dict):
            recipes = [data2]
        # else keep originals but we will stamp cuisine field as fallback
        for r in recipes:
            if not cuisine_matches(r, body.cuisine):
                r["cuisine"] = body.cuisine

    # Map -> normalized shape
    out: List[LlmRecipe] = []
    for r in recipes[: max(1, body.count)]:
        title = str(r.get("title") or "Untitled Recipe").strip()
        cuisine = str(r.get("cuisine") or (body.cuisine or "")).strip() or None
        ingredients = [str(i).strip() for i in (r.get("ingredients") or [])]
        instructions_raw = r.get("instructions") or []
        instructions = _fix_instructions(instructions_raw)

        macros = r.get("macros") or {}
        def n(x, default=0.0):
            try: return float(x)
            except Exception: return float(default)
        macros = {
            "calories": n(macros.get("calories"), 0),
            "protein": n(macros.get("protein"), 0),
            "carbs": n(macros.get("carbs"), 0),
            "fat": n(macros.get("fat"), 0),
        }

        out.append(LlmRecipe(
            title=title,
            cuisine=cuisine,
            ingredients=ingredients,
            instructions=instructions,
            macros=macros,
        ))

    # For backward compat you were returning one LlmRecipe earlier;
    # but your latest curl showed {"recipes":[...]}.
    # We’ll return the array to match your latest behavior.
    return {"recipes": [o.model_dump() for o in out]}
