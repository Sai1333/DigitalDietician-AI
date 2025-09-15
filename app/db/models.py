from sqlalchemy import Column, Integer, String, Date
from .database import Base

class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    unit = Column(String)
    expiry_date = Column(Date, nullable=True)

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship

# PantryItem class (already exists above)

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    ingredients = Column(Text)  # store as comma-separated or JSON string
    instructions = Column(Text, nullable=True)
    calories = Column(Integer, nullable=True)
    protein = Column(Integer, nullable=True)
    carbs = Column(Integer, nullable=True)
    fat = Column(Integer, nullable=True)
    time_minutes = Column(Integer, nullable=True, default=15)