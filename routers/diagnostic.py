from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.schemas import HistoryResponse, PredictionResponse, GradesResponse
from utils.ml import predict_image
from utils.auth import get_current_patient
from models.predictionrecord import PredictionRecord
from models.patients import Patient

router = APIRouter(tags=["diagnostic"])

GRADES = {
    0: {"name": "No DR",            "uz": "Kasallik yo'q",      "description": "Ko'zda diabetik retinopatiya belgilari topilmadi."},
    1: {"name": "Mild DR",          "uz": "Yengil daraja",      "description": "Kichik mikroanevrizm mavjud. Darhol xavf yo'q."},
    2: {"name": "Moderate DR",      "uz": "O'rtacha daraja",    "description": "Qon tomirlari shikastlangan. Kuzatuv zarur."},
    3: {"name": "Severe DR",        "uz": "Og'ir daraja",       "description": "Ko'p qon tomirlari shikastlangan. Tezkor davolash kerak."},
    4: {"name": "Proliferative DR", "uz": "Proliferativ daraja","description": "Eng og'ir holat. Zudlik bilan ko'z shifokori ko'rigidan o'tish zarur."},
}


def _prediction_detail(r: PredictionRecord) -> dict:
    g = GRADES[r.diagnosis]
    return {
        "id": r.id,
        "filename": r.filename,
        "diagnosis": r.diagnosis,
        "grade_name": g["name"],
        "grade_uz": g["uz"],
        "description": g["description"],
        "confidence": round(r.confidence * 100, 2),
        "probabilities": {
            "0": round(r.prob_0 * 100, 2),
            "1": round(r.prob_1 * 100, 2),
            "2": round(r.prob_2 * 100, 2),
            "3": round(r.prob_3 * 100, 2),
            "4": round(r.prob_4 * 100, 2),
        },
        "created_at": r.created_at,
    }


@router.get("/grades", response_model=GradesResponse)
def get_grades():
    return {"grades": GRADES}


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(..., description="Retinal fundus rasmi (JPG/PNG)"),
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(status_code=400, detail="Faqat JPG yoki PNG rasm qabul qilinadi.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Rasm hajmi 10MB dan oshmasligi kerak.")

    diagnosis, confidence, probabilities = predict_image(image_bytes)

    record = PredictionRecord(
        patient_id=patient.id,
        filename=file.filename,
        diagnosis=diagnosis,
        confidence=confidence,
        prob_0=probabilities[0],
        prob_1=probabilities[1],
        prob_2=probabilities[2],
        prob_3=probabilities[3],
        prob_4=probabilities[4],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _prediction_detail(record)


@router.get("/predictions/me", response_model=list[HistoryResponse])
def my_predictions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    records = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.patient_id == patient.id)
        .order_by(PredictionRecord.created_at.desc())
        .offset(skip).limit(limit).all()
    )
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "diagnosis": r.diagnosis,
            "grade_name": GRADES[r.diagnosis]["name"],
            "grade_uz": GRADES[r.diagnosis]["uz"],
            "confidence": round(r.confidence * 100, 2),
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.get("/predictions/me/{record_id}", response_model=PredictionResponse)
def my_prediction_detail(
    record_id: int,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    record = db.query(PredictionRecord).filter(
        PredictionRecord.id == record_id,
        PredictionRecord.patient_id == patient.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Natija topilmadi.")
    return _prediction_detail(record)
