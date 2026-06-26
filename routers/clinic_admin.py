import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.clinic import Clinic
from models.clinic_admin import ClinicAdmin
from models.doctors import Doctor
from models.patients import Patient
from models.nurse import Nurse
from schemas.schemas import DoctorCreate, DoctorResponse, ClinicUpdate, ClinicResponse, PatientResponse, NurseCreate, NurseResponse
from utils.auth import get_current_clinic_admin, hash_password

router = APIRouter(prefix="/clinic-admin", tags=["clinic-admin"])


@router.get("/clinic", response_model=ClinicResponse)
def get_my_clinic(
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    return db.query(Clinic).filter(Clinic.id == admin.clinic_id).first()


@router.patch("/clinic", response_model=ClinicResponse)
def update_my_clinic(
    body: ClinicUpdate,
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    clinic = db.query(Clinic).filter(Clinic.id == admin.clinic_id).first()
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(clinic, field, value)
    db.commit()
    db.refresh(clinic)
    return clinic


@router.post("/doctors", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(
    body: DoctorCreate,
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    if db.query(Doctor).filter(Doctor.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon mavjud")
    doctor = Doctor(
        clinic_id=admin.clinic_id,
        full_name=body.full_name,
        specialization=body.specialization,
        email=body.email,
        phone=body.phone,
        hashed_password=hash_password(body.password),
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/doctors", response_model=list[DoctorResponse])
def list_doctors(
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    return db.query(Doctor).filter(Doctor.clinic_id == admin.clinic_id).all()


@router.get("/patients", response_model=list[PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    return db.query(Patient).filter(Patient.clinic_id == admin.clinic_id).all()


@router.post("/nurses", response_model=NurseResponse, status_code=status.HTTP_201_CREATED)
def create_nurse(
    body: NurseCreate,
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    if db.query(Nurse).filter(Nurse.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon mavjud")

    # Noyob doimiy taklif kodi (8 bayt = 16 hex belgi)
    code = secrets.token_hex(8).upper()
    while db.query(Nurse).filter(Nurse.referral_code == code).first():
        code = secrets.token_hex(8).upper()

    nurse = Nurse(
        clinic_id=admin.clinic_id,
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        hashed_password=hash_password(body.password),
        referral_code=code,
    )
    db.add(nurse)
    db.commit()
    db.refresh(nurse)
    return nurse


@router.get("/nurses", response_model=list[NurseResponse])
def list_nurses(
    db: Session = Depends(get_db),
    admin: ClinicAdmin = Depends(get_current_clinic_admin),
):
    return db.query(Nurse).filter(Nurse.clinic_id == admin.clinic_id).all()
