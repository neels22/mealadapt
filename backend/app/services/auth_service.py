import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
from jose import JWTError, jwt
from dotenv import load_dotenv

from app.models.user import UserCreate, User, Token, TokenData, TokenPair
from app.database import (
    create_user, get_user_by_email, get_user_by_id, update_user, delete_user,
    store_refresh_token, get_refresh_token, delete_refresh_token, 
    delete_user_refresh_tokens, blacklist_token, is_token_blacklisted
)

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable is required. Set a secure random key of at least 32 characters.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1  # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Longer-lived refresh tokens


class AuthService:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.access_token_expire = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        self.refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
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
    
    def create_access_token(self, user_id: str) -> Tuple[str, str]:
        """Create a JWT access token. Returns (token, jti)"""
        jti = str(uuid.uuid4())
        expire = datetime.utcnow() + self.access_token_expire
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "access"
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, jti
    
    async def create_refresh_token(self, user_id: str) -> Tuple[str, str]:
        """Create a JWT refresh token and store it in DB. Returns (token, jti)"""
        jti = str(uuid.uuid4())
        expire = datetime.utcnow() + self.refresh_token_expire
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in database
        await store_refresh_token(jti, user_id, expire.isoformat())
        
        return encoded_jwt, jti
    
    async def create_token_pair(self, user_id: str) -> dict:
        """Create both access and refresh tokens"""
        access_token, access_jti = self.create_access_token(user_id)
        refresh_token, refresh_jti = await self.create_refresh_token(user_id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_jti": access_jti,
            "refresh_jti": refresh_jti
        }
    
    def decode_token(self, token: str, expected_type: str = "access") -> Optional[TokenData]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            jti: str = payload.get("jti")
            token_type: str = payload.get("type", "access")
            
            if user_id is None:
                return None
            
            # Verify token type matches expected
            if token_type != expected_type:
                return None
            
            return TokenData(user_id=user_id, jti=jti, token_type=token_type)
        except JWTError:
            return None
    
    async def decode_and_validate_token(self, token: str, expected_type: str = "access") -> Optional[TokenData]:
        """Decode token and check if it's blacklisted"""
        token_data = self.decode_token(token, expected_type)
        if token_data is None:
            return None
        
        # Check if token is blacklisted
        if token_data.jti and await is_token_blacklisted(token_data.jti):
            return None
        
        return token_data
    
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
        
        # Generate token pair
        tokens = await self.create_token_pair(user_id)
        
        return {
            "user": User(id=user_id, email=user_data.email, name=user_data.name),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
    
    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user and return tokens if valid"""
        user = await get_user_by_email(email)
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        # Generate token pair
        tokens = await self.create_token_pair(user["id"])
        
        return {
            "user": User(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                created_at=user.get("created_at"),
                updated_at=user.get("updated_at")
            ),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from an access token"""
        token_data = await self.decode_and_validate_token(token, expected_type="access")
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
    
    async def refresh_tokens(self, refresh_token: str) -> Optional[dict]:
        """
        Refresh tokens using a valid refresh token.
        Implements token rotation - old refresh token is invalidated.
        """
        # Decode and validate the refresh token
        token_data = await self.decode_and_validate_token(refresh_token, expected_type="refresh")
        if token_data is None or token_data.user_id is None or token_data.jti is None:
            return None
        
        # Check if refresh token exists in database (not already used)
        stored_token = await get_refresh_token(token_data.jti)
        if stored_token is None:
            return None
        
        # Get user to ensure they still exist
        user = await get_user_by_id(token_data.user_id)
        if user is None:
            return None
        
        # Delete old refresh token (token rotation)
        await delete_refresh_token(token_data.jti)
        
        # Create new token pair
        tokens = await self.create_token_pair(token_data.user_id)
        
        return {
            "user": User(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                created_at=user.get("created_at"),
                updated_at=user.get("updated_at")
            ),
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
    
    async def revoke_tokens(self, access_token: str, user_id: str) -> bool:
        """
        Revoke tokens during logout.
        Blacklists the access token and removes all refresh tokens for the user.
        """
        # Decode access token to get JTI (don't validate blacklist since we're blacklisting it)
        token_data = self.decode_token(access_token, expected_type="access")
        
        if token_data and token_data.jti:
            # Get expiry from token for blacklist cleanup
            try:
                payload = jwt.decode(access_token, self.secret_key, algorithms=[self.algorithm])
                exp = payload.get("exp")
                if exp:
                    expire_dt = datetime.utcfromtimestamp(exp)
                    await blacklist_token(token_data.jti, "access", expire_dt.isoformat())
            except JWTError:
                pass
        
        # Delete all refresh tokens for this user
        await delete_user_refresh_tokens(user_id)
        
        return True
    
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
