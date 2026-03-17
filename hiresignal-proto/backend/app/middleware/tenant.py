"""
Tenant middleware: Simple header-based tenant isolation (no RLS).
"""

from fastapi import Request
from uuid import UUID


class TenantMiddleware:
    """Extract tenant_id from authenticated user (already in JWT payload)"""
    
    async def __call__(self, request: Request, call_next):
        # Tenant ID is already extracted from JWT in dependencies
        # This is a placeholder for any future tenant-level middleware
        response = await call_next(request)
        return response
