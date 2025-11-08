from enum import Enum
from typing import List, Dict
import jwt
import os

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
        self.jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key')
    
    def create_token(self, user_id: str, role: Role) -> str:
        """Create JWT token for user"""
        payload = {
            'user_id': user_id,
            'role': role.value,
            'permissions': [p.value for p in self.role_permissions[role]]
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None
    
    def has_permission(self, token: str, required_permission: Permission) -> bool:
        """Check if user has required permission"""
        payload = self.verify_token(token)
        if not payload:
            return False
        
        user_permissions = [Permission(p) for p in payload.get('permissions', [])]
        return required_permission in user_permissions
    
    def enforce_permission(self, token: str, permission: Permission):
        """Decorator to enforce permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.has_permission(token, permission):
                    raise PermissionError(f"Permission {permission.value} required")
                return func(*args, **kwargs)
            return wrapper
        return decorator
