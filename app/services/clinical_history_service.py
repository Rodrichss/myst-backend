from sqlalchemy.orm import Session

from app.models.user import User
from app.models.clinical_history import ClinicalHistory

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