from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .base import BaseTable


class Message(BaseTable):
    __tablename__ = "messages"

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    role       = Column(String(20), nullable=False)   # "user" | "assistant"
    content    = Column(Text, nullable=False)
