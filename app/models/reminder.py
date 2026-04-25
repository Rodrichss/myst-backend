from sqlalchemy import Column, Integer, Time, Boolean, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Reminder(Base):
    __tablename__ = "reminder"

    id_reminder = Column(Integer, primary_key=True, index=True)

    id_user = Column(Integer, ForeignKey("users.id_user"), nullable = False)
    id_contact = Column(Integer, ForeignKey("contact.id_contact"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="reminders")
    contact = relationship("Contact", back_populates="reminders")

    title = Column(String(100))
    description = Column(String(255), nullable=True)

    start_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=True)
    end_date = Column(Date, nullable=True)
    end_time = Column(Time, nullable=True)

    type = Column(Boolean, nullable=True)            # medication, receipt
    dosage = Column(String(100), nullable=True)     # solo si type = True (medicamento)
    after_meal = Column(Boolean, nullable=True)     # solo si type = True (medicamento)

    status = Column(Integer, default=0, nullable=False)