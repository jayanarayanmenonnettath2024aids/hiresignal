"""
StorageService: Local disk-based file storage for resumes and reports.
"""

import os
from pathlib import Path
from typing import List
from app.config import settings
from app.utils import sanitize_filename, compute_hash, ensure_upload_dir, get_resume_path, get_report_path, validate_key


class StorageService:
    """Handle resume and report file storage on local disk"""
    
    @staticmethod
    async def save_resume(tenant_id: str, job_id: str, filename: str, content: bytes) -> str:
        """
        Save resume to disk.
        Returns relative key: "{tenant_id}/resumes/{job_id}/{hash}_{filename}"
        """
        content_hash = compute_hash(content)
        safe_filename = sanitize_filename(filename)
        
        path = get_resume_path(tenant_id, job_id, content_hash, safe_filename)
        path.write_bytes(content)
        
        # Return relative key
        key = f"{tenant_id}/resumes/{job_id}/{content_hash}_{safe_filename}"
        return key
    
    @staticmethod
    async def get_resume(key: str) -> bytes:
        """Retrieve resume bytes from disk"""
        if not validate_key(key):
            raise ValueError("Invalid key")
        
        full_path = Path(settings.upload_dir) / key
        
        if not full_path.exists():
            raise FileNotFoundError(f"Resume not found: {key}")
        
        return full_path.read_bytes()
    
    @staticmethod
    async def list_resumes(tenant_id: str, job_id: str) -> List[str]:
        """List all resume keys for a job"""
        dir_path = ensure_upload_dir(tenant_id, job_id, "resumes")
        
        if not dir_path.exists():
            return []
        
        keys = []
        for file_path in dir_path.iterdir():
            if file_path.is_file():
                relative_key = str(file_path.relative_to(settings.upload_dir)).replace("\\", "/")
                keys.append(relative_key)
        
        return keys
    
    @staticmethod
    async def delete_resume(key: str) -> None:
        """Delete resume file"""
        if not validate_key(key):
            raise ValueError("Invalid key")
        
        full_path = Path(settings.upload_dir) / key
        
        if full_path.exists():
            full_path.unlink()
            
            # Clean up empty directories
            parent = full_path.parent
            try:
                if not any(parent.iterdir()):
                    parent.rmdir()
            except OSError:
                pass
    
    @staticmethod
    async def save_report(tenant_id: str, job_id: str, filename: str, content: bytes) -> str:
        """Save report (CSV/Excel) to disk"""
        safe_filename = sanitize_filename(filename)
        path = get_report_path(tenant_id, job_id, safe_filename)
        path.write_bytes(content)
        
        key = f"{tenant_id}/reports/{job_id}/{safe_filename}"
        return key
    
    @staticmethod
    async def get_report(key: str) -> bytes:
        """Retrieve report bytes from disk"""
        if not validate_key(key):
            raise ValueError("Invalid key")
        
        full_path = Path(settings.upload_dir) / key
        
        if not full_path.exists():
            raise FileNotFoundError(f"Report not found: {key}")
        
        return full_path.read_bytes()
    
    @staticmethod
    def get_file_url(key: str) -> str:
        """Get URL for file serving"""
        return f"/api/files/{key}"


storage_service = StorageService()
