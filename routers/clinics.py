from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from models.clinic import Clinic
from schemas.schemas import ClinicResponse
from utils.geo import haversine_km

router = APIRouter(prefix="/clinics", tags=["clinics"])


@router.get("", response_model=list[ClinicResponse])
def list_clinics(db: Session = Depends(get_db)):
    return db.query(Clinic).all()


@router.get("/nearest", response_model=ClinicResponse)
def nearest(
    lat: float = Query(..., description="Bemor kengligi (latitude)"),
    lon: float = Query(..., description="Bemor uzunligi (longitude)"),
    db: Session = Depends(get_db),
):
    clinics = db.query(Clinic).filter(
        Clinic.latitude.isnot(None),
        Clinic.longitude.isnot(None),
    ).all()

    if not clinics:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Koordinatali klinika topilmadi")

    closest = min(clinics, key=lambda c: haversine_km(lat, lon, c.latitude, c.longitude))
    return closest
