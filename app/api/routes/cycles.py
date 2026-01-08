from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.cycle import Cycle
from app.models.clinical_history import ClinicalHistory
from app.schemas.cycle import CycleCreate, CycleUpdate, CycleResponse


router = APIRouter(
    prefix="/cycles",
    tags=["Cycles"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CycleResponse)
def create_cycle(
    data: CycleCreate,
    db: Session = Depends(get_db)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_history == data.id_history)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Clinical history not found")

    cycle = Cycle(**data.dict())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)

    return cycle

@router.get(
    "/history/{id_history}",
    response_model=list[CycleResponse]
)
def get_cycles_by_history(
    id_history: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Cycle)
        .filter(Cycle.id_history == id_history)
        .order_by(Cycle.period_start_date.desc())
        .all()
    )

@router.patch(
    "/{id_cycle_entry}",
    response_model=CycleResponse
)
def update_cycle(
    id_cycle_entry: int,
    data: CycleUpdate,
    db: Session = Depends(get_db)
):
    cycle = (
        db.query(Cycle)
        .filter(Cycle.id_cycle_entry == id_cycle_entry)
        .first()
    )

    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(cycle, key, value)

    db.commit()
    db.refresh(cycle)

    return cycle