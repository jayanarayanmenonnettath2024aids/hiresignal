from sqlalchemy import Column, String, Float, Integer, TIMESTAMP, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ScreeningJob(Base):
    __tablename__ = "screening_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    jd_text = Column(Text, nullable=False)
    jd_skills_extracted = Column(ARRAY(String), default=list, nullable=False)
    jd_quality_score = Column(Float)
    jd_is_vague = Column(Boolean, default=False, nullable=False)
    
    # Weights (sum to 1.0)
    weight_semantic = Column(Float, default=0.40, nullable=False)
    weight_tfidf = Column(Float, default=0.30, nullable=False)
    weight_skills = Column(Float, default=0.20, nullable=False)
    weight_experience = Column(Float, default=0.10, nullable=False)
    
    top_n = Column(Integer, default=10, nullable=False)
    total_submitted = Column(Integer, default=0, nullable=False)
    total_processed = Column(Integer, default=0, nullable=False)
    total_failed = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, done, failed
    
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
