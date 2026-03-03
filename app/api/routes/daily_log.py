from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog
from app.schemas.daily_log import (
    DailyLogCreate,
    DailyLogUpdate,
    DailyLogResponse
)
from datetime import date

router = APIRouter(
    prefix="/daily-logs",
    tags=["Daily Logs"]
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

def get_active_cycle(db: Session, history: ClinicalHistory):
    return db.query(Cycle).filter(
        Cycle.id_history == history.id_history,
        Cycle.end_date == None
    ).first()

# create daily log entry (private)
@router.post("/", response_model=DailyLogResponse)
def create_daily_log(
    data: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = get_or_create_clinical_history(db, current_user)
    active_cycle = get_active_cycle(db, history)

    # Si hay sangrado y no hay ciclo activo → crear ciclo
    if data.menstrual_flow and data.menstrual_flow > 0:

        if not active_cycle:
            active_cycle = Cycle(
                id_history=history.id_history,
                start_date=data.date
            )
            db.add(active_cycle)
            db.commit()
            db.refresh(active_cycle)

        # Si ya había ciclo activo pero nuevo sangrado → cerrar anterior
        elif active_cycle.start_date != data.date:
            active_cycle.end_date = data.date
            db.commit()

            new_cycle = Cycle(
                id_history=history.id_history,
                start_date=data.date
            )
            db.add(new_cycle)
            db.commit()
            db.refresh(new_cycle)
            active_cycle = new_cycle

    if not active_cycle:
        raise HTTPException(
            status_code=400,
            detail="No active cycle found. Register menstrual flow first."
        )

    log = DailyLog(
        **data.dict(),
        id_cycle=active_cycle.id_cycle
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log

# get my daily logs (private)
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

# update daily log entry (private)
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

    for key, value in data.dict(exclude_unset=True).items():
        setattr(log, key, value)

    db.commit()
    db.refresh(log)

    return log

# delete daily log entry (private)
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