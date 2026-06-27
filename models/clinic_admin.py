from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .base import BaseTable


class ClinicAdmin(BaseTable):
    __tablename__ = "clinic_admins"

    clinic_id       = Column(Integer, ForeignKey("clinics.id"), nullable=False, index=True)
    full_name       = Column(String(150), nullable=False)
    username        = Column(String(100), unique=True, nullable=True)
    email           = Column(String(255), unique=True, nullable=True)
    phone           = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_assistant    = Column(Boolean, nullable=False, default=False)
