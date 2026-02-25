from pydantic import BaseModel
import datetime
from typing import Optional

class ReminderCreate(BaseModel):
    id_contact: Optional[int] = None

    title: str
    description: Optional[str] = None

    date: datetime.date
    time: datetime.time

    repeats: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None

class ReminderUpdate(BaseModel):
    id_contact: Optional[int] = None

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
    title: str
    description: Optional[str]

    date: datetime.date
    time: datetime.time

    repeats: Optional[str]
    type: Optional[str]
    priority: Optional[str]

    id_user: int
    id_contact: Optional[int]

    is_completed: bool

    class Config:
        from_attributes = True