"""
Utils Module
~~~~~~~~~~~~

Utility functions and helpers.
"""

try:
    from src.utils.helpers import (
        format_code,
        parse_diff,
        extract_functions,
        calculate_complexity,
    )
    from src.utils.validators import (
        validate_code,
        validate_config,
        validate_repository_url,
    )
except ImportError:
    format_code = None
    parse_diff = None
    extract_functions = None
    calculate_complexity = None
    validate_code = None
    validate_config = None
    validate_repository_url = None

__all__ = [
    "format_code",
    "parse_diff",
    "extract_functions",
    "calculate_complexity",
    "validate_code",
    "validate_config",
    "validate_repository_url",
]
