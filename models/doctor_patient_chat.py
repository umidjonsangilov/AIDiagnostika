from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .base import BaseTable


class DoctorPatientMessage(BaseTable):
    __tablename__ = "doctor_patient_messages"

    doctor_id    = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    patient_id   = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    sender_type  = Column(String(10), nullable=False)          # "doctor" | "patient"
    message_type = Column(String(10), nullable=False, default="text")  # "text" | "image"
    content      = Column(Text, nullable=True)
    image_url    = Column(String(500), nullable=True)
