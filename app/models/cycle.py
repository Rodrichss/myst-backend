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
    weight = Column(Float)
    height = Column(Float)
    waist_circumference = Column(Float)

    # Vital Signs
    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    heart_rate = Column(Integer)

    body_temperature = Column(Float)
    glycemia = Column(Float)

    # Anticonceptives and sexual activity
    anticonceptive_use = Column(Boolean)
    anticonceptive_type = Column(String(50))

    sexual_penetration = Column(Boolean)

    on_fertile_window = Column(Boolean)

    # Flow and secretions
    menstrual_flow = Column(Integer)
    vaginal_discharge = Column(Integer)

    # Mood
    mood = Column(Integer)

    anxiety = Column(Integer)
    stress = Column(Integer)

    # Habits
    sleep_time = Column(Time)

    exercise = Column(String(50))
    exercise_time = Column(Time)

    water_consumption = Column(Float)

    hobbies_activities = Column(String(100))

    # Symptoms
    cramps = Column(Integer)
    cravings = Column(Integer)
    symptoms = Column(String(255))

    # Tests
    pregnancy_test = Column(Integer)
    ovulation_test = Column(Integer)

    # Notes
    notes = Column(String(255))

    # Dates
    period_start_date = Column(Date)
    period_end_date = Column(Date)