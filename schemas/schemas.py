from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional


class PredictionResponse(BaseModel):
    id: int
    filename: str
    diagnosis: int
    grade_name: str
    grade_uz: str
    description: str
    confidence: float
    probabilities: dict[str, float]
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    id: int
    filename: str
    diagnosis: int
    grade_name: str
    grade_uz: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class GradesResponse(BaseModel):
    grades: dict


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Clinic ────────────────────────────────────────────────────────────────────

class ClinicCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ClinicResponse(BaseModel):
    id: int
    name: str
    address: str
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ── ClinicAdmin ───────────────────────────────────────────────────────────────

class ClinicAdminCreate(BaseModel):
    clinic_id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class ClinicAdminResponse(BaseModel):
    id: int
    clinic_id: int
    full_name: str
    email: str
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Doctor ────────────────────────────────────────────────────────────────────

class DoctorCreate(BaseModel):
    full_name: str
    specialization: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class DoctorResponse(BaseModel):
    id: int
    clinic_id: int
    full_name: str
    specialization: str
    email: str
    phone: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Nurse ─────────────────────────────────────────────────────────────────────

class NurseCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class NurseResponse(BaseModel):
    id: int
    clinic_id: int
    full_name: str
    email: str
    phone: Optional[str]
    referral_code: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReferralResponse(BaseModel):
    id: int
    nurse_id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Patient ───────────────────────────────────────────────────────────────────

class PatientRegister(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    referral_code: Optional[str] = None


class PatientCreate(BaseModel):           # Klinika admin tomonidan yaratish
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    clinic_id: Optional[int] = None


class PatientResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    clinic_id: Optional[int]
    referred_by_nurse_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
