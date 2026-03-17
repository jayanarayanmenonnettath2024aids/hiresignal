"""
Main FastAPI application entry point.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Import routers
from app.routers import (
    auth_router,
    jobs_router,
    resumes_router,
    feedback_router,
    export_router,
    analytics_router,
    ws_router
)

# Import initialization
from app.database import Base, async_engine
import sqlalchemy


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """
    # Startup: create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database tables created")
    print("✓ HireSignal backend ready")
    
    yield
    
    # Shutdown
    print("\n✓ Shutting down HireSignal")


# Create FastAPI app
app = FastAPI(
    title="HireSignal Prototype",
    description="Offline resume screening platform with NLP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (configure in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(resumes_router)
app.include_router(feedback_router)
app.include_router(export_router)
app.include_router(analytics_router)
app.include_router(ws_router)


# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


# Serve uploaded files
@app.get("/api/files/{file_path:path}")
async def serve_file(file_path: str):
    """Serve files from uploads directory"""
    from app.utils import validate_key
    from app.config import settings
    
    if not validate_key(file_path):
        return {"error": "Invalid file path"}
    
    full_path = Path(settings.upload_dir) / file_path
    
    if not full_path.exists():
        return {"error": "File not found"}
    
    return FileResponse(full_path)


# Fallback to frontend (for SPA)
@app.get("/{full_path:path}")
async def catchall(full_path: str):
    """Serve frontend index.html for SPA routing"""
    frontend_index = Path("frontend/dist/index.html")
    if frontend_index.exists():
        return FileResponse(frontend_index)
    
    return {"message": "HireSignal API. Frontend not yet built."}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
