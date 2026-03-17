"""
Jobs router: CRUD for screening jobs, JD upload, job preview.
"""

import zipfile
import io
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.database import get_db
from app.schemas import JobCreate, JobResponse, JDPreviewResponse
from app.services import job_service, storage_service
from app.dependencies import get_current_user, get_current_tenant_id, get_current_user_id
from app.nlp import preprocess_jd
from app.workers.tasks.screening import process_screening_job
from app.config import settings

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
ALLOWED_MIMES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "application/zip",
    "application/x-zip-compressed",
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


def validate_upload_file(filename: str, content_type: str, size: int) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS and ext != ".zip":
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed: '{ext}'. Allowed: pdf, docx, doc, txt, zip",
        )

    mime = (content_type or "").split(";")[0].strip().lower()
    if mime and mime not in ALLOWED_MIMES:
        dangerous = {
            "application/x-sh",
            "application/x-shellscript",
            "text/x-shellscript",
            "application/x-executable",
            "application/x-msdownload",
            "application/x-bat",
            "application/octet-stream",
        }
        if mime in dangerous:
            raise HTTPException(status_code=400, detail=f"File type not allowed: {mime}")

    if size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size / (1024 * 1024):.1f}MB. Max 20MB per file.",
        )


@router.post("", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    current_tenant_id: UUID = Depends(get_current_tenant_id),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """Create a new screening job with JD"""
    job = await job_service.create_job(db, current_tenant_id, current_user_id, job_data)
    
    return {
        "id": str(job.id),
        "title": job.title,
        "jd_quality_score": job.jd_quality_score,
        "jd_is_vague": job.jd_is_vague,
        "status": job.status,
        "total_submitted": job.total_submitted,
        "total_processed": job.total_processed,
        "total_failed": job.total_failed,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "created_at": job.created_at.isoformat()
    }


@router.get("", response_model=list)
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """List all screening jobs for current tenant"""
    jobs = await job_service.list_jobs(db, current_tenant_id)
    
    return [
        {
            "id": str(job.id),
            "title": job.title,
            "jd_quality_score": job.jd_quality_score,
            "jd_is_vague": job.jd_is_vague,
            "status": job.status,
            "total_submitted": job.total_submitted,
            "total_processed": job.total_processed,
            "total_failed": job.total_failed,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "created_at": job.created_at.isoformat()
        }
        for job in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get specific job details"""
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job.id),
        "title": job.title,
        "jd_quality_score": job.jd_quality_score,
        "jd_is_vague": job.jd_is_vague,
        "status": job.status,
        "total_submitted": job.total_submitted,
        "total_processed": job.total_processed,
        "total_failed": job.total_failed,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "created_at": job.created_at.isoformat()
    }


@router.post("/preview-jd", response_model=JDPreviewResponse)
async def preview_jd(jd_text: str = Form(...)):
    """
    Preview JD: extract skills, compute quality score.
    Used for live preview while typing in job creation form.
    """
    jd_info = preprocess_jd(jd_text)
    
    return {
        "skills": jd_info['required_skills'],
        "quality_score": jd_info['quality_score'],
        "is_vague": jd_info['is_vague'],
        "min_yoe": jd_info['min_yoe']
    }


@router.post("/{job_id}/upload")
async def upload_resumes(
    job_id: UUID,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """
    Upload resumesfor screening job.
    Supports PDF, DOCX, TXT, ZIP (will be extracted).
    """
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    uploaded_files = []
    skipped_files = []
    
    for file in files:
        content = await file.read()

        validate_upload_file(
            filename=file.filename or "",
            content_type=file.content_type or "",
            size=len(content),
        )
        
        # Check file size
        if len(content) > settings.max_file_size_mb * 1024 * 1024:
            skipped_files.append(f"{file.filename} (too large)")
            continue
        
        filename_lower = file.filename.lower()
        
        # Handle ZIP
        if filename_lower.endswith('.zip'):
            try:
                zip_file = zipfile.ZipFile(io.BytesIO(content))
                for member in zip_file.namelist():
                    # Skip OSX junk
                    if '__MACOSX' in member or member.startswith('.'):
                        continue

                    member_name = Path(member).name
                    if not member_name:
                        continue
                    
                    # Only resume files
                    if Path(member_name).suffix.lower() not in ALLOWED_EXTENSIONS:
                        continue
                    
                    member_content = zip_file.read(member)
                    try:
                        validate_upload_file(member_name, "", len(member_content))
                    except HTTPException:
                        skipped_files.append(f"{member_name} (invalid member)")
                        continue

                    if len(member_content) > settings.max_file_size_mb * 1024 * 1024:
                        skipped_files.append(f"{member} (too large)")
                        continue
                    
                    # Save resume
                    key = await storage_service.save_resume(
                        str(current_tenant_id),
                        str(job_id),
                        member_name,
                        member_content
                    )
                    uploaded_files.append(key)
            except Exception as e:
                skipped_files.append(f"{file.filename} (invalid ZIP: {str(e)})")
        
        else:
            # Single file
            key = await storage_service.save_resume(
                str(current_tenant_id),
                str(job_id),
                file.filename,
                content
            )
            uploaded_files.append(key)
    
    # Update job total_submitted from files currently on disk for this job.
    # This avoids per-request overwrites when files are uploaded in multiple calls.
    upload_dir = Path(settings.upload_dir) / str(current_tenant_id) / "resumes" / str(job_id)
    if upload_dir.exists():
        job.total_submitted = sum(1 for p in upload_dir.iterdir() if p.is_file())
    else:
        job.total_submitted = 0

    if uploaded_files:
        job.status = 'pending'
        job.completed_at = None

    await db.commit()
    
    # Start async processing if we have files
    if uploaded_files:
        # Trigger Celery task
        process_screening_job.delay(str(job_id))
    
    return {
        "uploaded": len(uploaded_files),
        "skipped": len(skipped_files),
        "files": uploaded_files,
        "skipped_details": skipped_files
    }


@router.get("/{job_id}/results")
async def get_results(
    job_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get ranked results for a job"""
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from app.services import resume_service
    results = await resume_service.get_results_by_job(db, job_id, skip, limit)
    
    return [
        {
            "id": str(r.id),
            "filename": r.filename,
            "final_score": r.final_score,
            "score_semantic": r.score_semantic,
            "score_tfidf": r.score_tfidf,
            "score_skills": r.score_skills,
            "score_experience": r.score_experience,
            "rank": r.rank,
            "matched_skills": r.matched_skills,
            "missing_skills": r.missing_skills,
            "years_experience_detected": r.years_experience_detected,
            "language_detected": r.language_detected,
            "extraction_quality": r.extraction_quality,
            "flags": r.flags,
            "created_at": r.created_at.isoformat()
        }
        for r in results
    ]


@router.get("/{job_id}/summary")
async def get_job_summary(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get summary stats for a job"""
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get results
    from app.services import resume_service, feedback_service
    results = await resume_service.get_results_by_job(db, job_id, 0, 10000)
    feedback_counts = await feedback_service.count_feedback_by_action(db, job_id)
    
    scores = [r.final_score for r in results if r.final_score]
    
    return {
        "job_id": str(job.id),
        "title": job.title,
        "status": job.status,
        "total_submitted": job.total_submitted,
        "total_processed": job.total_processed,
        "total_failed": job.total_failed,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "shortlisted": feedback_counts.get('shortlist', 0),
        "rejected": feedback_counts.get('reject', 0)
    }
