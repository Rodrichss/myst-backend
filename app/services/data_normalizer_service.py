from app.utils.mapper import map_to_catalog, map_to_enum

# Catalogos
from app.catalogs.activity_catalog import ActivityCatalog
from app.catalogs.contraception_catalog import ContraceptionCatalog
from app.catalogs.cravings_enum import CravingsEnum
from app.catalogs.diabetes_catalog import DiabetesCatalog
from app.catalogs.discharge_enum import DischargeEnum
from app.catalogs.exercise_catalog import ExerciseCatalog
#from app.catalogs.medication_catalog import MedicationCatalog
from app.catalogs.sex_catalog import SexBiologyCatalog, SexLegallyCatalog
from app.catalogs.std_catalog import STDCatalog
from app.catalogs.substance_catalog import SubstanceCatalog
from app.catalogs.symptoms_catalog import SymptomsCatalog

# Enums
from app.catalogs.flow_enum import FlowEnum
from app.catalogs.mood_enum import MoodEnum
from app.catalogs.scale_enum import ScaleEnum
from app.catalogs.test_enum import TestEnum

class DataNormalizerService:
    @staticmethod
    def normalize_daily_log(data: dict) -> dict:
        if not data:
            return data

        # -- catálogos --
        if "anticonceptive_type" in data:
            data["anticonceptive_type"] = map_to_catalog(
                data["anticonceptive_type"],
                ContraceptionCatalog
            )

        if "exercise" in data:
            data["exercise"] = map_to_catalog(
                data["exercise"],
                ExerciseCatalog,
                multiple=True
            )

        if "hobbies_activities" in data:
            data["hobbies_activities"] = map_to_catalog(
                data["hobbies_activities"],
                ActivityCatalog,
                multiple=True
            )

        if "symptoms" in data:
            data["symptoms"] = map_to_catalog(
                data["symptoms"],
                SymptomsCatalog,
                multiple=True
            )

        # -- enums --
        if "cravings" in data:
            data["cravings"] = map_to_enum(data["cravings"], CravingsEnum)

        if "mood" in data:
            data["mood"] = map_to_enum(data["mood"], MoodEnum)

        if "menstrual_flow" in data:
            data["menstrual_flow"] = map_to_enum(data["menstrual_flow"], FlowEnum)

        if "vaginal_discharge" in data:
            data["vaginal_discharge"] = map_to_enum(
                data["vaginal_discharge"],
                DischargeEnum
            )

        if "anxiety" in data:
            data["anxiety"] = map_to_enum(data["anxiety"], ScaleEnum)

        if "stress" in data:
            data["stress"] = map_to_enum(data["stress"], ScaleEnum)

        if "cramps" in data:
            data["cramps"] = map_to_enum(data["cramps"], ScaleEnum)

        if "pregnancy_test" in data:
            data["pregnancy_test"] = map_to_enum(data["pregnancy_test"], TestEnum)

        if "ovulation_test" in data:
            data["ovulation_test"] = map_to_enum(data["ovulation_test"], TestEnum)

        return data

    @staticmethod
    def normalize_clinical_history(data: dict) -> dict:
        if not data:
            return data

        # -- catálogos --
        if "sex_biology" in data:
            data["sex_biology"] = map_to_catalog(
                data["sex_biology"],
                SexBiologyCatalog
            )

        if "sex_legally" in data:
            data["sex_legally"] = map_to_catalog(
                data["sex_legally"],
                SexLegallyCatalog
            )

        if "diabetes_mellitus" in data:
            data["diabetes_mellitus"] = map_to_catalog(
                data["diabetes_mellitus"],
                DiabetesCatalog
            )

        if "std" in data:
            data["std"] = map_to_catalog(
                data["std"],
                STDCatalog,
                multiple=True
            )

        if "sustance_use" in data:
            data["sustance_use"] = map_to_catalog(
                data["sustance_use"],
                SubstanceCatalog,
                multiple=True
            )

        return data