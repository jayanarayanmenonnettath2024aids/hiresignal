"""
AuthService: Handle user authentication, password hashing, JWT token generation.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from sqlalchemy import select
from app.config import settings
from app.models import User, Tenant
from app.utils import hash_password, verify_password
from app.schemas import LoginRequest


class AuthService:
    """Handle user authentication"""
    
    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> Tuple[Optional[str], Optional[dict]]:
        """
        Authenticate user and return JWT token + user info.
        Returns: (token, user_dict) or (None, None) if auth fails.
        """
        # Find user by email
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            return None, None
        
        # Generate JWT token
        access_token = AuthService._create_access_token(user.id, user.tenant_id)
        
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": str(user.tenant_id)
        }
        
        return access_token, user_dict
    
    @staticmethod
    def _create_access_token(user_id, tenant_id, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.jwt_expiration_hours)
        
        now = datetime.now(timezone.utc)
        expire = now + expires_delta
        
        to_encode = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "exp": expire,
            "iat": now
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            user_id: str = payload.get("sub")
            tenant_id: str = payload.get("tenant_id")
            
            if user_id is None or tenant_id is None:
                return None
            
            return {"user_id": user_id, "tenant_id": tenant_id}
        except JWTError:
            return None
    
    @staticmethod
    async def get_current_user(db: AsyncSession, token: str) -> Optional[dict]:
        """Get current user from token"""
        token_data = AuthService.verify_token(token)
        if not token_data:
            return None
        
        stmt = select(User).where(User.id == token_data["user_id"])
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "tenant_id": str(user.tenant_id)
        }


auth_service = AuthService()
