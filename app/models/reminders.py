from sqlalchemy import Column, Integer, Time, Boolean, Date, ForeignKey, String
from app.db.base import Base

class Reminder(Base):
    __tablename__ = "reminder"

    id_reminder = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("user.id_user"))
    id_contact = Column(Integer, ForeignKey("contact.id_contact"))

    title = Column(String(100))
    description = Column(String(255))
    date = Column(Date)
    time  = Column(Time)
    repeats = Column(String(50))  # e.g., "daily", "weekly", "monthly"
    type = Column(String(50))     # e.g., "medication", "appointment"
    priority = Column(String(20)) # e.g., "low", "medium", "high"
    is_completed = Column(Boolean, default=False)
