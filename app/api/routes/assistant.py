from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import pytz

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog

from app.schemas.assistant import ChatMessage
from app.services.ai_service import analyze_daily_message
from datetime import date, datetime, timedelta
from app.services.cycle_stats_service import update_cycle_stats, recalculate_cycle_end_dates

MAX_GAP_DAYS = 8

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"]
)

MEXICO_TZ = pytz.timezone("America/Mexico_City")

def _today_local() -> date:
    """Devuelve la fecha de hoy en hora de México, no UTC."""
    return datetime.now(MEXICO_TZ).date()


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


def _merge_symptoms(existing: str | None, new: str | None) -> str | None:
    """Combina síntomas existentes con nuevos, sin duplicados."""
    existing_set = set(s.strip() for s in existing.split(",") if s.strip()) if existing else set()
    new_set = set(s.strip() for s in new.split(",") if s.strip()) if new else set()
    merged = existing_set | new_set
    return ", ".join(sorted(merged)) if merged else None


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
    event_date: date = _parse_date(raw_date) if raw_date else _today_local()

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
        
        # Solo degradar a log_symptoms si el ciclo activo es reciente
        # (el event_date cae dentro de MAX_GAP_DAYS desde el último log con flujo)
        should_degrade = False
        if overlapping:
            last_flow_log = (
                db.query(DailyLog)
                .join(Cycle)
                .filter(
                    Cycle.id_history == history.id_history,
                    DailyLog.menstrual_flow > 0,
                    DailyLog.date <= event_date
                )
                .order_by(DailyLog.date.desc())
                .first()
            )
            if last_flow_log and (event_date - last_flow_log.date).days <= MAX_GAP_DAYS:
                should_degrade = True

        if should_degrade:
            intent = "log_symptoms"
            cycle = overlapping
        # Cerrar el ciclo abierto más reciente si lo hay (sin end_date)
        else:
            # Verificar que no exista ya un ciclo con ese start_date exacto
            existing_cycle = db.query(Cycle).filter(
                Cycle.id_history == history.id_history,
                Cycle.start_date == event_date
            ).first()
 
            if not existing_cycle:
                new_cycle = Cycle(
                    id_history=history.id_history,
                    start_date=event_date,
                )
                db.add(new_cycle)
                db.commit()
                db.refresh(new_cycle)
                # Recalcular todos los end_dates para manejar inserciones fuera de orden
                recalculate_cycle_end_dates(db, history.id_history)

                # Reasignar logs del mismo día que quedaron en el ciclo anterior
                orphan_log = db.query(DailyLog).filter(
                    DailyLog.date == event_date,
                    DailyLog.id_cycle != new_cycle.id_cycle
                ).join(Cycle).filter(
                    Cycle.id_history == history.id_history
                ).first()

                if orphan_log:
                    orphan_log.id_cycle = new_cycle.id_cycle
                    db.commit()
                    db.refresh(orphan_log)

                update_cycle_stats(db, history.id_history)
                cycle = new_cycle
            else:
                cycle = existing_cycle


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

    # Preparar datos del log

    valid_columns = set(DailyLog.__table__.columns.keys()) - {"id_log", "id_cycle", "date"}

    log_data = {
        key: value
        for key, value in extracted.items()
        if key in valid_columns
    }

    # symptoms en el modelo es String; si Gemini devuelve lista, unirla
    if "symptoms" in log_data:
        s = log_data["symptoms"]
        if isinstance(s, list):
            log_data["symptoms"] = ", ".join(s)
        elif isinstance(s, dict):
            # Gemini devolvió {"back_pain": true, "headache": false}
            # Solo incluir los que son True
            log_data["symptoms"] = ", ".join(k for k, v in s.items() if v)
        elif not isinstance(s, str):
            log_data["symptoms"] = str(s)

    # Detectar síntomas devueltos como campos booleanos sueltos
    VALID_SYMPTOMS = {
        "headache", "sore_throat", "muscle_aches", "back_pain",
        "shortness_of_breath", "fatigue", "insomnia", "fever",
        "cough", "bloating", "diarrhea", "constipation",
        "loss_of_taste_or_smell", "nausea_or_vomiting"
    }

    loose_symptoms = [
        key for key, value in extracted.items()
        if key in VALID_SYMPTOMS and value is True
    ]

    if loose_symptoms:
        existing_symptoms = log_data.get("symptoms", "")
        merged = _merge_symptoms(
            existing_symptoms if isinstance(existing_symptoms, str) else None,
            ", ".join(loose_symptoms)
        )
        log_data["symptoms"] = merged

    # Si el intent fue start_period (original o degradado),
    # garantizar al menos flujo ligero
    if extracted.get("intent") == "start_period" and "menstrual_flow" not in log_data:
        log_data["menstrual_flow"] = 1

    # Crear o actualizar el daily log
    existing_log = db.query(DailyLog).filter(
        DailyLog.id_cycle == cycle.id_cycle,
        DailyLog.date == event_date
    ).first()


    if existing_log:
        for key, value in log_data.items():
            if key == "symptoms":
                merged = _merge_symptoms(existing_log.symptoms, value)
                setattr(existing_log, "symptoms", merged)
            else:
                setattr(existing_log, key, value)
        db.commit()
        db.refresh(existing_log)
        status_msg = "Registro actualizado correctamente"

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