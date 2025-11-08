"""
Schemas Module
~~~~~~~~~~~~~~

Pydantic models for request/response validation.
"""

try:
    from src.schemas.user import UserCreate, UserResponse, UserUpdate
    from src.schemas.review import ReviewRequest, ReviewResponse
    from src.schemas.repository import RepositoryCreate, RepositoryResponse
except ImportError:
    UserCreate = None
    UserResponse = None
    UserUpdate = None
    ReviewRequest = None
    ReviewResponse = None
    RepositoryCreate = None
    RepositoryResponse = None

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "ReviewRequest",
    "ReviewResponse",
    "RepositoryCreate",
    "RepositoryResponse",
]