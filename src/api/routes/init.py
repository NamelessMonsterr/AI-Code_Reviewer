"""
API Routes
~~~~~~~~~~

All API endpoint definitions.
"""

from fastapi import APIRouter

router = APIRouter()

try:
    from src.api.routes import health, review, webhooks
    
    # Include all route modules
    router.include_router(health.router, tags=["health"])
    router.include_router(review.router, prefix="/review", tags=["review"])
    router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
except ImportError:
    pass

__all__ = ["router"]