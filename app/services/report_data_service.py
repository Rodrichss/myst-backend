from app.models.cycle import Cycle
from app.services.clinical_history_service import get_or_create_clinical_history

from app.catalogs.diabetes_catalog import DiabetesCatalog
from app.catalogs.sex_catalog import SexBiologyCatalog, SexLegallyCatalog
from app.catalogs.std_catalog import STDCatalog
from app.catalogs.substance_catalog import SubstanceCatalog

def split_values(value: str | None):
    if not value:
        return []

    return [v.strip() for v in value.split(",") if v.strip()]

def get_label_safe(catalog, value):
    if not value:
        return "No especificado"

    values = split_values(value)

    # múltiples
    if len(values) > 1:
        labels = [
            catalog.MAP.get(v)
            for v in values
            if catalog.MAP.get(v)
        ]
        return ", ".join(labels) if labels else "No especificado"

    # único
    return catalog.MAP.get(values[0], "No especificado")

def map_catalog_list(catalog, value):
    values = split_values(value)

    return [
        catalog.MAP.get(v)
        for v in values
        if catalog.MAP.get(v)
    ]

def get_full_clinical_report(db, user):
    history = get_or_create_clinical_history(db, user)

    cycles = db.query(Cycle).filter(
        Cycle.id_history == history.id_history
    ).order_by(Cycle.start_date.desc()).all()

    last_cycle = cycles[0] if cycles else None

    mapped_data = {
        "sex_biology": get_label_safe(SexBiologyCatalog, history.sex_biology),
        "sex_legally": get_label_safe(SexLegallyCatalog, history.sex_legally),
        "diabetes": get_label_safe(DiabetesCatalog, history.diabetes_mellitus),
        "std": map_catalog_list(STDCatalog, history.std),
        "substances": map_catalog_list(SubstanceCatalog, history.sustance_use)
    }

    return {
        "user": user,
        "history": history,
        "last_cycle": last_cycle,
        "mapped_data": mapped_data
    }