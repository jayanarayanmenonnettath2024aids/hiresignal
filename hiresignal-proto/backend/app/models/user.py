from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="hr", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        __import__('sqlalchemy').UniqueConstraint('tenant_id', 'email', name='uq_tenant_email'),
    )
