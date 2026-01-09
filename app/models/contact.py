from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

# app/models/contact.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Contact(Base):
    __tablename__ = "contact"

    id_contact = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"))

    #  Relationship to user
    user = relationship(
        "User",
        back_populates="contacts"
    )

    name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    phone_number = Column(String(20), unique=True)
    address = Column(String(200))

    # Relationships
    reminders = relationship(
        "Reminder",
        back_populates="contact"
    )