"""
Core Module
~~~~~~~~~~~

Core functionality including configuration, security, and logging.
"""

from src.core.config import settings

try:
    from src.core.security import auth_handler, AuthHandler
    from src.core.logging import setup_logging, get_logger
except ImportError:
    # Handle case where modules don't exist yet
    auth_handler = None
    AuthHandler = None
    setup_logging = None
    get_logger = None

__all__ = [
    "settings",
    "auth_handler",
    "AuthHandler",
    "setup_logging",
    "get_logger",
]
