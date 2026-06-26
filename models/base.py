from sqlalchemy import Column, Integer, DateTime, func
from db.database import Base

class BaseTable(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_onupdate=func.now())