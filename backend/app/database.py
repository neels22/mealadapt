"""
Database configuration and session management for PostgreSQL with SQLModel.
"""
import os
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Schema name for this project (separates from other projects in same DB)
SCHEMA_NAME = os.getenv("DB_SCHEMA", "mealadapt")

# Database URL from environment variable
# Format: postgresql+asyncpg://user:password@host:port/dbname
# Convert psycopg to asyncpg if needed
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mainmeal:mainmeal_secret@localhost:5432/mainmeal"
)

# Convert psycopg connection string to asyncpg if needed
if database_url.startswith("postgresql+psycopg://"):
    database_url = database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://")

DATABASE_URL = database_url

# Debug: Print connection info (without password) for troubleshooting
if os.getenv("DEBUG_DB", "false").lower() == "true":
    import re
    # Mask password in connection string for logging
    masked_url = re.sub(r':([^:@]+)@', r':****@', DATABASE_URL)
    print(f"🔍 Database URL: {masked_url}")
    print(f"🔍 Schema: {SCHEMA_NAME}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Log SQL queries if enabled
    future=True,
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """Initialize database - create schema and all tables"""
    # Import all models to register them with SQLModel
    from app.models.tables import (
        User, FamilyMember, HealthCondition, PantryItem,
        SavedRecipe, RecipeTag, ShoppingList, ShoppingItem,
        MealPlan, PlannedMeal, BarcodeCache, RefreshToken, BlacklistedToken
    )
    
    try:
        async with engine.begin() as conn:
            # Create schema if it doesn't exist (quoted to handle case sensitivity)
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}"'))
            await conn.commit()
        
        # Set the schema for SQLModel metadata
        SQLModel.metadata.schema = SCHEMA_NAME
        
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print(f"✅ Database schema '{SCHEMA_NAME}' and tables created successfully")
    except Exception as e:
        import re
        masked_url = re.sub(r':([^:@]+)@', r':****@', DATABASE_URL)
        print(f"❌ Database connection failed!")
        print(f"   Connection: {masked_url}")
        print(f"   Schema: {SCHEMA_NAME}")
        print(f"   Error: {str(e)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. If using Cloud SQL Proxy, make sure it's running:")
        print(f"      cloud-sql-proxy gen-lang-client-0515155454:us-central1:free-trial-first-project --port 5433")
        print(f"   2. Check if PostgreSQL/Cloud SQL Proxy is running on the specified host/port")
        print(f"   3. Verify your DATABASE_URL in .env file")
        print(f"   4. Check if the database '{DATABASE_URL.split('/')[-1]}' exists")
        print(f"   5. For Cloud SQL: Ensure your IP is whitelisted or use Cloud SQL Proxy")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.
    Use with FastAPI's Depends().
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections"""
    await engine.dispose()
