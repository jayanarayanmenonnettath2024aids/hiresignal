"""
Feedback router: HR feedback (shortlist, reject).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas import FeedbackCreate, FeedbackResponse
from app.services import feedback_service, resume_service
from app.dependencies import get_current_user, get_current_tenant_id, get_current_user_id

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_tenant_id: UUID = Depends(get_current_tenant_id),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Submit HR feedback on a resume (shortlist, reject, etc).
    """
    # Verify the resume result belongs to this tenant
    result = await resume_service.get_result(db, feedback_data.result_id)
    
    if not result or result.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Result not found")
    
    feedback = await feedback_service.create_feedback(
        db,
        feedback_data.result_id,
        result.job_id,
        current_tenant_id,
        current_user_id,
        feedback_data
    )
    
    return {
        "id": str(feedback.id),
        "result_id": str(feedback.result_id),
        "action": feedback.action,
        "notes": feedback.notes
    }


@router.get("/job/{job_id}")
async def get_job_feedback(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get all feedback for a job"""
    from app.services import job_service
    
    job = await job_service.get_job(db, job_id)
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    feedbacks = await feedback_service.get_feedback_for_job(db, job_id)
    
    return [
        {
            "id": str(f.id),
            "result_id": str(f.result_id),
            "action": f.action,
            "notes": f.notes,
            "created_at": f.created_at.isoformat()
        }
        for f in feedbacks
    ]
