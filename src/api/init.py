"""
API Module
~~~~~~~~~~

FastAPI routes and endpoints for the AI Code Reviewer.
"""

try:
    from src.api.server import app
    from src.api.routes import router
except ImportError:
    app = None
    router = None

__all__ = [
    "app",
    "router",
]
