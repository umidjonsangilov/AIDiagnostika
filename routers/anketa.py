import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.anketa import Anketa
from models.clinic_admin import ClinicAdmin
from models.doctors import Doctor
from utils.auth import get_current_clinic_admin, get_current_doctor

router = APIRouter(prefix="/anketa", tags=["anketa"])


def _serialize(a: Anketa) -> dict:
    return {
        "id": a.id,
        "patient_id": a.patient_id,
        "clinic_id": a.clinic_id,
        "assigned_doctor_id": a.assigned_doctor_id,
        "status": a.status,
        "created_at": a.created_at,
        "anketa": json.loads(a.content),
    }


# ── Klinika admin ko'rinishi ──────────────────────────────────────────────────

@router.get("/admin", summary="Klinikaga kelgan barcha anketalar")
def admin_list(
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    q = db.query(Anketa).filter(Anketa.clinic_id == admin.clinic_id)
    if status:
        q = q.filter(Anketa.status == status)
    return [_serialize(a) for a in q.order_by(Anketa.created_at.desc()).offset(skip).limit(limit)]


@router.patch("/admin/{anketa_id}/assign/{doctor_id}", summary="Anketani doktorga biriktirish")
def assign_doctor(
    anketa_id: int,
    doctor_id: int,
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    anketa = db.query(Anketa).filter(
        Anketa.id == anketa_id, Anketa.clinic_id == admin.clinic_id
    ).first()
    if not anketa:
        raise HTTPException(status_code=404, detail="Anketa topilmadi")
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id, Doctor.clinic_id == admin.clinic_id
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doktor topilmadi yoki boshqa klinikaga tegishli")
    anketa.assigned_doctor_id = doctor_id
    anketa.status = "shifokorga_berildi"
    db.commit()
    return _serialize(anketa)


# ── Doktor ko'rinishi ─────────────────────────────────────────────────────────

@router.get("/doctor", summary="Doktorga biriktirilgan anketalar")
def doctor_list(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    q = db.query(Anketa).filter(Anketa.assigned_doctor_id == doctor.id)
    return [_serialize(a) for a in q.order_by(Anketa.created_at.desc()).offset(skip).limit(limit)]


@router.get("/doctor/{anketa_id}")
def doctor_get(
    anketa_id: int,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    anketa = db.query(Anketa).filter(
        Anketa.id == anketa_id, Anketa.assigned_doctor_id == doctor.id
    ).first()
    if not anketa:
        raise HTTPException(status_code=404, detail="Anketa topilmadi")
    if anketa.status == "shifokorga_berildi":
        anketa.status = "ko'rildi"
        db.commit()
    return _serialize(anketa)
