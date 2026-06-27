from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.doctors import Doctor
from models.patients import Patient
from models.clinic_admin import ClinicAdmin
from models.system_admin import SystemAdmin
from models.clinic import Clinic
from models.nurse import Nurse
from schemas.schemas import UsernameLoginRequest, PhoneLoginRequest, TokenResponse, PatientRegister
from utils.auth import verify_password, create_access_token, hash_password
from utils.geo import nearest_clinic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/system-admin/login", response_model=TokenResponse)
def system_admin_login(body: UsernameLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(SystemAdmin).filter(SystemAdmin.username == body.username).first()
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username yoki parol noto'g'ri")
    token = create_access_token({"sub": admin.id, "role": "system_admin"})
    return {"access_token": token}


@router.post("/clinic-admin/login", response_model=TokenResponse)
def clinic_admin_login(body: UsernameLoginRequest, db: Session = Depends(get_db)):
    admin = db.query(ClinicAdmin).filter(ClinicAdmin.username == body.username).first()
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username yoki parol noto'g'ri")
    token = create_access_token({"sub": admin.id, "role": "clinic_admin", "clinic_id": admin.clinic_id})
    return {"access_token": token}


@router.post("/doctor/login", response_model=TokenResponse)
def doctor_login(body: UsernameLoginRequest, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.username == body.username).first()
    if not doctor or not verify_password(body.password, doctor.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username yoki parol noto'g'ri")
    token = create_access_token({"sub": doctor.id, "role": "doctor", "clinic_id": doctor.clinic_id})
    return {"access_token": token}


@router.post("/patient/login", response_model=TokenResponse)
def patient_login(body: PhoneLoginRequest, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.phone == body.phone).first()
    if not patient or not patient.hashed_password or not verify_password(body.password, patient.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Telefon yoki parol noto'g'ri")
    token = create_access_token({"sub": patient.id, "role": "patient"})
    return {"access_token": token}


@router.post("/nurse/login", response_model=TokenResponse)
def nurse_login(body: UsernameLoginRequest, db: Session = Depends(get_db)):
    nurse = db.query(Nurse).filter(Nurse.username == body.username).first()
    if not nurse or not verify_password(body.password, nurse.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username yoki parol noto'g'ri")
    token = create_access_token({"sub": nurse.id, "role": "nurse", "clinic_id": nurse.clinic_id})
    return {"access_token": token}


@router.post("/patient/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def patient_register(body: PatientRegister, db: Session = Depends(get_db)):
    if db.query(Patient).filter(Patient.username == body.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu username allaqachon band")
    if body.email and db.query(Patient).filter(Patient.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon ro'yxatdan o'tgan")

    clinic_id = None
    nurse_id  = None

    if body.referral_code:
        nurse = db.query(Nurse).filter(Nurse.referral_code == body.referral_code).first()
        if not nurse:
            raise HTTPException(status_code=400, detail="Taklif kodi noto'g'ri")
        clinic_id = nurse.clinic_id
        nurse_id  = nurse.id

    patient = Patient(
        clinic_id=clinic_id,
        full_name=body.full_name,
        username=body.username,
        phone=body.phone,
        email=body.email,
        hashed_password=hash_password(body.password),
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
