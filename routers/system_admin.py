from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.clinic import Clinic
from models.clinic_admin import ClinicAdmin
from schemas.schemas import (
    ClinicWithAdminCreate, ClinicWithAdminResponse,
    ClinicResponse, ClinicAdminResponse,
)
from utils.auth import get_current_system_admin, hash_password

router = APIRouter(prefix="/system-admin", tags=["system-admin"])


@router.post("/clinics", response_model=ClinicWithAdminResponse, status_code=status.HTTP_201_CREATED)
def create_clinic_with_admin(
    body: ClinicWithAdminCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_system_admin),
):
    if db.query(ClinicAdmin).filter(ClinicAdmin.email == body.admin_email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu admin email allaqachon mavjud")

    clinic = Clinic(
        name=body.clinic_name,
        address=body.clinic_address,
        phone=body.clinic_phone,
        latitude=body.clinic_latitude,
        longitude=body.clinic_longitude,
    )
    db.add(clinic)
    db.flush()

    admin = ClinicAdmin(
        clinic_id=clinic.id,
        full_name=body.admin_full_name,
        email=body.admin_email,
        phone=body.admin_phone,
        hashed_password=hash_password(body.admin_password),
    )
    db.add(admin)
    db.commit()
    db.refresh(clinic)
    db.refresh(admin)

    return {"clinic": clinic, "admin": admin}


@router.get("/clinics", response_model=list[ClinicResponse])
def list_clinics(
    db: Session = Depends(get_db),
    _=Depends(get_current_system_admin),
):
    return db.query(Clinic).all()


@router.get("/clinics/{clinic_id}/admins", response_model=list[ClinicAdminResponse])
def list_clinic_admins(
    clinic_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_system_admin),
):
    if not db.query(Clinic).filter(Clinic.id == clinic_id).first():
        raise HTTPException(status_code=404, detail="Kasalxona topilmadi")
    return db.query(ClinicAdmin).filter(ClinicAdmin.clinic_id == clinic_id).all()
