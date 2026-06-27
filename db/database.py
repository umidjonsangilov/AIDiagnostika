from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from data.config import DB_USER, DB_PASS, DB_HOST, DB_NAME

database_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()