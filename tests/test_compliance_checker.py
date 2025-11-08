import pytest
from src.compliance.compliance_checker import ComplianceChecker

class TestComplianceChecker:
    
    @pytest.fixture
    def checker(self):
        return ComplianceChecker()
    
    def test_soc2_unencrypted_data(self, checker):
        """Test SOC2 detection of unencrypted sensitive data"""
        code = """
        api_key = "sk-1234567890"
        password = user_input
        """
        
        violations = checker.check_soc2_compliance(code, "test.py")
        
        assert len(violations) > 0
        assert any(v['category'] == 'data_encryption' for v in violations)
    
    def test_hipaa_phi_exposure(self, checker):
        """Test HIPAA PHI logging detection"""
        code = """
        patient_data = get_patient()
        print(patient_data)
        """
        
        violations = checker.check_hipaa_compliance(code, "medical.py")
        
        assert len(violations) > 0
        assert any(v['standard'] == 'HIPAA' for v in violations)
    
    def test_pci_card_data(self, checker):
        """Test PCI DSS card data handling"""
        code = """
        card_number = "4111111111111111"
        cvv = "123"
        """
        
        violations = checker.check_pci_dss_compliance(code, "payment.py")
        
        assert len(violations) > 0
        assert any('card' in v['message'].lower() for v in violations)
    
    def test_gdpr_personal_data(self, checker):
        """Test GDPR personal data handling"""
        code = """
        email = user.email
        phone = user.phone
        """
        
        violations = checker.check_gdpr_compliance(code, "user.py")
        
        assert len(violations) > 0
    
    def test_compliant_code(self, checker):
        """Test that compliant code passes"""
        code = """
        encrypted_data = encrypt(sensitive_info)
        hashed_password = hash(password)
        """
        
        result = checker.run_all_compliance_checks(code, "secure.py")
        
        # Should have fewer violations
        assert result['compliance_status'] in ['PASSED', 'FAILED']
    
    def test_generate_report(self, checker):
        """Test compliance report generation"""
        violations = [
            {
                'standard': 'SOC2',
                'severity': 'critical',
                'message': 'Test violation',
                'file': 'test.py',
                'category': 'encryption'
            }
        ]
        
        report = checker.generate_compliance_report(violations)
        
        assert '## SOC2' in report
        assert 'Test violation' in report
        assert 'CRITICAL' in report
