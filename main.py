from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.database import Base, engine
from models import *
from middleware import RateLimitMiddleware
from routers import (
    diagnostic_router,
    chat_router,
    auth_router,
    superadmin_router,
    system_admin_router,
    clinic_admin_router,
    clinics_router,
    doctors_router,
    patients_router,
    anketa_router,
    dp_chat_router,
    nurses_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIDiagnostika API")

app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(superadmin_router)
app.include_router(system_admin_router)
app.include_router(clinic_admin_router)
app.include_router(clinics_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(chat_router)
app.include_router(anketa_router)
app.include_router(diagnostic_router)
app.include_router(dp_chat_router)
app.include_router(nurses_router)

import os
os.makedirs("uploads/chat", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7535, reload=True)
