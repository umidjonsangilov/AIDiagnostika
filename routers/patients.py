import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.patients import Patient
from models.anketa import Anketa
from models.chats import Message
from schemas.schemas import PatientUpdate, PatientResponse
from utils.auth import get_current_patient

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientResponse)
def get_me(patient: Patient = Depends(get_current_patient)):
    return patient


@router.patch("/me", response_model=PatientResponse)
def update_me(
    body: PatientUpdate,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/me/anketas")
def my_anketas(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    anketas = (
        db.query(Anketa)
        .filter(Anketa.patient_id == patient.id)
        .order_by(Anketa.created_at.desc())
        .all()
    )
    return [
        {
            "id": a.id,
            "status": a.status,
            "assigned_doctor_id": a.assigned_doctor_id,
            "created_at": a.created_at,
            "anketa": json.loads(a.content),
        }
        for a in anketas
    ]


@router.get("/me/chat")
def my_chat(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    messages = (
        db.query(Message)
        .filter(Message.patient_id == patient.id)
        .order_by(Message.created_at)
        .all()
    )
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]


@router.get("/me/all")
def my_all_data(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    """Bemorning barcha ma'lumotlari bir so'rovda."""
    from models.predictionrecord import PredictionRecord
    from routers.diagnostic import GRADES

    anketas = db.query(Anketa).filter(Anketa.patient_id == patient.id).order_by(Anketa.created_at.desc()).all()
    predictions = db.query(PredictionRecord).filter(PredictionRecord.patient_id == patient.id).order_by(PredictionRecord.created_at.desc()).all()
    messages = db.query(Message).filter(Message.patient_id == patient.id).order_by(Message.created_at).all()

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
        "chat": [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages],
    }
