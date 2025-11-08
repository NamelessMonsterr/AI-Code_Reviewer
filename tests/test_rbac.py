import pytest
import jwt
from datetime import datetime, timedelta
from src.auth.rbac import RBACManager, Role, Permission

class TestRBACManager:
    
    @pytest.fixture
    def rbac(self):
        """Create RBACManager instance"""
        return RBACManager()
    
    def test_create_token(self, rbac):
        """Test JWT token creation"""
        token = rbac.create_token('user_123', Role.ADMIN)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token contents
        payload = rbac.verify_token(token)
        assert payload['user_id'] == 'user_123'
        assert payload['role'] == 'admin'
    
    def test_token_expiration(self, rbac):
        """Test token expiration"""
        token = rbac.create_token('user_123', Role.ADMIN, expires_in_hours=0)
        
        with pytest.raises(ValueError, match="Token has expired"):
            rbac.verify_token(token)
    
    def test_invalid_token(self, rbac):
        """Test invalid token handling"""
        with pytest.raises(ValueError, match="Invalid token"):
            rbac.verify_token('invalid_token')
    
    def test_has_permission_admin(self, rbac):
        """Test admin has all permissions"""
        token = rbac.create_token('admin_user', Role.ADMIN)
        
        assert rbac.has_permission(token, Permission.CONFIGURE_BOT)
        assert rbac.has_permission(token, Permission.MANAGE_RULES)
        assert rbac.has_permission(token, Permission.VIEW_REPORTS)
    
    def test_has_permission_viewer(self, rbac):
        """Test viewer has limited permissions"""
        token = rbac.create_token('viewer_user', Role.VIEWER)
        
        assert rbac.has_permission(token, Permission.VIEW_REPORTS)
        assert not rbac.has_permission(token, Permission.CONFIGURE_BOT)
        assert not rbac.has_permission(token, Permission.MANAGE_RULES)
    
    def test_permission_decorator(self, rbac):
        """Test permission enforcement decorator"""
        
        @rbac.require_permission(Permission.CONFIGURE_BOT)
        def admin_function(token=None):
            return "success"
        
        # Admin token should work
        admin_token = rbac.create_token('admin', Role.ADMIN)
        result = admin_function(token=admin_token)
        assert result == "success"
        
        # Viewer token should fail
        viewer_token = rbac.create_token('viewer', Role.VIEWER)
        with pytest.raises(PermissionError):
            admin_function(token=viewer_token)
