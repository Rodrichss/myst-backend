from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.db.base import Base

class ClinicalHistory(Base):
    __tablename__ = "clinical_history"

    id_history = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    birthdate = Column(Date)
    depression = Column(Boolean)
    pcos = Column(Boolean)
    average_menstrual_cycle = Column(Integer)