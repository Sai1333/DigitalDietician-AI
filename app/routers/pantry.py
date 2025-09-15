from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models import PantryItem
from app.schemas.pantry import PantryCreate, PantryOut

router = APIRouter(prefix="/pantry", tags=["pantry"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/list", response_model=List[PantryOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(PantryItem).order_by(PantryItem.id.desc()).all()

@router.post("/add", response_model=PantryOut)
def add_item(payload: PantryCreate, db: Session = Depends(get_db)):
    item = PantryItem(
        name=payload.name,
        quantity=payload.quantity,
        unit=payload.unit,
        expiry_date=payload.expiry_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
