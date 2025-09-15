from pydantic import BaseModel
from typing import Optional

class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    ingredients: str  # later we can change this to List[str]
    instructions: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[int] = None
    carbs: Optional[int] = None
    fat: Optional[int] = None
    time_minutes: Optional[int] = 15

class RecipeOut(RecipeCreate):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 setting to load from SQLAlchemy objects
