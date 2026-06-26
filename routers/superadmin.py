from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.clinic import Clinic
from models.clinic_admin import ClinicAdmin
from schemas.schemas import ClinicCreate, ClinicResponse, ClinicAdminCreate, ClinicAdminResponse
from utils.auth import get_current_superadmin, hash_password

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.post("/clinics", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED)
def create_clinic(
    body: ClinicCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    clinic = Clinic(**body.model_dump())
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic


@router.get("/clinics", response_model=list[ClinicResponse])
def list_clinics(
    db: Session = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    return db.query(Clinic).all()


@router.post("/clinic-admins", response_model=ClinicAdminResponse, status_code=status.HTTP_201_CREATED)
def create_clinic_admin(
    body: ClinicAdminCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    if not db.query(Clinic).filter(Clinic.id == body.clinic_id).first():
        raise HTTPException(status_code=404, detail="Klinika topilmadi")
    if db.query(ClinicAdmin).filter(ClinicAdmin.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon mavjud")
    admin = ClinicAdmin(
        clinic_id=body.clinic_id,
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        hashed_password=hash_password(body.password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
