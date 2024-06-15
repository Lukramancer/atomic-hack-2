from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, String, func, DateTime
from sqlalchemy.orm import relationship

from .base import Base


@dataclass
class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, nullable=False, primary_key=True, index=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="uploads")

    input_image_key = Column(String, nullable=False)
    creation_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    chat_id = Column(Integer, nullable=True)
    bot_message_id = Column(Integer, nullable=True)

    description = Column(String, nullable=True)

    output_image_key = Column(String, nullable=True)

    attachments = relationship("Attachment", back_populates="upload")
