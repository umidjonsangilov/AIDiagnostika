from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models.nurse import Nurse
from models.referral import Referral
from models.patients import Patient
from schemas.schemas import NurseResponse, ReferralResponse
from utils.auth import get_current_nurse

router = APIRouter(prefix="/nurses", tags=["nurses"])


@router.get("/me", response_model=NurseResponse)
def get_me(nurse: Nurse = Depends(get_current_nurse)):
    """Hamshiranin profili va doimiy taklif kodi."""
    return nurse


@router.get("/referrals", response_model=list[ReferralResponse])
def my_referrals(
    db: Session = Depends(get_db),
    nurse: Nurse = Depends(get_current_nurse),
):
    """Hamshira taklifi orqali ro'yxatdan o'tgan bemorlar logi."""
    return (
        db.query(Referral)
        .filter(Referral.nurse_id == nurse.id)
        .order_by(Referral.created_at.desc())
        .all()
    )


@router.get("/patients")
def my_patients(
    db: Session = Depends(get_db),
    nurse: Nurse = Depends(get_current_nurse),
):
    """Hamshira taklif qilgan bemorlar ro'yxati."""
    patients = (
        db.query(Patient)
        .filter(Patient.referred_by_nurse_id == nurse.id)
        .order_by(Patient.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "full_name": p.full_name,
            "email": p.email,
            "phone": p.phone,
            "date_of_birth": p.date_of_birth,
            "clinic_id": p.clinic_id,
            "created_at": p.created_at,
        }
        for p in patients
    ]
