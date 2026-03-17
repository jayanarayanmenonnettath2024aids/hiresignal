import os
import hashlib
from pathlib import Path
from app.config import settings


def sanitize_filename(filename: str) -> str:
    """Remove path separators and limit filename length"""
    # Remove any path separators
    filename = os.path.basename(filename)
    filename = filename.replace("\\", "").replace("/", "")
    # Limit to 100 chars
    return filename[:100]


def compute_hash(content: bytes) -> str:
    """Compute SHA256 hash of content, return first 16 chars"""
    return hashlib.sha256(content).hexdigest()[:16]


def ensure_upload_dir(tenant_id: str, job_id: str, subdir: str = "resumes") -> Path:
    """Ensure directory exists for uploads"""
    path = Path(settings.upload_dir) / str(tenant_id) / subdir / str(job_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_resume_path(tenant_id: str, job_id: str, content_hash: str, filename: str) -> Path:
    """Get full path for resume storage"""
    dir_path = ensure_upload_dir(tenant_id, job_id, "resumes")
    safe_filename = sanitize_filename(filename)
    return dir_path / f"{content_hash}_{safe_filename}"


def get_report_path(tenant_id: str, job_id: str, filename: str) -> Path:
    """Get full path for report storage"""
    dir_path = ensure_upload_dir(tenant_id, job_id, "reports")
    safe_filename = sanitize_filename(filename)
    return dir_path / safe_filename


def validate_key(key: str) -> bool:
    """Validate storage key for path traversal"""
    return ".." not in key and not key.startswith("/")
