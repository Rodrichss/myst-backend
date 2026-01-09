from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    password = Column(String(255))
    initials = Column(String(6), nullable=True)
    picture = Column(String(50), nullable=True)

    # Relationships
    clinical_history = relationship(
        "ClinicalHistory",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    contacts = relationship(
        "Contact",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    reminders = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan"
    )