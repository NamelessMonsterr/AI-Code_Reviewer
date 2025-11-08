import pytest
import json
from src.audit.audit_logger import AuditLogger

class TestAuditLogger:
    
    @pytest.fixture
    def logger(self, test_data_dir):
        """Create AuditLogger instance"""
        return AuditLogger(
            log_file='test_audit.log',
            log_dir=str(test_data_dir)
        )
    
    def test_log_action(self, logger):
        """Test logging user action"""
        logger.log_action(
            user_id='user_123',
            action='code_review',
            resource='/repo/file.py',
            result='success'
        )
        
        # Verify log entry
        logs = logger.query_logs()
        assert len(logs) == 1
        assert logs[0]['user_id'] == 'user_123'
        assert logs[0]['action'] == 'code_review'
    
    def test_log_security_event(self, logger):
        """Test logging security event"""
        logger.log_security_event(
            event_type='unauthorized_access',
            severity='high',
            details={'ip': '192.168.1.1'}
        )
        
        logs = logger.query_logs()
        assert len(logs) == 1
        assert logs[0]['event_type'] == 'unauthorized_access'
    
    def test_log_compliance_check(self, logger):
        """Test logging compliance check"""
        violations = [
            {'type': 'data_leak', 'severity': 'critical'},
            {'type': 'missing_encryption', 'severity': 'high'}
        ]
        
        logger.log_compliance_check(
            standard='SOC2',
            result='FAILED',
            violations=violations
        )
        
        logs = logger.query_logs()
        assert len(logs) == 1
        assert logs[0]['standard'] == 'SOC2'
        assert logs[0]['violations_count'] == 2
    
    def test_query_logs_by_user(self, logger):
        """Test querying logs by user ID"""
        logger.log_action('user_1', 'action_1', 'resource_1')
        logger.log_action('user_2', 'action_2', 'resource_2')
        logger.log_action('user_1', 'action_3', 'resource_3')
        
        user_1_logs = logger.query_logs(user_id='user_1')
        assert len(user_1_logs) == 2
