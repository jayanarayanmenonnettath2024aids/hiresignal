"""
FeedbackService: Handle HR feedback (shortlist/reject).
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import HRFeedback
from app.schemas import FeedbackCreate


class FeedbackService:
    """Manage HR feedback"""
    
    @staticmethod
    async def create_feedback(
        db: AsyncSession,
        result_id: UUID,
        job_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        feedback_data: FeedbackCreate
    ) -> HRFeedback:
        """Create feedback record"""
        feedback = HRFeedback(
            result_id=result_id,
            job_id=job_id,
            tenant_id=tenant_id,
            user_id=user_id,
            action=feedback_data.action,
            notes=feedback_data.notes
        )
        
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        
        return feedback
    
    @staticmethod
    async def get_feedback_for_job(
        db: AsyncSession,
        job_id: UUID
    ) -> List[HRFeedback]:
        """Get all feedback for a job"""
        stmt = select(HRFeedback).where(
            HRFeedback.job_id == job_id
        ).order_by(HRFeedback.created_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_feedback_for_result(
        db: AsyncSession,
        result_id: UUID
    ) -> Optional[HRFeedback]:
        """Get feedback for a specific resume result"""
        stmt = select(HRFeedback).where(
            HRFeedback.result_id == result_id
        ).order_by(HRFeedback.created_at.desc()).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def count_feedback_by_action(db: AsyncSession, job_id: UUID) -> dict:
        """Count feedback by action for a job"""
        stmt = select(HRFeedback.action, func.count(HRFeedback.id)).where(
            HRFeedback.job_id == job_id
        ).group_by(HRFeedback.action)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        return {action: count for action, count in rows}


from sqlalchemy import func

feedback_service = FeedbackService()
