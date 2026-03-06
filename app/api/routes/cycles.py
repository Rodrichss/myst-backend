from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import numpy as np
from app.core.ml import cycle_predictor

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

#predict cycle (private)
@router.get("/predict/me")
def predict_my_next_cycle(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Obtener historial clínico
    history = (
        db.query(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Clinical history not found")

    # Obtener ciclos ordenados
    cycles = (
        db.query(Cycle)
        .filter(Cycle.id_history == history.id_history)
        .order_by(Cycle.start_date)
        .all()
    )

    if len(cycles) < 4:
        raise HTTPException(
            status_code=400,
            detail="Not enough cycle data to generate prediction"
        )

    # Extraer fechas
    start_dates = [cycle.start_date for cycle in cycles]

    # Calcular longitudes
    cycle_lengths = [
        (start_dates[i] - start_dates[i-1]).days
        for i in range(1, len(start_dates))
    ]

    # Features
    last_cycle = cycle_lengths[-1]
    rolling_mean = np.mean(cycle_lengths[-3:])
    rolling_std = np.std(cycle_lengths[-3:])

    predicted_length = cycle_predictor.predict_length(
        last_cycle,
        rolling_mean,
        rolling_std
    )

    predicted_date = start_dates[-1] + timedelta(days=int(predicted_length))

    return {
        "predicted_cycle_length": predicted_length,
        "predicted_next_period": predicted_date
    }