from openai import OpenAI
import os
from typing import Dict, List


class TestGenerator:
    """Automatically generate unit tests for code"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=self.api_key)

    def generate_tests(self, function_code: str, language: str, framework: str = None) -> str:
        """Generate comprehensive unit tests"""

        if framework is None:
            framework = self._get_default_framework(language)

        prompt = f"""Generate comprehensive unit tests for this {language} function using {framework}:

{function_code}

Include tests for:
1. Happy path (normal inputs)
2. Edge cases (empty, null, boundary values)
3. Error handling (invalid inputs)
4. Performance (if applicable)
5. Mock external dependencies

Provide complete, runnable test code."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    def _get_default_framework(self, language: str) -> str:
        """Get default testing framework for language"""
        frameworks = {
            "python": "pytest",
            "javascript": "jest",
            "java": "JUnit 5",
            "go": "testing package",
            "ruby": "RSpec",
            "csharp": "xUnit",
        }
        return frameworks.get(language.lower(), "unittest")

    def generate_integration_tests(self, endpoint_code: str, api_spec: Dict) -> str:
        """Generate integration tests for API endpoints"""
        prompt = f"""Generate integration tests for this API endpoint:

Code:
{endpoint_code}

API Specification:
{api_spec}

Include tests for:
1. Success responses
2. Error responses (4xx, 5xx)
3. Authentication/Authorization
4. Input validation
5. Response format validation"""

        response = self.client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.2
        )

        return response.choices[0].message.content

    def calculate_coverage_gaps(self, code: str, existing_tests: str) -> List[str]:
        """Identify uncovered code paths"""
        prompt = f"""Analyze this code and existing tests to identify coverage gaps:

Code:
{code}

Existing Tests:
{existing_tests}

List:
1. Uncovered code paths
2. Missing edge cases
3. Untested error conditions"""

        response = self.client.chat.completions.create(
            model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.2
        )

        return response.choices[0].message.content.split("\n")
