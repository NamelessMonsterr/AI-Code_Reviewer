"""
Models Module
~~~~~~~~~~~~~

Database models and schemas.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

try:
    from src.models.user import User
    from src.models.repository import Repository
    from src.models.review import Review
    from src.models.comment import Comment
except ImportError:
    User = None
    Repository = None
    Review = None
    Comment = None

__all__ = [
    "Base",
    "User",
    "Repository",
    "Review",
    "Comment",
]
