from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.clinical_history import ClinicalHistory
from app.models.user import User
from app.schemas.clinical_history import (
    ClinicalHistoryCreate,
    ClinicalHistoryUpdate,
    ClinicalHistoryResponse
)

router = APIRouter(
    prefix="/clinical-history",
    tags=["Clinical History"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ClinicalHistoryResponse)
def create_clinical_history(
    data: ClinicalHistoryCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = ClinicalHistory(**data.dict())
    db.add(history)
    db.commit()
    db.refresh(history)

    response = ClinicalHistoryResponse.from_orm(history)
    response.user_name = history.user.name

    return response

@router.get("/user/{id_user}", response_model=ClinicalHistoryResponse)
def get_history_by_user(
    id_user: int,
    db: Session = Depends(get_db)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == id_user)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Clinical history not found")

    response = ClinicalHistoryResponse.from_orm(history)
    response.user_name = history.user.name

    return response

@router.patch("/{id_history}", response_model=ClinicalHistoryResponse)
def update_clinical_history(
    id_history: int,
    data: ClinicalHistoryUpdate,
    db: Session = Depends(get_db)
):
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_history == id_history)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Clinical history not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(history, key, value)

    db.commit()
    db.refresh(history)

    response = ClinicalHistoryResponse.from_orm(history)
    response.user_name = history.user.name

    return response