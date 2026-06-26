from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from .base import BaseTable


class Patient(BaseTable):
    __tablename__ = "patients"

    clinic_id            = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    full_name            = Column(String(150), nullable=False)
    date_of_birth        = Column(Date, nullable=True)
    email                = Column(String(255), unique=True, nullable=False)
    phone                = Column(String(20), nullable=True)
    hashed_password      = Column(String(255), nullable=False)
    latitude             = Column(Float, nullable=True)
    longitude            = Column(Float, nullable=True)
    referred_by_nurse_id = Column(Integer, ForeignKey("nurses.id"), nullable=True, index=True)
