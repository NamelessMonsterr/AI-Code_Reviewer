import os
from compliance.compliance_checker import ComplianceChecker
from auth.rbac import RBACManager, Role, Permission
from audit.audit_logger import AuditLogger
from api.analytics_api import AnalyticsAPI


class EnhancedReviewPhase3:
    """Phase 3 enterprise-grade review system"""

    def __init__(self, user_id: str, user_role: Role):
        self.user_id = user_id
        self.rbac = RBACManager()
        self.audit_logger = AuditLogger()
        self.compliance_checker = ComplianceChecker()

        # Create user token
        self.token = self.rbac.create_token(user_id, user_role)

    def run_enterprise_review(
        self, code: str, file_path: str, compliance_standards: List[str]
    ) -> Dict:
        """Run enterprise review with compliance and audit"""

        # Log review action
        self.audit_logger.log_action(
            user_id=self.user_id,
            action="run_review",
            resource=file_path,
            details={"standards": compliance_standards},
        )

        # Check permissions
        if not self.rbac.has_permission(self.token, Permission.APPROVE_REVIEWS):
            raise PermissionError("User does not have review permissions")

        # Run compliance checks
        compliance_result = self.compliance_checker.run_all_compliance_checks(
            code, file_path, compliance_standards
        )

        # Log compliance check
        self.audit_logger.log_compliance_check(
            standard=",".join(compliance_standards),
            result=compliance_result["compliance_status"],
            violations=compliance_result["violations"],
        )

        # Generate report
        report = self.compliance_checker.generate_compliance_report(compliance_result["violations"])

        return {"compliance": compliance_result, "report": report, "audit_logged": True}


if __name__ == "__main__":
    # Example usage
    reviewer = EnhancedReviewPhase3(user_id="admin@company.com", user_role=Role.ADMIN)

    # Start API server
    api = AnalyticsAPI()
    api.run_server()
