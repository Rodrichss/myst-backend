from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.schemas.clinical_history import (
    ClinicalHistoryCreate,
    ClinicalHistoryUpdate,
    ClinicalHistoryResponse
)
from app.services.data_normalizer_service import DataNormalizerService
from app.services.cycle_stats_service import update_cycle_stats

router = APIRouter(
    prefix="/clinical-history",
    tags=["Clinical History"]
)

# Create clinical history (private)
@router.post("/", response_model=ClinicalHistoryResponse)
def create_clinical_history(
    data: ClinicalHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Clinical history already exists for this user"
        )

    # normalizar
    data_dict = data.dict(exclude_unset=True)
    data_dict = DataNormalizerService.normalize_clinical_history(data_dict)

    history = ClinicalHistory(
        **data_dict,
        id_user=current_user.id_user
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history

# Get my clinical history (private)
@router.get("/me", response_model=ClinicalHistoryResponse)
def get_my_clinical_history(
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

    return history

# Update my clinical history (private)
@router.patch("/me", response_model=ClinicalHistoryResponse)
def update_my_clinical_history(
    data: ClinicalHistoryUpdate,
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

    update_data = data.model_dump(exclude_unset=True)
    normalized_data = DataNormalizerService.normalize_clinical_history(update_data)

    for key, value in normalized_data.items():
        setattr(history, key, value)

    try:
        db.commit()
        db.refresh(history)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating database")

    return history

@router.post("/me/backfill-stats") # temporal for testing
def backfill_cycle_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(ClinicalHistory).filter(
        ClinicalHistory.id_user == current_user.id_user
    ).first()
    if not history:
        raise HTTPException(status_code=404, detail="Clinical history not found")
    
    update_cycle_stats(db, history.id_history)
    return {"message": "Stats updated successfully"}