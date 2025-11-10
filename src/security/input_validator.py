import re
from typing import Dict, List
import bleach
from pathlib import Path


class InputValidator:
    """Validate and sanitize user inputs"""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS
        r"javascript:",  # JavaScript injection
        r"on\w+\s*=",  # Event handlers
        r"eval\s*\(",  # Code execution
        r"exec\s*\(",  # Code execution
        r"__import__",  # Python imports
        r"subprocess\.",  # System commands
        r"os\.(system|popen)",  # System commands
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b|\bAND\b).*['\"]?\s*=\s*['\"]?",
        r"UNION.*SELECT",
        r"DROP\s+TABLE",
        r"INSERT\s+INTO",
        r"--",
        r"/\*.*\*/",
    ]

    def __init__(self):
        self.max_code_length = 100_000  # 100KB
        self.max_filename_length = 255

    def validate_code_input(self, code: str, language: str) -> Dict:
        """Validate code submission"""
        errors = []

        # Check length
        if len(code) > self.max_code_length:
            errors.append(f"Code exceeds maximum length of {self.max_code_length} characters")

        if not code.strip():
            errors.append("Code cannot be empty")

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(f"Potentially dangerous pattern detected: {pattern}")

        # Language-specific validation
        if language.lower() == "sql":
            for pattern in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, code, re.IGNORECASE):
                    errors.append(f"SQL injection pattern detected: {pattern}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized_code": self._sanitize_code(code) if len(errors) == 0 else None,
        }

    def validate_filename(self, filename: str) -> Dict:
        """Validate file path/name"""
        errors = []

        # Check length
        if len(filename) > self.max_filename_length:
            errors.append(f"Filename exceeds maximum length of {self.max_filename_length}")

        # Check for path traversal
        if ".." in filename or filename.startswith("/"):
            errors.append("Path traversal detected")

        # Check for null bytes
        if "\x00" in filename:
            errors.append("Null byte in filename")

        # Check for valid characters
        if not re.match(r"^[a-zA-Z0-9._/-]+$", filename):
            errors.append("Invalid characters in filename")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized_filename": self._sanitize_filename(filename) if len(errors) == 0 else None,
        }

    def validate_url(self, url: str) -> Dict:
        """Validate URL input"""
        errors = []

        # Basic URL pattern
        url_pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"

        if not re.match(url_pattern, url):
            errors.append("Invalid URL format")

        # Block private IPs
        private_ip_patterns = [
            r"127\.\d+\.\d+\.\d+",  # localhost
            r"10\.\d+\.\d+\.\d+",  # Private class A
            r"172\.(1[6-9]|2\d|3[01])\.\d+\.\d+",  # Private class B
            r"192\.168\.\d+\.\d+",  # Private class C
        ]

        for pattern in private_ip_patterns:
            if re.search(pattern, url):
                errors.append("Private IP addresses not allowed")
                break

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized_url": url if len(errors) == 0 else None,
        }

    def _sanitize_code(self, code: str) -> str:
        """Sanitize code input"""
        # Remove null bytes
        code = code.replace("\x00", "")

        # Normalize line endings
        code = code.replace("\r\n", "\n").replace("\r", "\n")

        return code

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename"""
        # Remove any path components
        filename = Path(filename).name

        # Remove null bytes
        filename = filename.replace("\x00", "")

        # Replace unsafe characters
        filename = re.sub(r"[^\w.-]", "_", filename)

        return filename

    def sanitize_html(self, html: str) -> str:
        """Sanitize HTML content"""
        allowed_tags = ["p", "br", "strong", "em", "code", "pre", "ul", "ol", "li"]
        allowed_attributes = {}

        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=True)
