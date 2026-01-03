from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate

router = APIRouter(tags=["Cycles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/cycles")
def create_cycle(cycle: CycleCreate, db: Session = Depends(get_db)):
    new_cycle = Cycle(**cycle.dict())
    db.add(new_cycle)
    db.commit()
    db.refresh(new_cycle)
    return new_cycle