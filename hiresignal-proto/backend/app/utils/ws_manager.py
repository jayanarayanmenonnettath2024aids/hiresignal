import asyncio
from typing import List, Dict, Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        """Add a WebSocket connection for a job"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    async def disconnect(self, job_id: str, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def broadcast(self, job_id: str, data: Dict[str, Any]):
        """Broadcast data to all connections for a job"""
        if job_id in self.active_connections:
            disconnected = []
            for ws in self.active_connections[job_id]:
                try:
                    await ws.send_json(data)
                except Exception as e:
                    # Connection lost
                    disconnected.append(ws)
            
            # Clean up disconnected connections
            for ws in disconnected:
                await self.disconnect(job_id, ws)


manager = ConnectionManager()
