import hashlib
import base64
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from data.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_bearer = HTTPBearer(scheme_name="Bearer")


def _prepare(password: str) -> str:
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()


def hash_password(password: str) -> str:
    return pwd_context.hash(_prepare(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prepare(plain), hashed)


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


def get_current_superadmin(x_token: str = Header(..., alias="X-Token")):
    from data.config import SUPERADMIN_TOKEN
    if x_token != SUPERADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token noto'g'ri")


def get_current_system_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.system_admin import SystemAdmin
    payload = _decode(credentials.credentials, "system_admin")
    admin = db.query(SystemAdmin).filter(SystemAdmin.id == payload["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tizim admini topilmadi")
    return admin


def get_current_clinic_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.clinic_admin import ClinicAdmin
    payload = _decode(credentials.credentials, "clinic_admin")
    admin = db.query(ClinicAdmin).filter(ClinicAdmin.id == payload["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin topilmadi")
    return admin


def get_current_main_clinic_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.clinic_admin import ClinicAdmin
    payload = _decode(credentials.credentials, "clinic_admin")
    admin = db.query(ClinicAdmin).filter(ClinicAdmin.id == payload["sub"]).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin topilmadi")
    if admin.is_assistant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu amal faqat asosiy admin uchun")
    return admin


def get_current_doctor(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.doctors import Doctor
    payload = _decode(credentials.credentials, "doctor")
    doctor = db.query(Doctor).filter(Doctor.id == payload["sub"]).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Doktor topilmadi")
    return doctor


def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.patients import Patient
    payload = _decode(credentials.credentials, "patient")
    patient = db.query(Patient).filter(Patient.id == payload["sub"]).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bemor topilmadi")
    return patient


def get_current_nurse(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
):
    from models.nurse import Nurse
    payload = _decode(credentials.credentials, "nurse")
    nurse = db.query(Nurse).filter(Nurse.id == payload["sub"]).first()
    if not nurse:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Hamshira topilmadi")
    return nurse
