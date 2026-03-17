"""
Export router: CSV and Excel export of screening results.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from app.database import get_db
from app.services import export_service, job_service, resume_service
from app.dependencies import get_current_tenant_id

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{job_id}/csv")
async def export_csv(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Export job results to CSV"""
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    results = await resume_service.get_results_by_job(db, job_id, 0, 10000)
    
    csv_content = await export_service.export_csv(db, job_id, results)
    
    filename = f"shortlist_{job.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{job_id}/excel")
async def export_excel(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_tenant_id: UUID = Depends(get_current_tenant_id)
):
    """Export job results to Excel"""
    job = await job_service.get_job(db, job_id)
    
    if not job or job.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    results = await resume_service.get_results_by_job(db, job_id, 0, 10000)
    
    excel_content = await export_service.export_excel(db, job_id, results)
    
    filename = f"shortlist_{job.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        iter([excel_content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
