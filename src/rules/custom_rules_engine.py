import yaml
import re
from typing import Dict, List, Any

class CustomRulesEngine:
    """Allow teams to define custom coding standards"""
    
    def __init__(self, rules_file='config/custom_rules.yaml'):
        self.rules_file = rules_file
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """Load custom rules from YAML file"""
        try:
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._create_default_rules()
    
    def _create_default_rules(self) -> Dict:
        """Create default rules template"""
        default_rules = {
            'naming_conventions': {
                'python': {
                    'class_name': r'^[A-Z][a-zA-Z0-9]*$',
                    'function_name': r'^[a-z_][a-z0-9_]*$',
                    'constant_name': r'^[A-Z_][A-Z0-9_]*$'
                }
            },
            'forbidden_patterns': {
                'python': ['eval(', 'exec(', '__import__'],
                'javascript': ['eval(', 'document.write(']
            },
            'required_patterns': {
                'python': {
                    'docstring': r'""".*"""',
                    'type_hints': r'def \w+\([^)]*:.*\) ->'
                }
            },
            'max_complexity': 10,
            'max_line_length': 120,
            'max_function_length': 50
        }
        return default_rules
    
    def validate_naming(self, code: str, language: str) -> List[Dict]:
        """Validate naming conventions"""
        violations = []
        if language not in self.rules.get('naming_conventions', {}):
            return violations
        
        patterns = self.rules['naming_conventions'][language]
        
        # Check class names
        if 'class_name' in patterns:
            class_pattern = re.compile(r'class\s+(\w+)')
            for match in class_pattern.finditer(code):
                name = match.group(1)
                if not re.match(patterns['class_name'], name):
                    violations.append({
                        'type': 'naming_violation',
                        'category': 'class_name',
                        'name': name,
                        'message': f'Class name "{name}" does not match convention'
                    })
        
        return violations
    
    def check_forbidden_patterns(self, code: str, language: str) -> List[Dict]:
        """Check for forbidden code patterns"""
        violations = []
        forbidden = self.rules.get('forbidden_patterns', {}).get(language, [])
        
        for pattern in forbidden:
            if pattern in code:
                violations.append({
                    'type': 'forbidden_pattern',
                    'pattern': pattern,
                    'message': f'Forbidden pattern "{pattern}" found in code'
                })
        
        return violations
    
    def check_complexity(self, code: str) -> List[Dict]:
        """Check cyclomatic complexity"""
        violations = []
        max_complexity = self.rules.get('max_complexity', 10)
        
        # Simple complexity check based on control flow keywords
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'and', 'or']
        complexity = sum(code.count(kw) for kw in complexity_keywords)
        
        if complexity > max_complexity:
            violations.append({
                'type': 'complexity_violation',
                'complexity': complexity,
                'max_allowed': max_complexity,
                'message': f'Code complexity ({complexity}) exceeds maximum ({max_complexity})'
            })
        
        return violations
    
    def apply_all_rules(self, code: str, language: str) -> Dict:
        """Apply all custom rules to code"""
        return {
            'naming_violations': self.validate_naming(code, language),
            'forbidden_patterns': self.check_forbidden_patterns(code, language),
            'complexity_issues': self.check_complexity(code)
        }
