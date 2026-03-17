"""
Dependencies: Dependency injection for FastAPI endpoints.
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import auth_service
from app.models import User, Tenant


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get current authenticated user from JWT token.
    Token must be in Authorization header: "Bearer <token>"
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    
    token = authorization[7:]  # Remove "Bearer "
    
    user = await auth_service.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user


async def get_current_user_id(
    current_user: dict = Depends(get_current_user)
) -> UUID:
    """Get current user ID"""
    return UUID(current_user["id"])


async def get_current_tenant_id(
    current_user: dict = Depends(get_current_user)
) -> UUID:
    """Get current user's tenant ID"""
    return UUID(current_user["tenant_id"])
