"""
WebSocket router: Live progress updates for screening jobs.
"""
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import asyncio
import json
import redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from uuid import UUID
from app.utils import manager
from app.config import settings
from app.dependencies import get_current_tenant_id

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(
    websocket: WebSocket,
    job_id: UUID,
    current_tenant_id: UUID = Query(...)  # Note: WebSocket doesn't use Depends easily
):
    """
    WebSocket connection for live screening job progress.
    Publishes: {processed, total, status, latest_result}
    """
    await manager.connect(str(job_id), websocket)
    
    redis_client = redis.from_url(settings.redis_url)
    pubsub = redis_client.pubsub()
    channel = f'job:{job_id}:progress'
    pubsub.subscribe(channel)
    
    try:
        # Send initial state
        from app.database import AsyncSessionLocal
        from app.services import job_service
        
        async with AsyncSessionLocal() as db:
            job = await job_service.get_job(db, job_id)
            if job and job.tenant_id == current_tenant_id:
                initial_data = {
                    "processed": job.total_processed,
                    "total": job.total_submitted,
                    "status": job.status
                }
                await websocket.send_json(initial_data)
        
        # Listen for updates
        async def listen_redis():
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        await websocket.send_json(data)
                    except:
                        pass
                await asyncio.sleep(0.1)
        
        # Keep connection alive
        async def keep_alive():
            while True:
                await asyncio.sleep(30)
                try:
                    await websocket.send_json({"ping": True})
                except:
                    break
        
        # Run both concurrently
        await asyncio.gather(listen_redis(), keep_alive())
    
    except WebSocketDisconnect:
        await manager.disconnect(str(job_id), websocket)
    
    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()
        redis_client.close()
