from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://hiresignal:password@localhost:5432/hiresignal"
    sync_database_url: str = "postgresql://hiresignal:password@localhost:5432/hiresignal"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 50
    max_resumes_per_job: int = 5000
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API
    api_base_url: str = "http://localhost:8000"
    frontend_base_url: str = "http://localhost:5173"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Environment
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
