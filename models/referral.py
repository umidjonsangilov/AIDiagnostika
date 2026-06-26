from sqlalchemy import Column, Integer, ForeignKey
from .base import BaseTable


class Referral(BaseTable):
    """Hamshira taklif qilgan bemorlarni qayd etuvchi log."""
    __tablename__ = "referrals"

    nurse_id   = Column(Integer, ForeignKey("nurses.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, unique=True)
