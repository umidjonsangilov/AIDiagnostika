from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from data.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

superadmin_scheme    = OAuth2PasswordBearer(tokenUrl="/auth/superadmin/login",    scheme_name="SuperAdminBearer")
system_admin_scheme  = OAuth2PasswordBearer(tokenUrl="/auth/system-admin/login",  scheme_name="SystemAdminBearer")
clinic_admin_scheme  = OAuth2PasswordBearer(tokenUrl="/auth/clinic-admin/login",  scheme_name="ClinicAdminBearer")
doctor_scheme        = OAuth2PasswordBearer(tokenUrl="/auth/doctor/login",        scheme_name="DoctorBearer")
patient_scheme       = OAuth2PasswordBearer(tokenUrl="/auth/patient/login",       scheme_name="PatientBearer")
nurse_scheme         = OAuth2PasswordBearer(tokenUrl="/auth/nurse/login",         scheme_name="NurseBearer")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode(token: str, expected_role: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token noto'g'ri yoki muddati o'tgan",
                            headers={"WWW-Authenticate": "Bearer"})
    if payload.get("role") != expected_role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")
    return payload


def get_current_superadmin(token: str = Depends(superadmin_scheme)):
    return _decode(token, "superadmin")


def get_current_system_admin(token: str = Depends(system_admin_scheme), db: Session = Depends(get_db)):
    from models.system_admin import SystemAdmin
    payload = _decode(token, "system_admin")
    admin = db.query(SystemAdmin).filter(SystemAdmin.id == payload["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizim admini topilmadi")
    return admin


def get_current_clinic_admin(token: str = Depends(clinic_admin_scheme), db: Session = Depends(get_db)):
    from models.clinic_admin import ClinicAdmin
    payload = _decode(token, "clinic_admin")
    admin = db.query(ClinicAdmin).filter(ClinicAdmin.id == payload["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin topilmadi")
    return admin


def get_current_main_clinic_admin(token: str = Depends(clinic_admin_scheme), db: Session = Depends(get_db)):
    admin = get_current_clinic_admin(token=token, db=db)
    if admin.is_assistant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu amal faqat asosiy admin uchun")
    return admin


def get_current_doctor(token: str = Depends(doctor_scheme), db: Session = Depends(get_db)):
    from models.doctors import Doctor
    payload = _decode(token, "doctor")
    doctor = db.query(Doctor).filter(Doctor.id == payload["sub"]).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Doktor topilmadi")
    return doctor


def get_current_patient(token: str = Depends(patient_scheme), db: Session = Depends(get_db)):
    from models.patients import Patient
    payload = _decode(token, "patient")
    patient = db.query(Patient).filter(Patient.id == payload["sub"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bemor topilmadi")
    return patient


def get_current_nurse(token: str = Depends(nurse_scheme), db: Session = Depends(get_db)):
    from models.nurse import Nurse
    payload = _decode(token, "nurse")
    nurse = db.query(Nurse).filter(Nurse.id == payload["sub"]).first()
    if not nurse:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Hamshira topilmadi")
    return nurse
