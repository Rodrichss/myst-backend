from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class ClinicalHistory(Base):
    __tablename__ = "clinical_history"

    id_history = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    # Relationship to User
    user = relationship("User", back_populates="clinical_history")

    # Personal Information
    # name  = clinical_history.user.name
    last_name = Column(String(50), nullable=True)
    second_last_name = Column(String(50), nullable=True)
    birthdate = Column(Date, nullable=True)
    sex_legally = Column(String(10), nullable=True)
    sex_biology = Column(String(10), nullable=True)

    # Clinical History
    depression_screening = Column(Boolean, nullable=True)
    depression = Column(Boolean, nullable=True)

    memory_screening = Column(Boolean, nullable=True)
    memory_alterations = Column(Boolean, nullable=True)
    dementia = Column(Boolean, nullable=True)

    urinary_incontinence_screening = Column(Boolean, nullable=True)
    urinary_incontinence = Column(Boolean, nullable=True)

    anemia_screening = Column(Boolean, nullable=True)
    obesity_screening = Column(Boolean, nullable=True)

    osteoporosis_screening = Column(Boolean, nullable=True)

    diabetes_mellitus = Column(String(50), nullable=True)
    arterial_hypertension = Column(Boolean, nullable=True)

    sustance_use = Column(String(50), nullable=True)

    std = Column(String(100), nullable=True)

    turner_syndrome_screening = Column(Boolean, nullable=True)

    endometriosis_screening = Column(Boolean, nullable=True)
    endometriosis = Column(Boolean, nullable=True)

    pcos_screening = Column(Boolean, nullable=True)
    pcos = Column(Boolean, nullable=True)

    average_menstrual_cycle = Column(Integer, nullable=True)
    average_ovulation = Column(Integer, nullable=True)

    sexually_active = Column(Boolean, nullable=True)
    miscarriages_abortions = Column(Integer, nullable=True)

    # Relationships
    cycles = relationship(
        "Cycle",
        back_populates="clinical_history",
        cascade="all, delete-orphan"
    )