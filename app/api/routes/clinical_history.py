from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.schemas.clinical_history import (
    ClinicalHistoryCreate,
    ClinicalHistoryUpdate,
    ClinicalHistoryResponse
)

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

    history = ClinicalHistory(
        **data.dict(), 
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

    for key, value in data.dict(exclude_unset=True).items():
        setattr(history, key, value)

    db.commit()
    db.refresh(history)
    return history