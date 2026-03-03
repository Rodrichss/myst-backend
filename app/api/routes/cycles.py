from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.schemas.cycle import CycleResponse

router = APIRouter(
    prefix="/cycles",
    tags=["Cycles"]
)

# get my cycles (private)
@router.get("/me", response_model=list[CycleResponse])
def get_my_cycles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cycles = (
        db.query(Cycle)
        .join(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .all()
    )

    return cycles

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