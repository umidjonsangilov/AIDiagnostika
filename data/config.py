from dotenv import load_dotenv
from os import getenv

load_dotenv()

DB_USER = getenv("DB_USER")
DB_PASS = getenv("DB_PASS")
DB_HOST = getenv("DB_HOST")
DB_NAME = getenv("DB_NAME")

ANTHROPIC_API_KEY = getenv("ANTHROPIC_API_KEY")

HF_TOKEN = getenv("HF_TOKEN")

JWT_SECRET = getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 1 kun

SUPERADMIN_TOKEN = getenv("SUPERADMIN_TOKEN", "change-me-superadmin-token")
