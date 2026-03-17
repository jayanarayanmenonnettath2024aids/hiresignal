from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base


class HRFeedback(Base):
    __tablename__ = "hr_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("resume_results.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("screening_jobs.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    action = Column(String(50), nullable=False)  # shortlist, reject, etc.
    notes = Column(Text)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
