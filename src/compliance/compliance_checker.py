import json
from typing import Dict, List
from datetime import datetime


class ComplianceChecker:
    """Enterprise compliance checking (SOC 2, HIPAA, PCI DSS, GDPR)"""

    def __init__(self):
        self.compliance_standards = self._load_standards()
        self.violations = []

    def _load_standards(self) -> Dict:
        """Load compliance standards and rules"""
        return {
            "SOC2": {
                "data_encryption": {
                    "patterns": ["password", "secret", "api_key", "token"],
                    "required": ["encrypt", "hash", "secure"],
                },
                "access_control": {"required": ["authenticate", "authorize", "permission"]},
                "audit_logging": {"required": ["log", "audit", "track"]},
            },
            "HIPAA": {
                "phi_handling": {
                    "forbidden": ["print", "console.log", "System.out"],
                    "required": ["encrypt", "anonymize", "de-identify"],
                },
                "data_transmission": {"required": ["tls", "ssl", "https"]},
            },
            "PCI_DSS": {
                "card_data": {
                    "patterns": ["card_number", "cvv", "expiry"],
                    "forbidden": ["plain_text", "unencrypted"],
                    "required": ["tokenize", "encrypt"],
                },
                "secure_storage": {"required": ["vault", "hsm", "kms"]},
            },
            "GDPR": {
                "personal_data": {
                    "patterns": ["email", "phone", "ssn", "address"],
                    "required": ["consent", "anonymize", "pseudonymize"],
                },
                "data_retention": {"required": ["delete", "expire", "purge"]},
            },
        }

    def check_soc2_compliance(self, code: str, file_path: str) -> List[Dict]:
        """Check SOC 2 compliance"""
        violations = []
        soc2_rules = self.compliance_standards["SOC2"]

        # Check for unencrypted sensitive data
        for pattern in soc2_rules["data_encryption"]["patterns"]:
            if pattern in code.lower():
                has_encryption = any(
                    req in code.lower() for req in soc2_rules["data_encryption"]["required"]
                )
                if not has_encryption:
                    violations.append(
                        {
                            "standard": "SOC2",
                            "category": "data_encryption",
                            "severity": "critical",
                            "message": f"Sensitive data ({pattern}) found without encryption",
                            "file": file_path,
                        }
                    )

        return violations

    def check_hipaa_compliance(self, code: str, file_path: str) -> List[Dict]:
        """Check HIPAA compliance for healthcare data"""
        violations = []
        hipaa_rules = self.compliance_standards["HIPAA"]

        # Check for PHI logging violations
        for forbidden in hipaa_rules["phi_handling"]["forbidden"]:
            if forbidden in code and any(
                p in code.lower() for p in ["patient", "medical", "health"]
            ):
                violations.append(
                    {
                        "standard": "HIPAA",
                        "category": "phi_handling",
                        "severity": "critical",
                        "message": f"Potential PHI exposure via {forbidden}",
                        "file": file_path,
                    }
                )

        return violations

    def check_pci_dss_compliance(self, code: str, file_path: str) -> List[Dict]:
        """Check PCI DSS compliance for payment data"""
        violations = []
        pci_rules = self.compliance_standards["PCI_DSS"]

        # Check for card data handling
        for pattern in pci_rules["card_data"]["patterns"]:
            if pattern in code.lower():
                has_tokenization = any(
                    req in code.lower() for req in pci_rules["card_data"]["required"]
                )
                if not has_tokenization:
                    violations.append(
                        {
                            "standard": "PCI DSS",
                            "category": "card_data",
                            "severity": "critical",
                            "message": f"Card data ({pattern}) must be tokenized/encrypted",
                            "file": file_path,
                        }
                    )

        return violations

    def check_gdpr_compliance(self, code: str, file_path: str) -> List[Dict]:
        """Check GDPR compliance for personal data"""
        violations = []
        gdpr_rules = self.compliance_standards["GDPR"]

        # Check for personal data handling
        for pattern in gdpr_rules["personal_data"]["patterns"]:
            if pattern in code.lower():
                has_protection = any(
                    req in code.lower() for req in gdpr_rules["personal_data"]["required"]
                )
                if not has_protection:
                    violations.append(
                        {
                            "standard": "GDPR",
                            "category": "personal_data",
                            "severity": "high",
                            "message": f"Personal data ({pattern}) requires GDPR protection",
                            "file": file_path,
                        }
                    )

        return violations

    def run_all_compliance_checks(
        self, code: str, file_path: str, standards: List[str] = None
    ) -> Dict:
        """Run all required compliance checks"""
        if standards is None:
            standards = ["SOC2", "HIPAA", "PCI_DSS", "GDPR"]

        all_violations = []

        if "SOC2" in standards:
            all_violations.extend(self.check_soc2_compliance(code, file_path))
        if "HIPAA" in standards:
            all_violations.extend(self.check_hipaa_compliance(code, file_path))
        if "PCI_DSS" in standards:
            all_violations.extend(self.check_pci_dss_compliance(code, file_path))
        if "GDPR" in standards:
            all_violations.extend(self.check_gdpr_compliance(code, file_path))

        return {
            "total_violations": len(all_violations),
            "violations": all_violations,
            "compliance_status": "FAILED" if all_violations else "PASSED",
        }

    def generate_compliance_report(self, violations: List[Dict]) -> str:
        """Generate detailed compliance report"""
        report = "# Compliance Report\n\n"
        report += f"**Generated**: {datetime.now().isoformat()}\n\n"

        # Group by standard
        by_standard = {}
        for v in violations:
            std = v["standard"]
            if std not in by_standard:
                by_standard[std] = []
            by_standard[std].append(v)

        for standard, viols in by_standard.items():
            report += f"## {standard}\n"
            report += f"**Violations**: {len(viols)}\n\n"
            for v in viols:
                report += f"- **{v['severity'].upper()}**: {v['message']}\n"
                report += f"  - File: `{v['file']}`\n"
                report += f"  - Category: {v['category']}\n\n"

        return report
