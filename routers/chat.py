import json
import anthropic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.chats import Message
from models.anketa import Anketa
from models.patients import Patient
from data.config import ANTHROPIC_API_KEY
from utils.auth import get_current_patient

router = APIRouter(prefix="/chat", tags=["chat"])
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Siz "AIDiagnostika" tibbiy platformasining AI yordamchisisiz.
Bemorlar bilan faqat O'ZBEK tilida muloqot qiling.

Vazifangiz: bemordan quyidagi ma'lumotlarni yig'ish (savolllarni birma-bir bering):
1. Ism va yosh
2. Asosiy shikoyat — ko'rish bilan bog'liq muammolar (loyqalik, dog'lar, parda, ko'rish yo'qolishi)
3. Belgilar qachondan boshlangan va qanday o'zgargan
4. Qand diabeti bor-yo'qligi va necha yildan beri
5. Qon shakarini nazorat holati (yaxshi / qiyin / dori bilan)
6. Ko'zda og'riq, qizarish, nur sezgirligining bor-yo'qligi
7. Oldingi ko'z muolajasi yoki operatsiyasi bo'lgan-bo'lmaganı
8. Hozir qabul qilayotgan dorilar (ko'z tomchilari ham)
9. Oilada ko'z kasalligi yoki diabetik retinopatiya bo'lgan-bo'lmaganı

Barcha javoblar olgandan so'ng: "Rahmat! Ma'lumotlaringiz to'plandi. Anketani yuborish uchun 'Yuborish' tugmasini bosing." deb xabar bering.
Boshqa mavzularga o'tmang. Samimiy va qisqa javob bering."""


@router.post("")
async def chat(
    message: str,
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    history = (
        db.query(Message)
        .filter(Message.patient_id == patient.id)
        .order_by(Message.created_at)
        .all()
    )

    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    ai_reply = response.content[0].text

    db.add(Message(patient_id=patient.id, role="user", content=message))
    db.add(Message(patient_id=patient.id, role="assistant", content=ai_reply))
    db.commit()

    return {"reply": ai_reply}


@router.post("/finalize", status_code=status.HTTP_201_CREATED)
async def finalize(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    history = (
        db.query(Message)
        .filter(Message.patient_id == patient.id)
        .order_by(Message.created_at)
        .all()
    )
    if not history:
        raise HTTPException(status_code=400, detail="Suhbat tarixi bo'sh. Avval doktor bilan gaplashing.")

    chat_text = "\n".join(
        f"{'Bemor' if m.role == 'user' else 'AI'}: {m.content}" for m in history
    )

    extraction_prompt = f"""Quyidagi tibbiy suhbat asosida bemorning ma'lumotlarini JSON formatda chiqar.

SUHBAT:
{chat_text}

Faqat quyidagi JSON strukturasini qaytar (boshqa matn bo'lmasin):
{{
  "ism_yosh": "...",
  "asosiy_shikoyat": "...",
  "belgilar_muddati": "...",
  "diabet": "bor/yo'q, necha yil",
  "qon_shakari_nazorati": "...",
  "qo'shimcha_belgilar": "...",
  "oldingi_muolaja": "...",
  "dorilar": "...",
  "oilaviy_tarix": "...",
  "xulosa": "Qisqa tibbiy xulosa"
}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": extraction_prompt}],
    )
    raw = response.content[0].text.strip()

    # JSON blokni tozalash (```json ... ``` bo'lsa)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        json.loads(raw)  # validatsiya
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI anketani to'g'ri formatlashda xato qildi.")

    anketa = Anketa(
        patient_id=patient.id,
        clinic_id=patient.clinic_id,
        content=raw,
        status="yangi",
    )
    db.add(anketa)
    db.commit()
    db.refresh(anketa)

    return {
        "anketa_id": anketa.id,
        "anketa": json.loads(raw),
        "message": "Anketa muvaffaqiyatli doktorga yuborildi.",
    }


@router.get("/history")
async def get_history(
    db: Session = Depends(get_db),
    patient: Patient = Depends(get_current_patient),
):
    messages = (
        db.query(Message)
        .filter(Message.patient_id == patient.id)
        .order_by(Message.created_at)
        .all()
    )
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]
