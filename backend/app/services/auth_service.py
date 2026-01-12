import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from dotenv import load_dotenv

from app.models.user import UserCreate, User, Token, TokenData
from app.database import create_user, get_user_by_email, get_user_by_id, update_user, delete_user

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class AuthService:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        # Truncate to 72 bytes (bcrypt limit)
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    
    def hash_password(self, password: str) -> str:
        """Hash a password (truncated to 72 bytes for bcrypt)"""
        # Truncate to 72 bytes (bcrypt limit)
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token"""
        expire = datetime.utcnow() + self.access_token_expire
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return TokenData(user_id=user_id)
        except JWTError:
            return None
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        # Check if email already exists
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(user_data.password)
        
        user = await create_user(
            user_id=user_id,
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name
        )
        
        # Generate token
        access_token = self.create_access_token(user_id)
        
        return {
            "user": User(id=user_id, email=user_data.email, name=user_data.name),
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user and return token if valid"""
        user = await get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        # Generate token
        access_token = self.create_access_token(user["id"])
        
        return {
            "user": User(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                created_at=user.get("created_at"),
                updated_at=user.get("updated_at")
            ),
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token"""
        token_data = self.decode_token(token)
        if token_data is None or token_data.user_id is None:
            return None
        
        user = await get_user_by_id(token_data.user_id)
        if user is None:
            return None
        
        return User(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user.get("created_at"),
            updated_at=user.get("updated_at")
        )
    
    async def update_user_profile(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """Update user profile"""
        # If email is being changed, check it's not already taken
        if email:
            existing = await get_user_by_email(email)
            if existing and existing["id"] != user_id:
                raise ValueError("Email already in use")
        
        user = await update_user(user_id, name=name, email=email)
        if user is None:
            return None
        
        return User(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user.get("created_at"),
            updated_at=user.get("updated_at")
        )
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await get_user_by_id(user_id)
        if not user:
            return False
        
        if not self.verify_password(current_password, user["password_hash"]):
            raise ValueError("Current password is incorrect")
        
        new_hash = self.hash_password(new_password)
        await update_user(user_id, password_hash=new_hash)
        return True
    
    async def delete_user_account(self, user_id: str) -> bool:
        """Delete a user account"""
        return await delete_user(user_id)


# Singleton instance
auth_service = AuthService()
