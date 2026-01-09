from pydantic import BaseModel
from datetime import date
from typing import Optional

class ClinicalHistoryCreate(BaseModel):
    id_user: int

    last_name: Optional[str] = None
    second_last_name: Optional[str] = None
    birthdate: Optional[date] = None
    sex_legally: Optional[str] = None
    sex_biology: Optional[str] = None

    depression_screening: Optional[bool] = None
    depression: Optional[bool] = None

    memory_screening: Optional[bool] = None
    memory_alterations: Optional[bool] = None
    dementia: Optional[bool] = None

    urinary_incontinence_screening: Optional[bool] = None
    urinary_incontinence: Optional[bool] = None

    anemia_screening: Optional[bool] = None
    obesity_screening: Optional[bool] = None
    osteoporosis_screening: Optional[bool] = None

    diabetes_mellitus: Optional[str] = None
    arterial_hypertension: Optional[bool] = None
    sustance_use: Optional[str] = None
    std: Optional[str] = None

    turner_syndrome_screening: Optional[bool] = None

    endometriosis_screening: Optional[bool] = None
    endometriosis: Optional[bool] = None

    pcos_screening: Optional[bool] = None
    pcos: Optional[bool] = None

    average_menstrual_cycle: Optional[int] = None
    average_ovulation: Optional[int] = None

    sexually_active: Optional[bool] = None
    miscarriages_abortions: Optional[int] = None

class ClinicalHistoryUpdate(ClinicalHistoryCreate):
    pass

class ClinicalHistoryResponse(ClinicalHistoryCreate):
    id_history: int
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
