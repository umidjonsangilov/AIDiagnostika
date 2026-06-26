from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.sql import func
from .base import BaseTable


class PredictionRecord(BaseTable):
    __tablename__ = "predictions"

    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    filename   = Column(String(255), nullable=False)
    diagnosis  = Column(Integer, nullable=False)       # 0-4
    confidence = Column(Float, nullable=False)         # 0.0-1.0
    prob_0     = Column(Float, nullable=False)
    prob_1     = Column(Float, nullable=False)
    prob_2     = Column(Float, nullable=False)
    prob_3     = Column(Float, nullable=False)
    prob_4     = Column(Float, nullable=False)
