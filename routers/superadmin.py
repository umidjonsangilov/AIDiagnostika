from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.system_admin import SystemAdmin
from schemas.schemas import SystemAdminCreate, SystemAdminResponse
from utils.auth import get_current_superadmin, hash_password

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


@router.post("/system-admins", response_model=SystemAdminResponse, status_code=status.HTTP_201_CREATED)
def create_system_admin(
    body: SystemAdminCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    if db.query(SystemAdmin).filter(SystemAdmin.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bu email allaqachon mavjud")
    admin = SystemAdmin(
        full_name=body.full_name,
        email=body.email,
        phone=body.phone,
        hashed_password=hash_password(body.password),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.get("/system-admins", response_model=list[SystemAdminResponse])
def list_system_admins(
    db: Session = Depends(get_db),
    _=Depends(get_current_superadmin),
):
    return db.query(SystemAdmin).all()
