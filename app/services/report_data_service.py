from app.models.cycle import Cycle
from app.services.clinical_history_service import get_or_create_clinical_history

def get_full_clinical_report(db, user):
    history = get_or_create_clinical_history(db, user)

    cycles = db.query(Cycle).filter(
        Cycle.id_history == history.id_history
    ).order_by(Cycle.start_date.desc()).all()

    last_cycle = cycles[0] if cycles else None

    return {
        "user": user,
        "history": history,
        "cycles": cycles,
        "last_cycle": last_cycle
    }
