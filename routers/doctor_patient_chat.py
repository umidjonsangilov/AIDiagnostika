import os
import uuid
from typing import Dict, List

from fastapi import (
    APIRouter, Depends, HTTPException, Query,
    UploadFile, File, WebSocket, WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models.doctor_patient_chat import DoctorPatientMessage
from models.doctors import Doctor
from models.patients import Patient
from data.config import JWT_SECRET, JWT_ALGORITHM
from utils.auth import get_current_doctor, get_current_patient

router = APIRouter(prefix="/dp-chat", tags=["doctor-patient-chat"])

UPLOAD_DIR = "uploads/chat"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# In-memory connection manager
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        # room_id -> list of {"ws": WebSocket, "sender_type": str}
        self.rooms: Dict[str, List[dict]] = {}

    @staticmethod
    def room_id(doctor_id: int, patient_id: int) -> str:
        return f"{doctor_id}_{patient_id}"

    async def connect(self, ws: WebSocket, room: str, sender_type: str) -> None:
        await ws.accept()
        self.rooms.setdefault(room, []).append({"ws": ws, "sender_type": sender_type})

    def disconnect(self, ws: WebSocket, room: str) -> None:
        if room in self.rooms:
            self.rooms[room] = [c for c in self.rooms[room] if c["ws"] is not ws]
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast(self, room: str, payload: dict) -> None:
        for conn in self.rooms.get(room, []):
            await conn["ws"].send_json(payload)


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# JWT helpers for WebSocket (token via query param)
# ---------------------------------------------------------------------------

def _ws_decode(token: str, expected_role: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None
    return payload if payload.get("role") == expected_role else None


# ---------------------------------------------------------------------------
# HTTP: image upload
# ---------------------------------------------------------------------------

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    token: str = Query(..., description="Doctor yoki patient JWT tokeni"),
):
    """Rasm yuklash. Doctor yoki patient token bilan foydalanishi mumkin."""
    payload = _ws_decode(token, "doctor") or _ws_decode(token, "patient")
    if not payload:
        raise HTTPException(status_code=401, detail="Token noto'g'ri")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Faqat rasm fayllar ruxsat etiladi (jpeg/png/gif/webp)")

    data = await file.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Rasm hajmi 10 MB dan oshmasligi kerak")

    ext = os.path.splitext(file.filename or "img.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(data)

    return {"image_url": f"/uploads/chat/{filename}"}


# ---------------------------------------------------------------------------
# HTTP: chat history
# ---------------------------------------------------------------------------

def _format(m: DoctorPatientMessage) -> dict:
    return {
        "id": m.id,
        "sender_type": m.sender_type,
        "message_type": m.message_type,
        "content": m.content,
        "image_url": m.image_url,
        "created_at": m.created_at,
    }


@router.get("/history/{patient_id}")
def doctor_history(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor: Doctor = Depends(get_current_doctor),
):
    """Doctor: bemorning chat tarixi."""
    msgs = (
        db.query(DoctorPatientMessage)
        .filter(
            DoctorPatientMessage.doctor_id == doctor.id,
            DoctorPatientMessage.patient_id == patient_id,
        )
        .order_by(DoctorPatientMessage.created_at)
        .all()
    )
    return [_format(m) for m in msgs]


@router.get("/history")
def patient_history(
    doctor_id: int = Query(...),
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    """Bemor: o'zining doktori bilan chat tarixi."""
    msgs = (
        db.query(DoctorPatientMessage)
        .filter(
            DoctorPatientMessage.doctor_id == doctor_id,
            DoctorPatientMessage.patient_id == patient.id,
        )
        .order_by(DoctorPatientMessage.created_at)
        .all()
    )
    return [_format(m) for m in msgs]


# ---------------------------------------------------------------------------
# WebSocket: doctor side  →  ws /dp-chat/ws/doctor/{patient_id}?token=...
# ---------------------------------------------------------------------------

@router.websocket("/ws/doctor/{patient_id}")
async def doctor_ws(
    websocket: WebSocket,
    patient_id: int,
    token: str = Query(...),
):
    payload = _ws_decode(token, "doctor")
    if not payload:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        doctor = db.query(Doctor).filter(Doctor.id == payload["sub"]).first()
        if not doctor:
            await websocket.close(code=4001)
            return

        room = manager.room_id(doctor.id, patient_id)
        await manager.connect(websocket, room, "doctor")

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "text")

                content   = data.get("content")   if msg_type == "text"  else None
                image_url = data.get("image_url") if msg_type == "image" else None

                if msg_type == "text" and not content:
                    continue
                if msg_type == "image" and not image_url:
                    continue

                msg = DoctorPatientMessage(
                    doctor_id=doctor.id,
                    patient_id=patient_id,
                    sender_type="doctor",
                    message_type=msg_type,
                    content=content,
                    image_url=image_url,
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)

                await manager.broadcast(room, _format(msg) | {"created_at": str(msg.created_at)})

        except WebSocketDisconnect:
            manager.disconnect(websocket, room)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# WebSocket: patient side  →  ws /dp-chat/ws/patient/{doctor_id}?token=...
# ---------------------------------------------------------------------------

@router.websocket("/ws/patient/{doctor_id}")
async def patient_ws(
    websocket: WebSocket,
    doctor_id: int,
    token: str = Query(...),
):
    payload = _ws_decode(token, "patient")
    if not payload:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.id == payload["sub"]).first()
        if not patient:
            await websocket.close(code=4001)
            return

        room = manager.room_id(doctor_id, patient.id)
        await manager.connect(websocket, room, "patient")

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "text")

                content   = data.get("content")   if msg_type == "text"  else None
                image_url = data.get("image_url") if msg_type == "image" else None

                if msg_type == "text" and not content:
                    continue
                if msg_type == "image" and not image_url:
                    continue

                msg = DoctorPatientMessage(
                    doctor_id=doctor_id,
                    patient_id=patient.id,
                    sender_type="patient",
                    message_type=msg_type,
                    content=content,
                    image_url=image_url,
                )
                db.add(msg)
                db.commit()
                db.refresh(msg)

                await manager.broadcast(room, _format(msg) | {"created_at": str(msg.created_at)})

        except WebSocketDisconnect:
            manager.disconnect(websocket, room)
    finally:
        db.close()
