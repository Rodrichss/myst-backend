from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class CycleCreate(BaseModel):
    id_history: int

    # Datos físicos
    weight: Optional[float] = None
    height: Optional[float] = None
    waist_circumference: Optional[float] = None
    body_temperature: Optional[float] = None
    glycemia: Optional[int] = None

    # Estado emocional
    mood: Optional[int] = None
    anxiety: Optional[int] = None
    stress: Optional[int] = None

    # Síntomas
    cramps: Optional[int] = None
    cravings: Optional[int] = None
    symptoms: Optional[str] = None

    # Actividad y hábitos
    sleep_time: Optional[time] = None
    exercise: Optional[str] = None
    exercise_time: Optional[time] = None
    water_consumption: Optional[float] = None
    hobbies_activities: Optional[str] = None

    # Sexualidad y anticonceptivos
    anticonceptive_use: Optional[bool] = None
    anticonceptive_type: Optional[str] = None
    sexual_penetration: Optional[bool] = None
    on_fertile_day: Optional[bool] = None

    # Pruebas
    pregnancy_test: Optional[int] = None
    ovulation_test: Optional[int] = None

    # Periodo
    menstrual_period: Optional[int] = None
    period_start_date: Optional[date] = None
    period_end_date: Optional[date] = None

    # Notas
    notes: Optional[str] = None

    class Config:
        orm_mode = True