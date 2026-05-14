from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog

from app.schemas.assistant import ChatMessage
from app.services.ai_service import analyze_daily_message
from datetime import date, datetime, timedelta
from app.services.cycle_stats_service import update_cycle_stats

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"]
)

def _parse_date(raw: str) -> date:
    """Convierte string ISO a date y rechaza fechas futuras."""
    parsed = datetime.fromisoformat(raw).date()
    today = date.today()
    if parsed > today:
        # El modelo devolvió una fecha futura: retroceder un año
        parsed = parsed.replace(year=parsed.year - 1)
    return parsed


def _get_or_create_history(db: Session, user_id: int) -> ClinicalHistory:
    history = db.query(ClinicalHistory).filter(
        ClinicalHistory.id_user == user_id
    ).first()
    if not history:
        history = ClinicalHistory(id_user=user_id)
        db.add(history)
        db.commit()
        db.refresh(history)
    return history

@router.post("/log-day")
def log_day_from_chat(
    data: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    extracted = analyze_daily_message(data.message)

    if "error" in extracted:
        raise HTTPException(status_code=400, detail=extracted["error"])

    # Normalizar keys a minúsculas por si el modelo las devuelve en mayúsculas
    extracted = {k.lower(): v for k, v in extracted.items()}

    # ── Parsear fecha ──────────────────────────────────────────────────────────
    raw_date = extracted.get("date")
    event_date: date = _parse_date(raw_date) if raw_date else date.today()

    intent = extracted.get("intent", "log_symptoms")
    history = _get_or_create_history(db, current_user.id_user)

    cycle = None

    # ── Manejar intents de ciclo ───────────────────────────────────────────────
    if intent == "start_period":
        # Verificar que no exista ya un ciclo que cubra esta fecha
        overlapping = db.query(Cycle).filter(
            Cycle.id_history == history.id_history,
            Cycle.start_date <= event_date,
            (Cycle.end_date == None) | (Cycle.end_date >= event_date)
        ).first()

        if overlapping:
            intent = "log_symptoms"
            cycle = overlapping

        # Cerrar el ciclo abierto más reciente si lo hay (sin end_date)
        else:
            open_cycle = (
                db.query(Cycle)
                .filter(
                    Cycle.id_history == history.id_history,
                    Cycle.end_date == None,
                    Cycle.start_date < event_date
                )
                .order_by(Cycle.start_date.desc())
                .first()
            )
            if open_cycle:
                open_cycle.end_date = event_date - timedelta(days=1)
                # Sanity check: end_date no puede ser anterior a start_date
                if open_cycle.end_date < open_cycle.start_date:
                    open_cycle.end_date = open_cycle.start_date
                db.commit()

            new_cycle = Cycle(
                id_history=history.id_history,
                start_date=event_date,
            )
            db.add(new_cycle)
            db.commit()
            db.refresh(new_cycle)
            update_cycle_stats(db, history.id_history)
            cycle = new_cycle

    elif intent == "end_period":
        # Buscar el ciclo abierto más reciente
        open_cycle = (
            db.query(Cycle)
            .filter(
                Cycle.id_history == history.id_history,
                Cycle.end_date == None,
                Cycle.start_date <= event_date
            )
            .order_by(Cycle.start_date.desc())
            .first()
        )

        if not open_cycle:
            raise HTTPException(
                status_code=400,
                detail="No hay un ciclo abierto para cerrar en esa fecha."
            )

        # Validar coherencia de fechas
        if event_date < open_cycle.start_date:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"La fecha de fin ({event_date}) es anterior al inicio del ciclo "
                    f"({open_cycle.start_date}). Verifica la fecha."
                )
            )

        open_cycle.end_date = event_date
        db.commit()
        db.refresh(open_cycle)
        update_cycle_stats(db, history.id_history)
        cycle = open_cycle

    else:  # log_symptoms
        # Buscar el ciclo que contenga la fecha del log
        cycle = (
            db.query(Cycle)
            .filter(
                Cycle.id_history == history.id_history,
                Cycle.start_date <= event_date,
                (Cycle.end_date == None) | (Cycle.end_date >= event_date)
            )
            .first()
        )

        if not cycle:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"No se encontró un ciclo activo para la fecha {event_date}. "
                    "Registra primero el inicio de tu periodo."
                )
            )

    # ── Crear el daily log ─────────────────────────────────────────────────────
    # 1. Buscamos si ya existe un log para ese ciclo y esa fecha
    existing_log = db.query(DailyLog).filter(
        DailyLog.id_cycle == cycle.id_cycle,
        DailyLog.date == event_date
    ).first()

    valid_columns = set(DailyLog.__table__.columns.keys()) - {"id_log", "id_cycle", "date"}

    log_data = {
        key: value
        for key, value in extracted.items()
        if key in valid_columns
    }

    # symptoms en el modelo es String; si Gemini devuelve lista, unirla
    if "symptoms" in log_data and isinstance(log_data["symptoms"], list):
        log_data["symptoms"] = ", ".join(log_data["symptoms"])

    # Si el intent fue start_period (original o degradado),
    # garantizar al menos flujo ligero
    if extracted.get("intent") == "start_period" and "menstrual_flow" not in log_data:
        log_data["menstrual_flow"] = 1

    if existing_log:
        # 2. Si existe, lo actualizamos con los nuevos datos de Gemini
        for key, value in log_data.items():
            setattr(existing_log, key, value)
        status_msg = "Registro actualizado correctamente"
        db.commit()
        db.refresh(existing_log)
    else:
        # 3. Si no existe, lo creamos
        new_log = DailyLog(
            id_cycle=cycle.id_cycle,
            date=event_date,
            **log_data
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        status_msg = "Registro guardado correctamente"

    return {
    "message": status_msg,
    "intent": intent,
    "date": event_date.isoformat(),
    "cycle_id": cycle.id_cycle,
    "data_extracted": extracted, # 'extracted' ya tiene response e is_red_flag
}