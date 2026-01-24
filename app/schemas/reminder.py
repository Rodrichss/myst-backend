from pydantic import BaseModel
import datetime
from typing import Optional

class ReminderCreate(BaseModel):
    id_user: int
    id_contact: Optional[int] = None

    title: str
    description: Optional[str] = None

    date: datetime.date
    time: datetime.time

    repeats: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None

    repeats: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None

    is_completed: Optional[bool] = None

class ReminderResponse(ReminderCreate):
    id_reminder: int
    is_completed: bool

    class Config:
        from_attributes = True