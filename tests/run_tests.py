#!/usr/bin/env python
"""
Run all tests with coverage reporting
"""
import pytest
import sys


def main():
    """Run pytest with coverage"""
    args = [
        "--verbose",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term",
        "--cov-report=xml",
        "tests/",
    ]

    exit_code = pytest.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
