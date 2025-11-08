"""
Configuration Tests
~~~~~~~~~~~~~~~~~~~

Tests for application configuration.
"""

import pytest
from src.core.config import settings


def test_config_app_name():
    """Test app name configuration."""
    assert settings.app_name == "AI Code Reviewer"


def test_config_environment():
    """Test environment configuration."""
    assert settings.environment in ["development", "staging", "production"]


def test_config_debug_mode():
    """Test debug mode in testing."""
    assert settings.debug is True


def test_config_openai_key():
    """Test OpenAI API key is set."""
    assert settings.openai_api_key is not None
    assert len(settings.openai_api_key) > 0


def test_config_jwt_secret():
    """Test JWT secret is set and sufficient length."""
    assert settings.jwt_secret is not None
    assert len(settings.jwt_secret) >= 32


def test_config_database_url():
    """Test database URL is set."""
    assert settings.database_url is not None


def test_config_redis_url():
    """Test Redis URL is set."""
    assert settings.redis_url is not None


def test_config_testing_mode():
    """Test that testing mode is enabled."""
    assert settings.testing is True


def test_config_feature_flags():
    """Test feature flags."""
    assert isinstance(settings.enable_auto_fix, bool)
    assert isinstance(settings.enable_test_generation, bool)
    assert isinstance(settings.enable_compliance_checks, bool)
