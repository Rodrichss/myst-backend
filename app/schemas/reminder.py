from pydantic import BaseModel
import datetime
from typing import Optional
from pydantic import BaseModel, model_validator

class ReminderCreate(BaseModel):
    id_contact: Optional[int] = None

    title: str
    description: Optional[str] = None

    start_date: datetime.date
    end_date: Optional[datetime.date] = None
    day_time: Optional[datetime.time] = None

    # type: False = receta, True = medicamento
    type: Optional[bool] = None
    dosage: Optional[str] = None        # relevante solo si type = True
    after_meal: Optional[bool] = None   # relevante solo si type = True

    status: Optional[int] = 0

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date no puede ser anterior a start_date")
        return self

class ReminderUpdate(BaseModel):
    id_contact: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None

    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    day_time: Optional[datetime.time] = None

    type: Optional[bool] = None
    dosage: Optional[str] = None
    after_meal: Optional[bool] = None
    status: Optional[int] = None

class ReminderResponse(BaseModel):
    id_reminder: int
    id_contact: Optional[int] = None

    title: str
    description: Optional[str] = None

    start_date: datetime.date
    end_date: Optional[datetime.date] = None
    day_time: Optional[datetime.time] = None

    type: Optional[bool] = None
    dosage: Optional[str] = None
    after_meal: Optional[bool] = None
    status: int

    class Config:
        from_attributes = True