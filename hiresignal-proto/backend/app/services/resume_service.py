"""
ResumeService: CRUD and scoring for resume results.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from app.models import ResumeResult
from app.database import sync_engine
from app.nlp import (
    TextExtractor, AnomalyDetector, extract_skills, scorer
)


class ResumeService:
    """Manage resume processing and scoring"""
    
    @staticmethod
    async def create_result(
        db: AsyncSession,
        job_id: UUID,
        tenant_id: UUID,
        filename: str,
        content_hash: str,
        extracted_text: str,
        language: str,
        extraction_quality: str,
        flags: dict,
        is_ocr: bool = False,
        processing_ms: int = 0
    ) -> ResumeResult:
        """Create a resume result record"""
        result = ResumeResult(
            job_id=job_id,
            tenant_id=tenant_id,
            filename=filename,
            content_hash=content_hash,
            extracted_text=extracted_text,
            extracted_text_length=len(extracted_text),
            extraction_quality=extraction_quality,
            language_detected=language,
            status="pending",
            flags=flags,
            processing_ms=processing_ms
        )
        
        db.add(result)
        await db.flush()
        await db.commit()
        await db.refresh(result)
        
        return result
    
    @staticmethod
    async def update_result(
        db: AsyncSession,
        result_id: UUID,
        updates: dict
    ) -> Optional[ResumeResult]:
        """Update resume result"""
        stmt = update(ResumeResult).where(
            ResumeResult.id == result_id
        ).values(**updates)
        
        await db.execute(stmt)
        await db.commit()
        
        # Refresh
        stmt = select(ResumeResult).where(ResumeResult.id == result_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_result(db: AsyncSession, result_id: UUID) -> Optional[ResumeResult]:
        """Get result by ID"""
        stmt = select(ResumeResult).where(ResumeResult.id == result_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_results_by_job(
        db: AsyncSession,
        job_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[ResumeResult]:
        """Get ranked results for a job"""
        stmt = select(ResumeResult).where(
            ResumeResult.job_id == job_id,
            ResumeResult.status == "done"
        ).order_by(
            ResumeResult.final_score.desc(),
            ResumeResult.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def check_duplicate(
        db: AsyncSession,
        job_id: UUID,
        content_hash: str
    ) -> Optional[ResumeResult]:
        """Check if resume with same content hash already exists"""
        stmt = select(ResumeResult).where(
            ResumeResult.job_id == job_id,
            ResumeResult.content_hash == content_hash
        ).limit(1)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_ranks(db: AsyncSession, job_id: UUID) -> None:
        """Update rank column for all results in a job"""
        # Get all results for this job, ordered by score
        stmt = select(ResumeResult).where(
            ResumeResult.job_id == job_id,
            ResumeResult.status == "done"
        ).order_by(ResumeResult.final_score.desc())
        
        result = await db.execute(stmt)
        results = result.scalars().all()
        
        for rank, res in enumerate(results, start=1):
            await ResumeService.update_result(db, res.id, {'rank': rank})


resume_service = ResumeService()
