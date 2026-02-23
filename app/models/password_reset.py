from sqlalchemy import Column, DateTime, Integer, Boolean, Float, Date, ForeignKey, String, Time
from sqlalchemy.orm import relationship
from app.db.base import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=False
    )

    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # RELATIONSHIP hacia User
    user = relationship("User", back_populates="password_reset_tokens")