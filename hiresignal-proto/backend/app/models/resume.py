from sqlalchemy import Column, String, Float, Integer, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.sql import func
import uuid

from app.database import Base


class ResumeResult(Base):
    __tablename__ = "resume_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("screening_jobs.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_key = Column(String(500))
    content_hash = Column(String(100), nullable=False)
    
    extracted_text = Column(Text)
    extracted_text_length = Column(Integer)
    extraction_quality = Column(String(50), default="good", nullable=False)  # good, ocr_used, poor
    language_detected = Column(String(10), default="en")
    
    # 4 Signals
    score_semantic = Column(Float)
    score_tfidf = Column(Float)
    score_skills = Column(Float)
    score_experience = Column(Float)
    final_score = Column(Float)
    rank = Column(Integer)
    
    # Skills
    matched_skills = Column(ARRAY(String), default=list, nullable=False)
    missing_skills = Column(ARRAY(String), default=list, nullable=False)
    years_experience_detected = Column(Float)
    
    # Flags: stuffing, blank_resume, multilingual, duplicate_of, etc.
    flags = Column(JSONB, default={}, nullable=False)
    
    processing_ms = Column(Integer)
    status = Column(String(50), default="pending", nullable=False)  # pending, done, failed
    error_message = Column(Text)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
