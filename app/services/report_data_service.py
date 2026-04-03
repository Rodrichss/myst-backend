from app.models.cycle import Cycle
from app.services.clinical_history_service import get_or_create_clinical_history

from app.utils.catalogs.diabetes_catalog import DiabetesCatalog
from app.utils.catalogs.std_catalog import STDCatalog
from app.utils.catalogs.substance_catalog import SubstanceCatalog

def get_label_safe(catalog, value):
    return catalog.get_label(value) if value else "No especificado"

def get_full_clinical_report(db, user):
    history = get_or_create_clinical_history(db, user)

    cycles = db.query(Cycle).filter(
        Cycle.id_history == history.id_history
    ).order_by(Cycle.start_date.desc()).all()

    last_cycle = cycles[0] if cycles else None

    # Limpiar datos
    if history.sustance_use:
        raw_values = SubstanceCatalog.deserialize(history.sustance_use)

        substances = [
            label
            for s in raw_values
            if (label := SubstanceCatalog.get_label(s)) is not None
        ]
    else:
        substances = []

    # Mapear datos para el PDF
    mapped_data = {
        "diabetes": get_label_safe(DiabetesCatalog, history.diabetes_mellitus),
        "std": get_label_safe(STDCatalog, history.std),
        "substances": substances
    }

    return {
        "user": user,
        "history": history,
        "last_cycle": last_cycle,
        "mapped_data": mapped_data
    }