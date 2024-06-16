from sqlalchemy import Column, Integer, DateTime, String, func, BigInteger
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, nullable=False, primary_key=True, index=True)

    role = Column(String, nullable=False, default="basic")
    register_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    uploads = relationship("Upload", back_populates="user")
