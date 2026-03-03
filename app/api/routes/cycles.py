from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.schemas.cycle import (
    CycleCreate,
    CycleUpdate,
    CycleResponse
)

router = APIRouter(
    prefix="/cycles",
    tags=["Cycles"]
)

# validate clinical history exists for user, if not create it
def get_or_create_clinical_history(
    db: Session,
    current_user: User
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )

    if history:
        return history

    history = ClinicalHistory(
        id_user=current_user.id_user
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history

# Create cycle entry (private)
@router.post("/", response_model=CycleResponse)
def create_cycle(
    data: CycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = get_or_create_clinical_history(db, current_user)

    cycle = Cycle(
        **data.dict(),
        id_history=history.id_history
    )

    db.add(cycle)
    db.commit()
    db.refresh(cycle)

    return cycle

# get my cycles (private)
@router.get("/me", response_model=list[CycleResponse])
def get_my_cycles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )

    if not history:
        return []

    cycles = (
        db.query(Cycle)
        .filter(Cycle.id_history == history.id_history)
        .all()
    )

    return cycles

# update cycle entry (private)
@router.patch("/{cycle_id}", response_model=CycleResponse)
def update_my_cycle(
    cycle_id: int,
    data: CycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Clinical history not found"
        )

    cycle = (
        db.query(Cycle)
        .filter(
            Cycle.id_cycle_entry == cycle_id,
            Cycle.id_history == history.id_history
        )
        .first()
    )

    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="Cycle not found"
        )

    for key, value in data.dict(exclude_unset=True).items():
        setattr(cycle, key, value)

    db.commit()
    db.refresh(cycle)

    return cycle

# delete cycle entry (private)
@router.delete("/{cycle_id}")
def delete_my_cycle(
    cycle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="Clinical history not found"
        )

    cycle = (
        db.query(Cycle)
        .filter(
            Cycle.id_cycle_entry == cycle_id,
            Cycle.id_history == history.id_history
        )
        .first()
    )

    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="Cycle not found"
        )

    db.delete(cycle)
    db.commit()

    return {"message": "Cycle deleted successfully"}