import json
import logging
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    """Comprehensive audit logging for enterprise compliance"""
    
    def __init__(self, log_file='audit.log'):
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup structured logging"""
        logger = logging.getLogger('audit')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_action(self, user_id: str, action: str, resource: str, 
                   details: Dict = None, result: str = 'success'):
        """Log user action for audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'result': result,
            'details': details or {},
            'ip_address': self._get_client_ip()
        }
        self.logger.info(json.dumps(audit_entry))
    
    def log_security_event(self, event_type: str, severity: str, details: Dict):
        """Log security-related events"""
        security_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        self.logger.warning(json.dumps(security_entry))
    
    def log_compliance_check(self, standard: str, result: str, violations: List):
        """Log compliance check results"""
        compliance_entry = {
            'timestamp': datetime.now().isoformat(),
            'standard': standard,
            'result': result,
            'violations_count': len(violations),
            'violations': violations
        }
        self.logger.info(json.dumps(compliance_entry))
    
    def _get_client_ip(self) -> str:
        """Get client IP address (placeholder)"""
        return "127.0.0.1"
    
    def query_logs(self, start_date: str = None, end_date: str = None, 
                   user_id: str = None) -> List[Dict]:
        """Query audit logs with filters"""
        results = []
        with open(self.log_file, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                
                # Apply filters
                if user_id and entry.get('user_id') != user_id:
                    continue
                if start_date and entry['timestamp'] < start_date:
                    continue
                if end_date and entry['timestamp'] > end_date:
                    continue
                
                results.append(entry)
        
        return results
