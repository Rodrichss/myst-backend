from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
class Address(Base):
    __tablename__ = "address"

    id_address = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)

    # Relationship to User
    user = relationship("User", back_populates="addresses")

    # Relationship to Contact (una dirección puede estar asignada a varios contactos)
    contacts = relationship("Contact", back_populates="address_ref")

    name = Column(String(100), nullable=False)        # ej. "Casa", "Trabajo"
    street = Column(String(200), nullable=False)
    neighborhood = Column(String(100), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(10), nullable=True)
    phone_number = Column(String(20), nullable=True)

    is_selected = Column(Boolean, default=False, nullable=False)
