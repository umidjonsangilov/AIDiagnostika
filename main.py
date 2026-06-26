from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import Base, engine
from models import *
from routers import (
    diagnostic_router,
    chat_router,
    auth_router,
    superadmin_router,
    clinic_admin_router,
    clinics_router,
    doctors_router,
    patients_router,
    anketa_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIDiagnostika API")

origins = [
    "http://localhost:5170",
    "http://localhost:5171",
    "http://localhost:5172",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179",
    "http://localhost:5180"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(superadmin_router)
app.include_router(clinic_admin_router)
app.include_router(clinics_router)
app.include_router(doctors_router)
app.include_router(patients_router)
app.include_router(chat_router)
app.include_router(anketa_router)
app.include_router(diagnostic_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
