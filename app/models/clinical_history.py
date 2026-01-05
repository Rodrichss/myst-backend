from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.db.base import Base

class ClinicalHistory(Base):
    __tablename__ = "clinical_history"

    id_history = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    # Personal Information
    #name = Column(String(50))
    last_name = Column(String(50))
    second_last_name = Column(String(50))
    birthdate = Column(Date)
    sex_legally = Column(String(10))
    sex_biology = Column(String(10))

    # Clinical History
    depression_screening = Column(Boolean)
    depression = Column(Boolean)

    memory_screening = Column(Boolean)
    memory_alterations = Column(Boolean)
    dementia = Column(Boolean)

    urinary_incontinence_screening = Column(Boolean)
    urinary_incontinence = Column(Boolean)

    anemia_screening = Column(Boolean)
    obesity_screening = Column(Boolean)

    osteoporosis_screening = Column(Boolean)

    diabetes_mellitus = Column(String(50))

    arterial_hypertension = Column(Boolean)

    sustance_use = Column(String(50))

    std = Column(String(100))

    turner_syndrome_screening = Column(Boolean)

    endometriosis_screening = Column(Boolean)
    endometriosis = Column(Boolean)

    pcos_screening = Column(Boolean)
    pcos = Column(Boolean)

    average_menstrual_cycle = Column(Integer)
    average_ovulation = Column(Integer)

    sexually_active = Column(Boolean)
    miscarriages_abortions = Column(Integer)