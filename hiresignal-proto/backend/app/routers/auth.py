"""
Auth router: Login endpoint (POST), get current user (GET).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.services import auth_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    Returns JWT access token.
    """
    token, user_dict = await auth_service.login(db, request.email, request.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "role": current_user["role"]
    }
