from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, Literal

class ClinicalHistoryCreate(BaseModel):
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
    sustance_use: Optional[str | list[str]] = None
    std: Optional[str | list[str]] = None

    turner_syndrome_screening: Optional[bool] = None

    endometriosis_screening: Optional[bool] = None
    endometriosis: Optional[bool] = None

    pcos_screening: Optional[bool] = None
    pcos: Optional[bool] = None

    # No se exponen en Create/Update — son calculados automáticamente
    # average_menstrual_cycle, average_ovulation, last_period_date, regularity

    sexually_active: Optional[bool] = None
    miscarriages_abortions: Optional[int] = Field(default=None, ge=0, le=20)

class ClinicalHistoryUpdate(ClinicalHistoryCreate):
    pass

class ClinicalHistoryResponse(ClinicalHistoryCreate):
    id_history: int

    # Campos calculados — solo lectura
    average_menstrual_cycle: Optional[int] = None
    average_ovulation: Optional[int] = None
    last_period_date: Optional[date] = None
    regularity: Optional[Literal["regular", "irregular"]] = None

    class Config:
        from_attributes = True
