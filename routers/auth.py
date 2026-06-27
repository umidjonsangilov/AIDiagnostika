from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.doctors import Doctor
from models.patients import Patient
from models.clinic_admin import ClinicAdmin
from models.clinic import Clinic
from models.nurse import Nurse
from pydantic import BaseModel
from schemas.schemas import LoginRequest, TokenResponse, PatientRegister
from utils.auth import verify_password, create_access_token, hash_password
from utils.geo import nearest_clinic
from data.config import SUPERADMIN_LOGIN, SUPERADMIN_PASSWORD


class SuperAdminLoginRequest(BaseModel):
    username: str
    password: str

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/superadmin/login", response_model=TokenResponse)
def superadmin_login(body: SuperAdminLoginRequest):
    if body.username != SUPERADMIN_LOGIN or body.password != SUPERADMIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Noto'g'ri ma'lumotlar")
    token = create_access_token({"sub": 0, "role": "superadmin"})
    return {"access_token": token}


@router.post("/clinic-admin/login", response_model=TokenResponse)
def clinic_admin_login(body: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(ClinicAdmin).filter(ClinicAdmin.email == body.email).first()
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email yoki parol noto'g'ri")
    token = create_access_token({"sub": admin.id, "role": "clinic_admin", "clinic_id": admin.clinic_id})
    return {"access_token": token}


@router.post("/doctor/login", response_model=TokenResponse)
def doctor_login(body: LoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.email == body.email).first()
    if not doctor or not verify_password(body.password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email yoki parol noto'g'ri")
    token = create_access_token({"sub": doctor.id, "role": "doctor", "clinic_id": doctor.clinic_id})
    return {"access_token": token}


@router.post("/patient/login", response_model=TokenResponse)
def patient_login(body: LoginRequest, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.email == body.email).first()
    if not patient or not verify_password(body.password, patient.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email yoki parol noto'g'ri")
    token = create_access_token({"sub": patient.id, "role": "patient"})
    return {"access_token": token}


@router.post("/nurse/login", response_model=TokenResponse)
def nurse_login(body: LoginRequest, db: Session = Depends(get_db)):
    nurse = db.query(Nurse).filter(Nurse.email == body.email).first()
    if not nurse or not verify_password(body.password, nurse.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email yoki parol noto'g'ri")
    token = create_access_token({"sub": nurse.id, "role": "nurse", "clinic_id": nurse.clinic_id})
    return {"access_token": token}


@router.post("/patient/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def patient_register(body: PatientRegister, db: Session = Depends(get_db)):
    if db.query(Patient).filter(Patient.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon ro'yxatdan o'tgan")

    clinic_id = body.clinic_id
    nurse_id  = None

    if body.referral_code:
        nurse = db.query(Nurse).filter(Nurse.referral_code == body.referral_code).first()
        if not nurse:
            raise HTTPException(status_code=400, detail="Taklif kodi noto'g'ri")
        clinic_id = nurse.clinic_id
        nurse_id  = nurse.id
    elif clinic_id is None and body.latitude is not None and body.longitude is not None:
        clinics = db.query(Clinic).all()
        closest = nearest_clinic(body.latitude, body.longitude, clinics)
        if closest:
            clinic_id = closest.id

    patient = Patient(
        clinic_id=clinic_id,
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        date_of_birth=body.date_of_birth,
        hashed_password=hash_password(body.password),
        latitude=body.latitude,
        longitude=body.longitude,
        referred_by_nurse_id=nurse_id,
    )
    db.add(patient)
    db.flush()

    if nurse_id:
        from models.referral import Referral
        db.add(Referral(nurse_id=nurse_id, patient_id=patient.id))

    db.commit()
    db.refresh(patient)
    token = create_access_token({"sub": patient.id, "role": "patient"})
    return {"access_token": token}
