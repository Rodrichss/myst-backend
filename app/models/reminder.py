from sqlalchemy import Column, Integer, Time, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Reminder(Base):
    __tablename__ = "reminder"

    id_reminder = Column(Integer, primary_key=True, index=True)

    id_user = Column(Integer, ForeignKey("users.id_user"))
    id_contact = Column(Integer, ForeignKey("contact.id_contact"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reminders")
    contact = relationship("Contact", back_populates="reminders")

    title = Column(String(100))
    description = Column(String(255), nullable=True)

    date = Column(Date)
    time = Column(Time)

    repeats = Column(String(50), nullable=True)      # daily, weekly, monthly
    type = Column(String(50), nullable=True)         # medication, appointment
    priority = Column(String(20), nullable=True)     # low, medium, high

    is_completed = Column(Boolean, default=False)
