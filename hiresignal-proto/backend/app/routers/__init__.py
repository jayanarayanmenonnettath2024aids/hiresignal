# Routers package
from app.routers.auth import router as auth_router
from app.routers.jobs import router as jobs_router
from app.routers.resumes import router as resumes_router
from app.routers.feedback import router as feedback_router
from app.routers.export import router as export_router
from app.routers.analytics import router as analytics_router
from app.routers.ws import router as ws_router

__all__ = [
    "auth_router", "jobs_router", "resumes_router",
    "feedback_router", "export_router", "analytics_router", "ws_router"
]
