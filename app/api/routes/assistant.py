from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.clinical_history import ClinicalHistory
from app.models.cycle import Cycle
from app.models.daily_log import DailyLog

from app.schemas.assistant import ChatMessage
from app.services.ai_service import analyze_daily_message
from datetime import date

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"]
)

@router.post("/log-day")
def log_day_from_chat(
    data: ChatMessage,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    extracted = analyze_daily_message(data.message)

    if "error" in extracted:
        raise HTTPException(
            status_code = 400,
            detail = extracted["error"]
        )

    history = db.query(ClinicalHistory).filter(
        ClinicalHistory.id_user == current_user.id_user
    ).first()

    if not history:
        history = ClinicalHistory(id_user=current_user.id_user)
        db.add(history)
        db.commit()
        db.refresh(history)

    cycle = db.query(Cycle).filter(
        Cycle.id_history == history.id_history,
        Cycle.end_date == None
    ).first()

    if not cycle:
        cycle = Cycle(id_history=history.id_history, start_date=date.today())
        db.add(cycle)
        db.commit()
        db.refresh(cycle)

    valid_fields = DailyLog.__table__.columns.keys()
    filtered_data = {
        key: value
        for key, value in extracted.items()
        if key in valid_fields
    }

    log = DailyLog(
        id_cycle=cycle.id_cycle,
        date=date.today(),
        **filtered_data
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return {
        "message": "Daily log registered successfully",
        "data_extracted": extracted
    }