from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class LabStudy(Base):
    __tablename__ = "lab_studies"

    id_study = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)

    laboratory_name = Column(String(100), nullable=True)
    test_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="lab_studies")
    results = relationship(
        "LabResult",
        back_populates="study",
        cascade="all, delete-orphan"
    )


class LabResult(Base):
    __tablename__ = "lab_results"

    id_result = Column(Integer, primary_key=True, index=True)
    id_study = Column(Integer, ForeignKey("lab_studies.id_study"), nullable=False)

    parameter = Column(String(100), nullable=False)      # TSH, Glucosa, etc.
    value = Column(Float, nullable=False)                # 3.390
    unit = Column(String(20), nullable=True)             # uUI/mL
    reference_range = Column(String(100), nullable=True) # "0.510 - 4.300"

    study = relationship("LabStudy", back_populates="results")