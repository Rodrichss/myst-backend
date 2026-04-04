from sqlalchemy import Column, Integer, Boolean, Float, Date, ForeignKey, String, Time
from sqlalchemy.orm import relationship
from app.db.base import Base
class Cycle(Base):
    __tablename__ = "cycle"

    id_cycle = Column(Integer, primary_key=True, index=True)
    id_history = Column(Integer, ForeignKey("clinical_history.id_history"))

    # Relationship to ClinicalHistory
    clinical_history = relationship("ClinicalHistory", back_populates="cycles")

    # Order within the history (1 = first cycle, 2 = second, etc.)
    # Useful for PDFs and sorting without relying on dates alone
    position = Column(Integer, nullable=True)

    # Dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Relationships
    daily_logs = relationship(
        "DailyLog",
        back_populates="cycle",
        cascade="all, delete-orphan"
    )