from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    upload = relationship("Upload", back_populates="attachments")

    in_upload_index = Column(Integer, nullable=False, default=0)

    image_file_key = Column(String, nullable=False)
