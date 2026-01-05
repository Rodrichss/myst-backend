from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Contact(Base):
    __tablename__ = "contact"

    id_contact = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("user.id_user"))

    name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    phone_number = Column(String(20), unique=True)
    address = Column(String(200))