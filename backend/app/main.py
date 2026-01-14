"""
MainMeal API - AI-powered recipe adaptation for family dietary needs.
FastAPI application with PostgreSQL backend using SQLModel.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes import family, recipe, scan, pantry, auth, saved_recipes, shopping, meal_plan, barcode, rate_limit
from app.database import init_db, close_db
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.request_size import RequestSizeLimitMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: Close database connections
    await close_db()


app = FastAPI(
    title="MainMeal API",
    description="AI-powered recipe adaptation for family dietary needs",
    version="1.0.0",
    lifespan=lifespan
)

# Error Handler Middleware (must be first to catch all errors)
app.add_middleware(ErrorHandlerMiddleware)

# Request Size Limit Middleware
app.add_middleware(RequestSizeLimitMiddleware, max_size=10 * 1024 * 1024)  # 10MB

# Security Headers Middleware (must be added before CORS)
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
# Strip whitespace from origins
origins = [origin.strip() for origin in origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Range", "X-Total-Count"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(family.router, prefix="/api/family", tags=["Family"])
app.include_router(recipe.router, prefix="/api/recipe", tags=["Recipe"])
app.include_router(saved_recipes.router, prefix="/api/recipes", tags=["Saved Recipes"])
app.include_router(shopping.router, prefix="/api/shopping", tags=["Shopping"])
app.include_router(meal_plan.router, prefix="/api/meal-plans", tags=["Meal Plans"])
app.include_router(barcode.router, prefix="/api/barcode", tags=["Barcode"])
app.include_router(scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(pantry.router, prefix="/api/pantry", tags=["Pantry"])
app.include_router(rate_limit.router, prefix="/api/rate-limits", tags=["Rate Limits"])


@app.get("/")
async def root():
    return {"message": "MainMeal API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
