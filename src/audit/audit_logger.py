import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class AuditLogger:
    """Comprehensive audit logging for enterprise compliance"""

    def __init__(self, log_file: str = "audit.log", log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / log_file
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging with rotation"""
        logger = logging.getLogger("audit")
        logger.setLevel(logging.INFO)

        # File handler with rotation
        from logging.handlers import RotatingFileHandler

        handler = RotatingFileHandler(self.log_file, maxBytes=10485760, backupCount=5)  # 10MB
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def log_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Optional[Dict] = None,
        result: str = "success",
    ) -> None:
        """Log user action for audit trail"""
        try:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "result": result,
                "details": details or {},
                "ip_address": self._get_client_ip(),
            }
            self.logger.info(json.dumps(audit_entry))
        except Exception as e:
            self.logger.error(f"Failed to log action: {str(e)}")

    def log_security_event(self, event_type: str, severity: str, details: Dict) -> None:
        """Log security-related events"""
        try:
            security_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "details": details,
            }
            self.logger.warning(json.dumps(security_entry))
        except Exception as e:
            self.logger.error(f"Failed to log security event: {str(e)}")

    def log_compliance_check(self, standard: str, result: str, violations: List[Dict]) -> None:
        """Log compliance check results"""
        try:
            compliance_entry = {
                "timestamp": datetime.now().isoformat(),
                "standard": standard,
                "result": result,
                "violations_count": len(violations),
                "violations": violations,
            }
            self.logger.info(json.dumps(compliance_entry))
        except Exception as e:
            self.logger.error(f"Failed to log compliance check: {str(e)}")

    def _get_client_ip(self) -> str:
        """Get client IP address"""
        # Implementation depends on your framework (Flask, FastAPI, etc.)
        return "127.0.0.1"

    def query_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict]:
        """Query audit logs with filters"""
        results = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())

                    # Apply filters
                    if user_id and entry.get("user_id") != user_id:
                        continue
                    if start_date and entry["timestamp"] < start_date:
                        continue
                    if end_date and entry["timestamp"] > end_date:
                        continue

                    results.append(entry)
        except FileNotFoundError:
            self.logger.warning(f"Log file not found: {self.log_file}")
        except Exception as e:
            self.logger.error(f"Error querying logs: {str(e)}")

        return results
