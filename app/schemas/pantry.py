from pydantic import BaseModel
from datetime import date
from typing import Optional

class PantryCreate(BaseModel):
    name: str
    quantity: int = 1
    unit: str = "unit"
    expiry_date: Optional[date] = None

class PantryOut(BaseModel):
    id: int
    name: str
    quantity: int
    unit: str
    expiry_date: Optional[date]

    class Config:
        from_attributes = True  # Pydantic v2: map from SQLAlchemy model
