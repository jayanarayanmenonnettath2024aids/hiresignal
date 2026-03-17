"""
Analytics router: Summary stats and charts for dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import func, select
from app.database import get_db
from app.models import ResumeResult, ScreeningJob
from app.services import job_service, resume_service
from app.dependencies import get_current_tenant_id

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get overview stats"""
    # Get all jobs for tenant
    stmt = select(ScreeningJob).where(ScreeningJob.tenant_id == current_tenant_id)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    total_jobs = len(jobs)
    total_processed = sum(j.total_processed for j in jobs)
    avg_score = 0
    
    # Get all results
    stmt = select(ResumeResult).where(
        ResumeResult.tenant_id == current_tenant_id,
        ResumeResult.status == 'done'
    )
    result = await db.execute(stmt)
    all_results = result.scalars().all()
    
    scores = [r.final_score for r in all_results if r.final_score]
    if scores:
        avg_score = sum(scores) / len(scores)
    
    return {
        "total_jobs": total_jobs,
        "total_resumes_screened": total_processed,
        "avg_match_score": round(avg_score, 3),
        "quota_used_this_month": 0  # Simplified
    }


@router.get("/score-trend")
async def get_score_trend(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get score trend over time"""
    # Simplified: return last N results
    stmt = select(ResumeResult).where(
        ResumeResult.tenant_id == current_tenant_id,
        ResumeResult.status == 'done'
    ).order_by(ResumeResult.created_at.desc()).limit(100)
    
    result = await db.execute(stmt)
    results = result.scalars().all()
    
    return [
        {
            "date": r.created_at.isoformat(),
            "score": r.final_score
        }
        for r in reversed(results)
    ]


@router.get("/skills")
async def get_skill_stats(
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Get matched and missing skills stats"""
    stmt = select(ResumeResult).where(
        ResumeResult.tenant_id == current_tenant_id,
        ResumeResult.status == 'done'
    )
    
    result = await db.execute(stmt)
    results = result.scalars().all()
    
    matched_skills = {}
    missing_skills = {}
    
    for r in results:
        for skill in r.matched_skills:
            matched_skills[skill] = matched_skills.get(skill, 0) + 1
        for skill in r.missing_skills:
            missing_skills[skill] = missing_skills.get(skill, 0) + 1
    
    # Top 10
    top_matched = sorted(matched_skills.items(), key=lambda x: x[1], reverse=True)[:10]
    top_missing = sorted(missing_skills.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "top_matched_skills": [{"skill": s, "count": c} for s, c in top_matched],
        "top_missing_skills": [{"skill": s, "count": c} for s, c in top_missing]
    }
