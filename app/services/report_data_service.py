from app.models.cycle import Cycle
from app.services.clinical_history_service import get_or_create_clinical_history

# Clinical data mapping
from app.catalogs.diabetes_catalog import DiabetesCatalog
from app.catalogs.sex_catalog import SexBiologyCatalog, SexLegallyCatalog
from app.catalogs.std_catalog import STDCatalog
from app.catalogs.substance_catalog import SubstanceCatalog

# Cycle data mapping
from app.catalogs.activity_catalog import ActivityCatalog
from app.catalogs.contraception_catalog import ContraceptionCatalog
from app.catalogs.exercise_catalog import ExerciseCatalog
from app.catalogs.symptoms_catalog import SymptomsCatalog

from app.catalogs.cravings_enum import CravingsEnum
from app.catalogs.discharge_enum import DischargeEnum
from app.catalogs.flow_enum import FlowEnum
from app.catalogs.mood_enum import MoodEnum
from app.catalogs.scale_enum import ScaleEnum
from app.catalogs.test_enum import TestEnum

from app.catalogs.water_helper import WaterHelper

# -------------------------
# HELPERS
# -------------------------
def split_values(value: str | None):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

def get_label_safe(catalog, value):
    if value is None:
        return "No especificado"

    # ENUM (int)
    if isinstance(value, int):
        return catalog.MAP.get(value, "No especificado")

    # CATALOG (string)
    values = split_values(value)

    if len(values) > 1:
        labels = [
            catalog.MAP.get(v)
            for v in values
            if catalog.MAP.get(v)
        ]
        return ", ".join(labels) if labels else "No especificado"

    return catalog.MAP.get(values[0], "No especificado")

def map_catalog_list(catalog, value):
    values = split_values(value)

    return [
        catalog.MAP.get(v)
        for v in values
        if catalog.MAP.get(v)
    ]

def build_cycle_report(user, history, cycle):
    return {
        "user": user,
        "history": history,
        "cycle": cycle,
        "mapped_cycle": map_cycle(cycle),
        "mapped_data": map_clinical_history(history)
    }

# -------------------------
# MAPPING
# -------------------------
def map_daily_log(log):
    return {
        "date": log.date,

        "weight": log.weight,
        "height": log.height,
        "waist_circumference": log.waist_circumference,

        "systolic_bp": log.systolic_bp,
        "diastolic_bp": log.diastolic_bp,
        "heart_rate": log.heart_rate,

        "body_temperature": log.body_temperature,
        "glycemia": log.glycemia,

        "anticonceptive_use": log.anticonceptive_use,
        "anticonceptive_type": get_label_safe(ContraceptionCatalog, log.anticonceptive_type),

        "sexual_penetration": log.sexual_penetration,
        "on_fertile_window": log.on_fertile_window,

        "menstrual_flow": get_label_safe(FlowEnum, log.menstrual_flow),
        "vaginal_discharge": get_label_safe(DischargeEnum, log.vaginal_discharge),

        "mood": get_label_safe(MoodEnum, log.mood),
        "anxiety": get_label_safe(ScaleEnum, log.anxiety),
        "stress": get_label_safe(ScaleEnum, log.stress),

        "sleep_time": log.sleep_time,
        "exercise": map_catalog_list(ExerciseCatalog, log.exercise),
        "exercise_time": log.exercise_time,

        "water_consumption": WaterHelper.to_label(log.water_consumption),

        "hobbies_activities": map_catalog_list(ActivityCatalog, log.hobbies_activities),

        "cramps": get_label_safe(ScaleEnum, log.cramps),
        "cravings": get_label_safe(CravingsEnum, log.cravings),
        "symptoms": map_catalog_list(SymptomsCatalog, log.symptoms),

        "pregnancy_test": get_label_safe(TestEnum, log.pregnancy_test),
        "ovulation_test": get_label_safe(TestEnum, log.ovulation_test),

        "notes": log.notes
    }

def map_cycle(cycle):
    if not cycle:
        return None

    logs = sorted(cycle.daily_logs, key=lambda x: x.date) if cycle.daily_logs else []

    return {
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "logs": [map_daily_log(log) for log in logs]
    }

def map_clinical_history(history):
    return {
        "sex_biology": get_label_safe(SexBiologyCatalog, history.sex_biology),
        "sex_legally": get_label_safe(SexLegallyCatalog, history.sex_legally),
        "diabetes": get_label_safe(DiabetesCatalog, history.diabetes_mellitus),
        "std": map_catalog_list(STDCatalog, history.std),
        "substances": map_catalog_list(SubstanceCatalog, history.sustance_use)
    }

# -------------------------
# SERVICEs
# -------------------------
def get_full_clinical_report(db, user):
    history = get_or_create_clinical_history(db, user)

    last_cycle = db.query(Cycle).filter(
        Cycle.id_history == history.id_history
    ).order_by(Cycle.start_date.desc()).first()

    report = build_cycle_report(user, history, last_cycle)
    report["last_cycle"] = last_cycle

    return report

def get_cycle_report_by_id(db, user, cycle_id: int):
    history = get_or_create_clinical_history(db, user)

    cycle = db.query(Cycle).filter(
        Cycle.id_cycle == cycle_id,
        Cycle.id_history == history.id_history
    ).first()

    if not cycle:
        return None

    return build_cycle_report(user, history, cycle)