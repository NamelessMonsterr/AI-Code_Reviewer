from typing import List, Dict
import re
from collections import Counter


class CodingPatternRecognizer:
    """Learn team-specific coding patterns and preferences"""

    def __init__(self):
        self.patterns = {
            "naming_conventions": Counter(),
            "code_structure": Counter(),
            "common_imports": Counter(),
            "error_handling": Counter(),
            "documentation_style": Counter(),
        }

    def learn_from_codebase(self, files: Dict[str, str]):
        """Learn patterns from existing codebase"""
        for file_path, code in files.items():
            self._extract_naming_patterns(code)
            self._extract_structure_patterns(code)
            self._extract_import_patterns(code)
            self._extract_error_handling(code)
            self._extract_doc_patterns(code)

    def _extract_naming_patterns(self, code: str):
        """Extract naming convention patterns"""
        # Class names
        class_names = re.findall(r"class\s+(\w+)", code)
        for name in class_names:
            if name[0].isupper():
                self.patterns["naming_conventions"]["PascalCase_classes"] += 1
            else:
                self.patterns["naming_conventions"]["lowercase_classes"] += 1

        # Function names
        func_names = re.findall(r"def\s+(\w+)", code)
        for name in func_names:
            if "_" in name:
                self.patterns["naming_conventions"]["snake_case_functions"] += 1
            elif name[0].islower() and any(c.isupper() for c in name):
                self.patterns["naming_conventions"]["camelCase_functions"] += 1

    def _extract_structure_patterns(self, code: str):
        """Extract code structure patterns"""
        # Check for type hints
        if "->" in code or ": " in code:
            self.patterns["code_structure"]["uses_type_hints"] += 1

        # Check for docstrings
        if '"""' in code or "'''" in code:
            self.patterns["code_structure"]["has_docstrings"] += 1

        # Check for decorators
        if "@" in code:
            self.patterns["code_structure"]["uses_decorators"] += 1

    def _extract_import_patterns(self, code: str):
        """Extract common import patterns"""
        imports = re.findall(r"import\s+(\w+)", code)
        imports.extend(re.findall(r"from\s+(\w+)", code))

        for imp in imports:
            self.patterns["common_imports"][imp] += 1

    def _extract_error_handling(self, code: str):
        """Extract error handling patterns"""
        if "try:" in code:
            self.patterns["error_handling"]["uses_try_except"] += 1

        if "raise " in code:
            self.patterns["error_handling"]["raises_exceptions"] += 1

        if "logging." in code or "logger." in code:
            self.patterns["error_handling"]["uses_logging"] += 1

    def _extract_doc_patterns(self, code: str):
        """Extract documentation patterns"""
        # Check docstring style
        if "Args:" in code or "Returns:" in code:
            self.patterns["documentation_style"]["google_style"] += 1
        elif ":param " in code or ":return:" in code:
            self.patterns["documentation_style"]["sphinx_style"] += 1

    def get_team_preferences(self) -> Dict:
        """Get team coding preferences"""
        preferences = {}

        for category, counter in self.patterns.items():
            if counter:
                most_common = counter.most_common(1)[0]
                preferences[category] = {
                    "preferred": most_common[0],
                    "usage_count": most_common[1],
                    "all_patterns": dict(counter),
                }

        return preferences

    def check_consistency(self, code: str) -> List[Dict]:
        """Check if code follows team patterns"""
        violations = []
        preferences = self.get_team_preferences()

        # Check naming consistency
        if "naming_conventions" in preferences:
            preferred = preferences["naming_conventions"]["preferred"]
            if "snake_case" in preferred:
                class_names = re.findall(r"class\s+(\w+)", code)
                for name in class_names:
                    if not name[0].isupper():
                        violations.append(
                            {
                                "type": "naming_inconsistency",
                                "message": f"Class {name} should use PascalCase (team standard)",
                                "severity": "low",
                            }
                        )

        return violations
