"""
Application configuration and environment variable validation.
Validates required environment variables at import time so
the app fails fast on startup rather than at first request.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _get_required(name: str) -> str:
    """Get a required environment variable or exit with a clear message."""
    value = os.getenv(name)
    if not value:
        print(f"ERROR: Required environment variable '{name}' is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def _get_optional(name: str, default: str = "") -> str:
    return os.getenv(name, default)


# Database
DATABASE_URL = _get_optional(
    "DATABASE_URL",
    "postgresql+asyncpg://mainmeal:mainmeal_secret@localhost:5432/mainmeal"
)
DB_SCHEMA = _get_optional("DB_SCHEMA", "mealadapt")

# AI Service
GEMINI_API_KEY = _get_optional("GEMINI_API_KEY", "")

# Auth
JWT_SECRET_KEY = _get_optional("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_ALGORITHM = _get_optional("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_optional("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(_get_optional("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# CORS
CORS_ORIGINS = [
    origin.strip()
    for origin in _get_optional("CORS_ORIGINS", "http://localhost:3000").split(",")
]

# Rate Limiting
DAILY_AI_CALL_LIMIT = int(_get_optional("DAILY_AI_CALL_LIMIT", "50"))

# Warnings for missing optional but recommended vars
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. AI features will fail at runtime.", file=sys.stderr)

if JWT_SECRET_KEY == "dev-secret-change-in-production":
    print("WARNING: Using default JWT secret. Set JWT_SECRET_KEY in production.", file=sys.stderr)
