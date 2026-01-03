from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.db.base import Base

class Cycle(Base):
    __tablename__ = "cycle"

    id_cycle_entry = Column(Integer, primary_key=True, index=True)
    id_history = Column(Integer, ForeignKey("clinical_history.id_history"))

    weight = Column(Float)
    mood = Column(Integer)
    cramps = Column(Integer)
    period_start_date = Column(Date)
    period_end_date = Column(Date)