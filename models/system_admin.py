from sqlalchemy import Column, String
from .base import BaseTable


class SystemAdmin(BaseTable):
    __tablename__ = "system_admins"

    full_name       = Column(String(150), nullable=False)
    username        = Column(String(100), unique=True, nullable=True)
    email           = Column(String(255), unique=True, nullable=True)
    phone           = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
