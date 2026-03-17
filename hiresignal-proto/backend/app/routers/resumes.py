"""
Resumes router: Single-screen screening and resume file serving.
"""

import base64
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas import SingleScreenRequest, SingleScreenResponse
from app.services import storage_service
from app.dependencies import get_current_user, get_current_tenant_id
from app.workers.tasks.screening import process_single_resume

router = APIRouter(prefix="/api/screen", tags=["screening"])


@router.post("/single", response_model=SingleScreenResponse)
async def single_screen(
    jd_text: str = Form(...),
    resume_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Quick single-screen: upload resume and JD, get score in <3 seconds.
    Synchronous Celery task or direct computation.
    """
    resume_content = await resume_file.read()
    
    # Encode to base64 for Celery
    resume_b64 = base64.b64encode(resume_content).decode('utf-8')
    
    # Call Celery task (synchronous wait using apply())
    try:
        result = process_single_resume.apply(
            args=(jd_text, resume_b64, resume_file.filename),
            timeout=10  # 10 second timeout
        ).get(timeout=10)

        result.setdefault('filename', resume_file.filename or 'resume')
        result.setdefault('language_detected', 'en')
        result.setdefault('extraction_quality', 'good')
        result.setdefault('matched_skills', [])
        result.setdefault('missing_skills', [])
        result.setdefault('flags', {})
        result.setdefault('years_experience_detected', None)
        result.setdefault('processing_ms', None)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")
