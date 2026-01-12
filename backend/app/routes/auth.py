"""
Authentication routes for user registration, login, and token management.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserCreate, UserLogin, UserUpdate, UserPasswordUpdate, User, RefreshTokenRequest
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_user_required
from app.database import get_session

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """Register a new user account and return access + refresh tokens"""
    try:
        result = await auth_service.register_user(session, user_data)
        return {
            "user": result["user"].model_dump(),
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": result["token_type"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=dict)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session)
):
    """Login with email and password, returns access + refresh tokens"""
    result = await auth_service.authenticate_user(
        session,
        email=credentials.email,
        password=credentials.password
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user": result["user"].model_dump(),
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": result["token_type"]
    }


@router.post("/refresh", response_model=dict)
async def refresh_tokens(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Get new access and refresh tokens using a valid refresh token.
    The old refresh token is invalidated (token rotation).
    """
    result = await auth_service.refresh_tokens(session, request.refresh_token)
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user": result["user"].model_dump(),
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": result["token_type"]
    }


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_session)
):
    """
    Logout the current user.
    Blacklists the access token and invalidates all refresh tokens.
    """
    access_token = credentials.credentials
    await auth_service.revoke_tokens(session, access_token, current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user_required)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=User)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_session)
):
    """Update current user profile"""
    try:
        updated_user = await auth_service.update_user_profile(
            session,
            user_id=current_user.id,
            name=update_data.name,
            email=update_data.email
        )
        
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me/password")
async def change_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_session)
):
    """Change current user's password"""
    try:
        success = await auth_service.change_password(
            session,
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user_required),
    session: AsyncSession = Depends(get_session)
):
    """Delete current user's account and all associated data"""
    success = await auth_service.delete_user_account(session, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    return {"message": "Account deleted successfully"}
