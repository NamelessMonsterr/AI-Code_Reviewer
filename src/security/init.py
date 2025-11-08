"""
Security Module
~~~~~~~~~~~~~~~

Security utilities including rate limiting, authentication, and encryption.
"""

try:
    from src.security.rate_limiter import RateLimiter
    from src.security.authentication import authenticate_user, create_access_token
    from src.security.encryption import encrypt_data, decrypt_data
except ImportError:
    RateLimiter = None
    authenticate_user = None
    create_access_token = None
    encrypt_data = None
    decrypt_data = None

__all__ = [
    "RateLimiter",
    "authenticate_user",
    "create_access_token",
    "encrypt_data",
    "decrypt_data",
]
