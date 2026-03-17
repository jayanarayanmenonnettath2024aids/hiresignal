from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(String(50), default="starter", nullable=False)
    monthly_quota = Column(Integer, default=500, nullable=False)
    used_this_month = Column(Integer, default=0, nullable=False)
    settings = Column(JSONB, default={}, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
