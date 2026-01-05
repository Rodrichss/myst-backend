from sqlalchemy import Column, Integer, Boolean, Float, Date, ForeignKey, String, Time
from app.db.base import Base

class Cycle(Base):
    __tablename__ = "cycle"

    id_cycle_entry = Column(Integer, primary_key=True, index=True)
    id_history = Column(Integer, ForeignKey("clinical_history.id_history"))

    weight = Column(Float)
    height = Column(Float)
    waist_circumference = Column(Float)

    systolic_bp = Column(Integer)
    diastolic_bp = Column(Integer)
    heart_rate = Column(Integer)

    body_temperature = Column(Float)
    glycemia = Column(Float)

    anticonceptive_use = Column(Boolean)
    anticonceptive_type = Column(String(50))

    sexual_penetration = Column(Boolean)

    on_fertile_window = Column(Boolean)

    menstrual_flow = Column(Integer)
    vaginal_discharge = Column(Integer)

    mood = Column(Integer)

    anxiety = Column(Integer)
    stress = Column(Integer)

    sleep_time = Column(Time)

    exercise = Column(String(50))
    exercise_time = Column(Time)

    cramps = Column(Integer)
    cravings = Column(Integer)

    symptoms = Column(String(255))

    pregnancy_test = Column(Integer)
    ovulation_test = Column(Integer)

    water_consumption = Column(Float)

    hobbies_activities = Column(String(100))

    notes = Column(String(255))

    period_start_date = Column(Date)
    period_end_date = Column(Date)