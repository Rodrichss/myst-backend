from sqlalchemy import Column, Integer, Boolean, Float, Date, ForeignKey, String, Time
from sqlalchemy.orm import relationship
from app.db.base import Base

class Cycle(Base):
    __tablename__ = "cycle"

    id_cycle_entry = Column(Integer, primary_key=True, index=True)
    id_history = Column(Integer, ForeignKey("clinical_history.id_history"))

    # Relationship to ClinicalHistory
    clinical_history = relationship("ClinicalHistory", back_populates="cycles")

    # Antropometry
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    waist_circumference = Column(Float, nullable=True)

    # Vital Signs
    systolic_bp = Column(Integer, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)

    body_temperature = Column(Float, nullable=True)
    glycemia = Column(Float, nullable=True)

    # Anticonceptives and sexual activity
    anticonceptive_use = Column(Boolean, nullable=True)
    anticonceptive_type = Column(String(50), nullable=True)

    sexual_penetration = Column(Boolean, nullable=True)

    on_fertile_window = Column(Boolean, nullable=True)

    # Flow and secretions
    menstrual_flow = Column(Integer, nullable=True)
    vaginal_discharge = Column(Integer, nullable=True)

    # Mood
    mood = Column(Integer, nullable=True)

    anxiety = Column(Integer, nullable=True)
    stress = Column(Integer, nullable=True)

    # Habits
    sleep_time = Column(Time, nullable=True)

    exercise = Column(String(50), nullable=True)
    exercise_time = Column(Time, nullable=True)

    water_consumption = Column(Float, nullable=True)

    hobbies_activities = Column(String(100), nullable=True)

    # Symptoms
    cramps = Column(Integer, nullable=True)
    cravings = Column(Integer, nullable=True)
    symptoms = Column(String(255), nullable=True)

    # Tests
    pregnancy_test = Column(Integer, nullable=True)
    ovulation_test = Column(Integer, nullable=True)

    # Notes
    notes = Column(String(255), nullable=True)

    # Dates
    period_start_date = Column(Date, nullable=True)
    period_end_date = Column(Date, nullable=True)