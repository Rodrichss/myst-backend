from app.models.clinical_history import ClinicalHistory

def get_or_create_clinical_history(db, user):
    history = db.query(ClinicalHistory).filter(
        ClinicalHistory.id_user == user.id_user
    ).first()

    if not history:
        history = ClinicalHistory(id_user=user.id_user)
        db.add(history)
        db.commit()
        db.refresh(history)

    return history