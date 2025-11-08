from enum import Enum
from typing import List, Dict, Optional
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class Permission(Enum):
    CONFIGURE_BOT = "configure_bot"
    VIEW_REPORTS = "view_reports"
    APPROVE_REVIEWS = "approve_reviews"
    MANAGE_RULES = "manage_rules"
    VIEW_ANALYTICS = "view_analytics"

class RBACManager:
    """Role-Based Access Control for enterprise security"""
    
    def __init__(self):
        self.role_permissions = {
            Role.ADMIN: [
                Permission.CONFIGURE_BOT,
                Permission.VIEW_REPORTS,
                Permission.APPROVE_REVIEWS,
                Permission.MANAGE_RULES,
                Permission.VIEW_ANALYTICS
            ],
            Role.DEVELOPER: [
                Permission.VIEW_REPORTS,
                Permission.APPROVE_REVIEWS,
                Permission.VIEW_ANALYTICS
            ],
            Role.REVIEWER: [
                Permission.VIEW_REPORTS,
                Permission.APPROVE_REVIEWS
            ],
            Role.VIEWER: [
                Permission.VIEW_REPORTS
            ]
        }
        self.jwt_secret = self._get_jwt_secret()
    
    def _get_jwt_secret(self) -> str:
        """Get JWT secret from environment, raise error if not set"""
        secret = os.getenv('JWT_SECRET')
        if not secret:
            raise ValueError(
                "JWT_SECRET environment variable must be set. "
                "Generate a secure secret: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if len(secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return secret
    
    def create_token(self, user_id: str, role: Role, expires_in_hours: int = 24) -> str:
        """Create JWT token for user with expiration"""
        payload = {
            'user_id': user_id,
            'role': role.value,
            'permissions': [p.value for p in self.role_permissions[role]],
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        try:
            return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        except Exception as e:
            raise ValueError(f"Failed to create token: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def has_permission(self, token: str, required_permission: Permission) -> bool:
        """Check if user has required permission"""
        try:
            payload = self.verify_token(token)
            user_permissions = [Permission(p) for p in payload.get('permissions', [])]
            return required_permission in user_permissions
        except ValueError:
            return False
    
    def require_permission(self, permission: Permission):
        """Decorator to enforce permission on functions"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract token from kwargs or request context
                token = kwargs.get('token') or self._get_token_from_context()
                if not self.has_permission(token, permission):
                    raise PermissionError(f"Permission {permission.value} required")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _get_token_from_context(self) -> Optional[str]:
        """Get token from request context (Flask/FastAPI)"""
        # Implementation depends on your framework
        return None
