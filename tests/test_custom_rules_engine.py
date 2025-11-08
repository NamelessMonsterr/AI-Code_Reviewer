import pytest
from src.rules.custom_rules_engine import CustomRulesEngine

class TestCustomRulesEngine:
    
    @pytest.fixture
    def engine(self, tmp_path):
        """Create rules engine with temporary config"""
        return CustomRulesEngine()
    
    def test_validate_naming_python(self, engine):
        """Test Python naming convention validation"""
        code = """
        class myClass:  # Should be PascalCase
            pass
        
        def MyFunction():  # Should be snake_case
            pass
        """
        
        violations = engine.validate_naming(code, 'python')
        
        assert len(violations) > 0
        assert any(v['category'] == 'class_name' for v in violations)
    
    def test_forbidden_patterns(self, engine):
        """Test detection of forbidden patterns"""
        code = """
        result = eval(user_input)
        exec(dangerous_code)
        """
        
        violations = engine.check_forbidden_patterns(code, 'python')
        
        assert len(violations) >= 2
        assert any('eval(' in v['pattern'] for v in violations)
    
    def test_complexity_check(self, engine):
        """Test cyclomatic complexity detection"""
        complex_code = """
        if condition1:
            if condition2:
                for item in items:
                    while True:
                        if something:
                            if another:
                                try:
                                    if yet_another:
                                        pass
                                except:
                                    pass
        """
        
        violations = engine.check_complexity(complex_code)
        
        assert len(violations) > 0
        assert violations[0]['type'] == 'complexity_violation'
    
    def test_apply_all_rules(self, engine):
        """Test applying all rules at once"""
        code = """
        class badName:
            def WRONG_CASE(self):
                eval("dangerous")
                if a and b and c and d and e:
                    pass
        """
        
        result = engine.apply_all_rules(code, 'python')
        
        assert 'naming_violations' in result
        assert 'forbidden_patterns' in result
        assert 'complexity_issues' in result
