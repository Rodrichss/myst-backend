from logging import log

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User

from app.services.clinical_history_service import get_or_create_clinical_history
from app.services.data_normalizer_service import DataNormalizerService

from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog
from app.schemas.daily_log import (
    DailyLogCreate,
    DailyLogUpdate,
    DailyLogResponse
)

from datetime import date

MAX_GAP_DAYS = 1

router = APIRouter(
    prefix="/daily-logs",
    tags=["Daily Logs"]
)

def get_active_cycle(db: Session, history: ClinicalHistory):
    return db.query(Cycle).filter(
        Cycle.id_history == history.id_history,
        Cycle.end_date == None
    ).first()

def get_last_bleeding_log(db: Session, cycle: Cycle):
    return (
        db.query(DailyLog)
        .filter(
            DailyLog.id_cycle == cycle.id_cycle,
            DailyLog.menstrual_flow != None,
            DailyLog.menstrual_flow > 0
        )
        .order_by(DailyLog.date.desc())
        .first()
    )

# create daily log entry
@router.post("/", response_model=DailyLogResponse)
def create_daily_log(
    data: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = get_or_create_clinical_history(db, current_user)
    active_cycle = get_active_cycle(db, history)

    # Convertir a dict y normalizar
    data_dict = data.dict(exclude_unset=True)
    data_dict = DataNormalizerService.normalize_daily_log(data_dict)

    # Si hay sangrado y no hay ciclo activo → crear ciclo
    if data_dict.get("menstrual_flow") and data_dict["menstrual_flow"] > 0:
        if not active_cycle:
            active_cycle = Cycle(
                id_history=history.id_history,
                start_date=data_dict.get("date")
            )
            db.add(active_cycle)
            db.commit()
            db.refresh(active_cycle)

        else:
            last_log = get_last_bleeding_log(db, active_cycle)

            if last_log:
                days_diff = (data_dict.get("date") - last_log.date).days

                # mismo ciclo
                if days_diff <= MAX_GAP_DAYS:
                    pass

                # nuevo ciclo
                else:
                    active_cycle.end_date = last_log.date
                    db.commit()

                    new_cycle = Cycle(
                        id_history=history.id_history,
                        start_date=data_dict.get("date")
                    )
                    db.add(new_cycle)
                    db.commit()
                    db.refresh(new_cycle)
                    active_cycle = new_cycle

            else:
                # no sangrado es ciclo actual
                pass

    if not active_cycle:
        raise HTTPException(
            status_code=400,
            detail="No active cycle found. Register menstrual flow first."
        )

    # Crear log diario
    log = DailyLog(
        **data_dict,
        id_cycle=active_cycle.id_cycle
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

# get my logs
@router.get("/me", response_model=list[DailyLogResponse])
def get_my_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = (
        db.query(DailyLog)
        .join(Cycle)
        .join(ClinicalHistory)
        .filter(ClinicalHistory.id_user == current_user.id_user)
        .all()
    )

    return logs

# update daily log entry
@router.patch("/{log_id}", response_model=DailyLogResponse)
def update_log(
    log_id: int,
    data: DailyLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = (
        db.query(DailyLog)
        .join(Cycle)
        .join(ClinicalHistory)
        .filter(
            DailyLog.id_log == log_id,
            ClinicalHistory.id_user == current_user.id_user
        )
        .first()
    )

    if not log:
        raise HTTPException(404, "Log not found")

    # solo campos enviados
    original_data = data.dict(exclude_unset=True)
    normalized_data = DataNormalizerService.normalize_daily_log(original_data.copy())

    for key in original_data:
        original_value = original_data.get(key)
        normalized_value = normalized_data.get(key)

        # usuario quiere borrar explícitamente
        if original_value is None:
            setattr(log, key, None)

        # valor válido → guardar normalizado
        elif normalized_value is not None:
            setattr(log, key, normalized_value)

        # valor inválido → NO TOCAR (se ignora)
        else:
            pass

    db.commit()
    db.refresh(log)

    return log

# delete daily log entry
@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = (
        db.query(DailyLog)
        .join(Cycle)
        .join(ClinicalHistory)
        .filter(
            DailyLog.id_log == log_id,
            ClinicalHistory.id_user == current_user.id_user
        )
        .first()
    )

    if not log:
        raise HTTPException(404, "Log not found")

    db.delete(log)
    db.commit()

    return {"message": "Log deleted successfully"}