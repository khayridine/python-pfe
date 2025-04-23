# operation.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Operation
from typing import List
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Dépendance DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schéma de sortie
class OperationOut(BaseModel):
    id: int
    type: str
    date: date
    statut: str
    montant: float
    taxe: float
    frais: float

    class Config:
        orm_mode = True

# Route GET pour toutes les opérations
@router.get("/operations", response_model=List[OperationOut])
def get_operations(db: Session = Depends(get_db)):
    return db.query(Operation).all()
