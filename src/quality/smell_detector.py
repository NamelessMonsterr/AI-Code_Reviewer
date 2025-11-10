from typing import List, Dict
import re


class CodeSmellDetector:
    """Detect code smells and suggest refactoring"""

    def __init__(self):
        self.smells = self._load_smell_patterns()

    def _load_smell_patterns(self) -> Dict:
        """Load code smell patterns"""
        return {
            "long_method": {
                "threshold": 50,
                "message": "Method is too long, consider extracting smaller methods",
            },
            "large_class": {
                "threshold": 500,
                "message": "Class is too large, consider splitting responsibilities",
            },
            "duplicate_code": {
                "threshold": 0.8,
                "message": "Duplicate code detected, consider extracting to shared method",
            },
            "magic_numbers": {
                "pattern": r"\b\d{2,}\b",
                "message": "Magic number found, use named constant instead",
            },
            "long_parameter_list": {
                "threshold": 5,
                "message": "Too many parameters, consider using object/config",
            },
            "deep_nesting": {
                "threshold": 4,
                "message": "Deep nesting detected, consider early returns or extraction",
            },
        }

    def detect_long_method(self, code: str) -> List[Dict]:
        """Detect methods that are too long"""
        smells = []
        lines = code.split("\n")

        if len(lines) > self.smells["long_method"]["threshold"]:
            smells.append(
                {
                    "type": "long_method",
                    "severity": "medium",
                    "lines": len(lines),
                    "message": self.smells["long_method"]["message"],
                }
            )

        return smells

    def detect_magic_numbers(self, code: str) -> List[Dict]:
        """Detect magic numbers in code"""
        smells = []
        pattern = self.smells["magic_numbers"]["pattern"]

        for match in re.finditer(pattern, code):
            number = match.group()
            if number not in ["0", "1", "100"]:  # Common acceptable numbers
                smells.append(
                    {
                        "type": "magic_number",
                        "severity": "low",
                        "number": number,
                        "position": match.start(),
                        "message": f"Magic number {number} should be a named constant",
                    }
                )

        return smells

    def detect_god_class(self, code: str, class_name: str) -> Dict:
        """Detect God/Monster class anti-pattern"""
        lines = code.split("\n")
        method_count = len(re.findall(r"def \w+\(", code))

        if len(lines) > 500 or method_count > 20:
            return {
                "type": "god_class",
                "severity": "high",
                "class": class_name,
                "lines": len(lines),
                "methods": method_count,
                "message": "Class has too many responsibilities, violates Single Responsibility Principle",
            }

        return None

    def detect_deep_nesting(self, code: str) -> List[Dict]:
        """Detect deeply nested code blocks"""
        smells = []
        lines = code.split("\n")

        for i, line in enumerate(lines):
            indent = len(line) - len(line.lstrip())
            if indent > 16:  # More than 4 levels of indentation
                smells.append(
                    {
                        "type": "deep_nesting",
                        "severity": "medium",
                        "line": i + 1,
                        "indent_level": indent // 4,
                        "message": self.smells["deep_nesting"]["message"],
                    }
                )

        return smells

    def run_all_detections(self, code: str) -> Dict:
        """Run all code smell detections"""
        return {
            "long_methods": self.detect_long_method(code),
            "magic_numbers": self.detect_magic_numbers(code),
            "deep_nesting": self.detect_deep_nesting(code),
            "total_smells": 0,  # Calculate total
        }
