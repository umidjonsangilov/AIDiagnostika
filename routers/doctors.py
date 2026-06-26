import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.doctors import Doctor
from models.patients import Patient
from models.anketa import Anketa
from models.predictionrecord import PredictionRecord
from models.chats import Message
from schemas.schemas import DoctorResponse, PatientResponse
from utils.auth import get_current_doctor

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/me", response_model=DoctorResponse)
def get_me(doctor: Doctor = Depends(get_current_doctor)):
    return doctor


@router.get("/patients", response_model=list[PatientResponse])
def clinic_patients(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """Doktor o'z klinikasidagi barcha bemorlarni ko'radi."""
    return (
        db.query(Patient)
        .filter(Patient.clinic_id == doctor.clinic_id)
        .offset(skip).limit(limit).all()
    )


@router.get("/patients/{patient_id}")
def patient_full(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """Bitta bemorning barcha ma'lumotlari: profil, anketalar, tekshiruvlar."""
    from routers.diagnostic import GRADES

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.clinic_id == doctor.clinic_id,
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Bemor topilmadi yoki boshqa klinikaga tegishli.")

    anketas = db.query(Anketa).filter(Anketa.patient_id == patient.id).order_by(Anketa.created_at.desc()).all()
    predictions = db.query(PredictionRecord).filter(PredictionRecord.patient_id == patient.id).order_by(PredictionRecord.created_at.desc()).all()

    return {
        "profile": {
            "id": patient.id,
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": patient.phone,
            "date_of_birth": patient.date_of_birth,
            "clinic_id": patient.clinic_id,
            "created_at": patient.created_at,
        },
        "anketas": [
            {"id": a.id, "status": a.status, "assigned_doctor_id": a.assigned_doctor_id,
             "created_at": a.created_at, "anketa": json.loads(a.content)}
            for a in anketas
        ],
        "predictions": [
            {"id": r.id, "filename": r.filename, "diagnosis": r.diagnosis,
             "grade_name": GRADES[r.diagnosis]["name"], "grade_uz": GRADES[r.diagnosis]["uz"],
             "confidence": round(r.confidence * 100, 2), "created_at": r.created_at}
            for r in predictions
        ],
    }
