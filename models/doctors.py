from sqlalchemy import Column, Integer, String, ForeignKey
from .base import BaseTable


class Doctor(BaseTable):
    __tablename__ = "doctors"

    clinic_id       = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    full_name       = Column(String(150), nullable=False)
    username        = Column(String(100), unique=True, nullable=True)
    specialization  = Column(String(150), nullable=False)
    email           = Column(String(255), unique=True, nullable=True)
    phone           = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
