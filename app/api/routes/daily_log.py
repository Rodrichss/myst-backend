from logging import log

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User

from app.services.clinical_history_service import get_or_create_clinical_history
from app.services.data_normalizer_service import DataNormalizerService
from app.services.cycle_stats_service import update_cycle_stats

from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog
from app.schemas.daily_log import (
    DailyLogCreate,
    DailyLogUpdate,
    DailyLogResponse
)

from datetime import date, timedelta

MAX_GAP_DAYS = 8

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

def get_cycle_for_date(db: Session, history_id: int, log_date: date):
    # fecha en ciclo existente
    return (
        db.query(Cycle).filter(
            Cycle.id_history == history_id,
            Cycle.start_date <= log_date
        ).filter(
            (Cycle.end_date == None) | (Cycle.end_date >= log_date)
        ).order_by(Cycle.start_date.desc()).first()
    )

# create daily log entry (Con comportamiento UPSERT integrado)
@router.post("/", response_model=DailyLogResponse)
def create_daily_log(
    data: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = get_or_create_clinical_history(db, current_user)

    # Convertir a dict y normalizar
    data_dict = data.dict(exclude_unset=True)
    data_dict = DataNormalizerService.normalize_daily_log(data_dict)
    log_date = data_dict.get("date")

    # 1. CLAVE DEL CAMBIO: Verificar si ya existe un log para esa fecha y ese usuario
    existing_log = (
        db.query(DailyLog)
        .join(Cycle)
        .filter(
            Cycle.id_history == history.id_history,
            DailyLog.date == log_date
        )
        .first()
    )

    # Encontrar el ciclo correspondiente para la fecha dada
    target_cycle = get_cycle_for_date(db, history.id_history, log_date)

    # Si hay sangrado y no hay ciclo activo o corresponde a un nuevo periodo → crear ciclo
    if data_dict.get("menstrual_flow", 0) > 0:
        should_create = False

        if not target_cycle:
            should_create = True
        elif target_cycle.start_date < log_date:
            # Hay ciclo activo — verificar si el log_date corresponde a un nuevo periodo
            last_flow_log = (
                db.query(DailyLog)
                .filter(
                    DailyLog.id_cycle == target_cycle.id_cycle,
                    DailyLog.menstrual_flow > 0
                )
                .order_by(DailyLog.date.desc())
                .first()
            )
            if not last_flow_log or (log_date - last_flow_log.date).days > MAX_GAP_DAYS:
                should_create = True

        if should_create:
            # Cerrar ciclo anterior si está abierto
            if target_cycle and not target_cycle.end_date:
                target_cycle.end_date = log_date - timedelta(days=1)
                if target_cycle.end_date < target_cycle.start_date:
                    target_cycle.end_date = target_cycle.start_date
                db.commit()

            next_cycle = db.query(Cycle).filter(
                Cycle.id_history == history.id_history,
                Cycle.start_date > log_date
            ).order_by(Cycle.start_date.asc()).first()

            target_cycle = Cycle(
                id_history=history.id_history,
                start_date=log_date,
                end_date=next_cycle.start_date - timedelta(days=1) if next_cycle else None
            )
            db.add(target_cycle)
            db.commit()
            db.refresh(target_cycle)
            update_cycle_stats(db, history.id_history)

    # Fallback: usar el ciclo abierto más reciente si no se determinó uno específico
    if not target_cycle:
        target_cycle = db.query(Cycle).filter(
            Cycle.id_history == history.id_history,
            Cycle.end_date == None
        ).order_by(Cycle.start_date.desc()).first()

    if not target_cycle:
        raise HTTPException(
            status_code=400,
            detail="No se encontró un ciclo para esta fecha. Registra un flujo menstrual primero."
        )

    # 2. SEGUNDA CLAVE: Si el log existe, hacemos un PATCH encubierto (UPDATE)
    if existing_log:
        # Si por alguna razón el ciclo cambió debido a la lógica de arriba, lo reasignamos
        existing_log.id_cycle = target_cycle.id_cycle

        for key, value in data_dict.items():
            # Evitamos pisar las llaves de control estructurales de la base de datos
            if key in ["id_log", "id_cycle", "date"]:
                continue

            # Replicamos tu lógica inteligente de actualización del PATCH original:
            if value is None:
                setattr(existing_log, key, None)
            else:
                setattr(existing_log, key, value)

        db.commit()
        db.refresh(existing_log)
        return existing_log

    # 3. Si NO existe el log, procedemos con el INSERT original con total seguridad
    log = DailyLog(
        **data_dict,
        id_cycle=target_cycle.id_cycle
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