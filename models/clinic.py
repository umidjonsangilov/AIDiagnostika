from sqlalchemy import Column, String, Float
from .base import BaseTable


class Clinic(BaseTable):
    __tablename__ = "clinics"

    name      = Column(String(200), nullable=False)
    address   = Column(String(400), nullable=False)
    phone     = Column(String(30), nullable=True)
    latitude  = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
