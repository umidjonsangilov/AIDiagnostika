from sqlalchemy import Column, Integer, Text, String, ForeignKey
from .base import BaseTable


class Anketa(BaseTable):
    __tablename__ = "anketas"

    patient_id          = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    clinic_id           = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    assigned_doctor_id  = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    content             = Column(Text, nullable=False)          # JSON
    status              = Column(String(20), nullable=False, default="yangi")
    # yangi | ko'rildi | shifokorga_berildi
