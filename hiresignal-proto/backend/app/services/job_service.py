"""
JobService: CRUD operations for screening jobs and JD preprocessing.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models import ScreeningJob
from app.schemas import JobCreate, JobUpdate
from app.nlp import preprocess_jd


class JobService:
    """Manage screening jobs"""
    
    @staticmethod
    async def create_job(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        job_data: JobCreate
    ) -> ScreeningJob:
        """
        Create a new screening job.
        Preprocesses JD to extract skills, quality score, etc.
        """
        jd_info = preprocess_jd(job_data.jd_text)
        
        job = ScreeningJob(
            tenant_id=tenant_id,
            created_by=user_id,
            title=job_data.title,
            jd_text=job_data.jd_text,
            jd_skills_extracted=jd_info['required_skills'],
            jd_quality_score=jd_info['quality_score'],
            jd_is_vague=jd_info['is_vague'],
            weight_semantic=job_data.weight_semantic,
            weight_tfidf=job_data.weight_tfidf,
            weight_skills=job_data.weight_skills,
            weight_experience=job_data.weight_experience,
            top_n=job_data.top_n,
            status="pending"
        )
        
        db.add(job)
        await db.flush()
        await db.commit()
        await db.refresh(job)
        
        return job
    
    @staticmethod
    async def get_job(db: AsyncSession, job_id: UUID) -> Optional[ScreeningJob]:
        """Get job by ID"""
        stmt = select(ScreeningJob).where(ScreeningJob.id == job_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_jobs(db: AsyncSession, tenant_id: UUID) -> List[ScreeningJob]:
        """List all jobs for a tenant"""
        stmt = select(ScreeningJob).where(
            ScreeningJob.tenant_id == tenant_id
        ).order_by(ScreeningJob.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_job(
        db: AsyncSession,
        job_id: UUID,
        updates: dict
    ) -> Optional[ScreeningJob]:
        """Update job"""
        stmt = update(ScreeningJob).where(
            ScreeningJob.id == job_id
        ).values(**updates)
        
        await db.execute(stmt)
        await db.commit()
        
        return await JobService.get_job(db, job_id)
    
    @staticmethod
    async def set_job_processing(db: AsyncSession, job_id: UUID) -> None:
        """Mark job as processing"""
        await JobService.update_job(db, job_id, {
            'status': 'processing',
            'started_at': datetime.now(timezone.utc),
            'total_processed': 0,
            'total_failed': 0
        })
    
    @staticmethod
    async def set_job_done(db: AsyncSession, job_id: UUID) -> None:
        """Mark job as done"""
        await JobService.update_job(db, job_id, {
            'status': 'done',
            'completed_at': datetime.now(timezone.utc)
        })
    
    @staticmethod
    async def set_job_failed(db: AsyncSession, job_id: UUID, error_msg: str) -> None:
        """Mark job as failed"""
        await JobService.update_job(db, job_id, {
            'status': 'failed',
            'completed_at': datetime.now(timezone.utc)
        })
    
    @staticmethod
    async def increment_processed(db: AsyncSession, job_id: UUID, count: int = 1) -> None:
        """Increment processed count"""
        job = await JobService.get_job(db, job_id)
        if job:
            new_count = job.total_processed + count
            await JobService.update_job(db, job_id, {
                'total_processed': new_count
            })


job_service = JobService()
