from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class DailyLogBase(BaseModel):
    date: date

    weight: Optional[float] = None
    height: Optional[float] = None
    waist_circumference: Optional[float] = None

    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None

    body_temperature: Optional[float] = None
    glycemia: Optional[float] = None

    anticonceptive_use: Optional[bool] = None
    anticonceptive_type: Optional[str] = None

    sexual_penetration: Optional[bool] = None
    on_fertile_window: Optional[bool] = None

    menstrual_flow: Optional[int] = None
    vaginal_discharge: Optional[int] = None

    mood: Optional[int] = None
    anxiety: Optional[int] = None
    stress: Optional[int] = None

    sleep_time: Optional[time] = None
    exercise: Optional[str] = None
    exercise_time: Optional[time] = None
    water_consumption: Optional[float] = None
    hobbies_activities: Optional[str] = None

    cramps: Optional[int] = None
    cravings: Optional[int] = None
    symptoms: Optional[str] = None

    pregnancy_test: Optional[int] = None
    ovulation_test: Optional[int] = None

    notes: Optional[str] = None


class DailyLogCreate(DailyLogBase):
    pass


class DailyLogUpdate(BaseModel):
    # todos opcionales
    weight: Optional[float] = None
    menstrual_flow: Optional[int] = None
    mood: Optional[int] = None
    stress: Optional[int] = None
    notes: Optional[str] = None


class DailyLogResponse(DailyLogBase):
    id_log: int
    id_cycle: int

    class Config:
        from_attributes = True