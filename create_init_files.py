#!/usr/bin/env python3
"""
Script to create all __init__.py files with proper content.
"""

import os
from pathlib import Path

# Define the content for each __init__.py file
INIT_FILES = {
    "src/__init__.py": '''"""
AI Code Reviewer
~~~~~~~~~~~~~~~~~

An intelligent, AI-powered code review automation tool.

:copyright: (c) 2024 AI Code Reviewer Team
:license: MIT, see LICENSE for more details.
"""

__version__ = "0.1.0"
__author__ = "AI Code Reviewer Team"
__license__ = "MIT"

from src.core.config import settings

__all__ = ["__version__", "settings"]
''',
    
    "src/core/__init__.py": '''"""Core Module - Core functionality."""

from src.core.config import settings

__all__ = ["settings"]
''',
    
    "src/api/__init__.py": '''"""API Module - FastAPI routes and endpoints."""

__all__ = []
''',
    
    "src/services/__init__.py": '''"""Services Module - Business logic layer."""

__all__ = []
''',
    
    "src/security/__init__.py": '''"""Security Module - Security utilities."""

__all__ = []
''',
    
    "src/models/__init__.py": '''"""Models Module - Database models."""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

__all__ = ["Base"]
''',
    
    "src/integrations/__init__.py": '''"""Integrations Module - Third-party integrations."""

__all__ = []
''',
    
    "src/utils/__init__.py": '''"""Utils Module - Utility functions."""

__all__ = []
''',
    
    "src/schemas/__init__.py": '''"""Schemas Module - Pydantic models."""

__all__ = []
''',
    
    "src/tasks/__init__.py": '''"""Tasks Module - Celery background tasks."""

__all__ = []
''',
    
    "tests/__init__.py": '''"""Test Suite for AI Code Reviewer."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

__all__ = []
''',
}

def create_init_files():
    """Create all __init__.py files."""
    for file_path, content in INIT_FILES.items():
        path = Path(file_path)
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        with open(path, 'w') as f:
            f.write(content)
        
        print(f"✅ Created {file_path}")

if __name__ == "__main__":
    print("🔧 Creating __init__.py files...")
    create_init_files()
    print("✅ Done! All __init__.py files created.")
