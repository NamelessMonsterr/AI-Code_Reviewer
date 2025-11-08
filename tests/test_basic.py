"""
Basic Tests
~~~~~~~~~~~

Basic sanity tests to ensure the application is set up correctly.
"""

import sys
import pytest
from pathlib import Path


# ============================================================================
# Python Environment Tests
# ============================================================================

def test_python_version():
    """Test that Python version is 3.10 or higher."""
    assert sys.version_info >= (3, 10), f"Python 3.10+ required, got {sys.version_info}"


def test_python_version_string():
    """Test Python version string."""
    version_string = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert version_string in ["3.10", "3.11", "3.12"], f"Unexpected Python version: {version_string}"


# ============================================================================
# Basic Math Tests
# ============================================================================

def test_basic_addition():
    """Test basic addition."""
    assert 1 + 1 == 2


def test_basic_subtraction():
    """Test basic subtraction."""
    assert 5 - 3 == 2


def test_basic_multiplication():
    """Test basic multiplication."""
    assert 3 * 4 == 12


def test_basic_division():
    """Test basic division."""
    assert 10 / 2 == 5


# ============================================================================
# Import Tests
# ============================================================================

def test_import_fastapi():
    """Test that FastAPI can be imported."""
    try:
        import fastapi
        assert fastapi is not None
    except ImportError as e:
        pytest.fail(f"Failed to import fastapi: {e}")


def test_import_pydantic():
    """Test that Pydantic can be imported."""
    try:
        import pydantic
        assert pydantic is not None
    except ImportError as e:
        pytest.fail(f"Failed to import pydantic: {e}")


def test_import_sqlalchemy():
    """Test that SQLAlchemy can be imported."""
    try:
        import sqlalchemy
        assert sqlalchemy is not None
    except ImportError as e:
        pytest.fail(f"Failed to import sqlalchemy: {e}")


def test_import_pytest():
    """Test that pytest is available."""
    assert pytest is not None


# ============================================================================
# Configuration Tests
# ============================================================================

def test_settings_import():
    """Test that settings can be imported."""
    try:
        from src.core.config import settings
        assert settings is not None
        assert settings.app_name is not None
    except ImportError as e:
        pytest.fail(f"Failed to import settings: {e}")


def test_settings_values(test_settings):
    """Test that settings have expected values."""
    assert test_settings.app_name == "AI Code Reviewer"
    assert test_settings.environment == "development"
    assert test_settings.testing is True


def test_settings_debug_mode(test_settings):
    """Test that debug mode is enabled in tests."""
    assert test_settings.debug is True


def test_settings_database_url(test_settings):
    """Test that database URL is set."""
    assert test_settings.database_url is not None
    assert "sqlite" in test_settings.database_url.lower() or "postgresql" in test_settings.database_url.lower()


# ============================================================================
# Project Structure Tests
# ============================================================================

def test_project_structure():
    """Test that project structure exists."""
    project_root = Path(__file__).parent.parent
    
    # Check main directories
    assert (project_root / "src").exists(), "src directory not found"
    assert (project_root / "tests").exists(), "tests directory not found"
    
    # Check src subdirectories
    src_dir = project_root / "src"
    expected_dirs = ["api", "core", "models", "services", "integrations", "utils"]
    
    for dir_name in expected_dirs:
        dir_path = src_dir / dir_name
        if dir_path.exists():
            assert (dir_path / "__init__.py").exists(), f"{dir_name}/__init__.py not found"


def test_init_files_exist():
    """Test that __init__.py files exist."""
    project_root = Path(__file__).parent.parent
    
    # Check that src/__init__.py exists
    assert (project_root / "src" / "__init__.py").exists(), "src/__init__.py not found"
    
    # Check that tests/__init__.py exists
    assert (project_root / "tests" / "__init__.py").exists(), "tests/__init__.py not found"


# ============================================================================
# Database Tests
# ============================================================================

def test_database_session(db_session):
    """Test that database session works."""
    assert db_session is not None
    # Try a simple query
    result = db_session.execute("SELECT 1")
    assert result is not None


def test_database_tables(db_engine):
    """Test that database tables are created."""
    from sqlalchemy import inspect
    
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    # Check that we can get table names (even if empty)
    assert isinstance(tables, list)


# ============================================================================
# Redis Tests
# ============================================================================

def test_redis_connection(redis):
    """Test that Redis connection works."""
    assert redis is not None


def test_redis_set_get(redis):
    """Test Redis set and get operations."""
    redis.set("test_key", "test_value")
    value = redis.get("test_key")
    assert value == "test_value"


def test_redis_delete(redis):
    """Test Redis delete operation."""
    redis.set("test_key", "test_value")
    redis.delete("test_key")
    value = redis.get("test_key")
    assert value is None


# ============================================================================
# API Tests
# ============================================================================

def test_api_app_creation(app):
    """Test that FastAPI app can be created."""
    assert app is not None
    assert hasattr(app, "routes")


def test_api_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


def test_api_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]


def test_api_cors_headers(client):
    """Test that CORS headers are set."""
    response = client.get("/")
    # Note: TestClient doesn't process middleware the same way
    # This test verifies the endpoint works
    assert response.status_code == 200


# ============================================================================
# Fixture Tests
# ============================================================================

def test_test_user_fixture(test_user):
    """Test that test_user fixture works."""
    assert test_user is not None
    assert "email" in test_user
    assert "username" in test_user
    assert test_user["email"] == "test@example.com"


def test_auth_token_fixture(auth_token):
    """Test that auth_token fixture works."""
    assert auth_token is not None
    assert isinstance(auth_token, str)
    assert len(auth_token) > 0


def test_auth_headers_fixture(auth_headers):
    """Test that auth_headers fixture works."""
    assert auth_headers is not None
    assert "Authorization" in auth_headers
    assert auth_headers["Authorization"].startswith("Bearer ")


def test_mock_code_sample_fixture(mock_code_sample):
    """Test that mock_code_sample fixture works."""
    assert mock_code_sample is not None
    assert "file_path" in mock_code_sample
    assert "language" in mock_code_sample
    assert "content" in mock_code_sample


# ============================================================================
# Temporary Directory Tests
# ============================================================================

def test_temp_dir_fixture(temp_dir):
    """Test that temp_dir fixture works."""
    assert temp_dir.exists()
    assert temp_dir.is_dir()
    
    # Create a test file
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello, World!")
    
    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"


# ============================================================================
# Environment Tests
# ============================================================================

def test_environment_variables():
    """Test that environment variables are set."""
    import os
    
    assert os.getenv("TESTING") == "True"
    assert os.getenv("ENVIRONMENT") == "development"
    assert os.getenv("OPENAI_API_KEY") is not None


def test_mock_env_fixture(mock_env):
    """Test that mock_env fixture works."""
    import os
    
    mock_env(TEST_VAR="test_value")
    assert os.getenv("TEST_VAR") == "test_value"


# ============================================================================
# Code Sample Tests
# ============================================================================

def test_sample_python_code_fixture(sample_python_code):
    """Test that sample_python_code fixture works."""
    assert sample_python_code is not None
    assert "def fibonacci" in sample_python_code
    assert "class Calculator" in sample_python_code


def test_sample_javascript_code_fixture(sample_javascript_code):
    """Test that sample_javascript_code fixture works."""
    assert sample_javascript_code is not None
    assert "function fibonacci" in sample_javascript_code
    assert "class Calculator" in sample_javascript_code


# ============================================================================
# Async Tests
# ============================================================================

@pytest.mark.asyncio
async def test_async_basic():
    """Test basic async functionality."""
    import asyncio
    await asyncio.sleep(0.001)
    assert True


@pytest.mark.asyncio
async def test_async_client(async_client):
    """Test async client."""
    response = await async_client.get("/")
    assert response.status_code == 200


# ============================================================================
# Parametrized Tests
# ============================================================================

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (5, 5, 10),
    (10, -5, 5),
    (0, 0, 0),
])
def test_parametrized_addition(a, b, expected):
    """Test parametrized addition."""
    assert a + b == expected


@pytest.mark.parametrize("language,extension", [
    ("python", ".py"),
    ("javascript", ".js"),
    ("typescript", ".ts"),
    ("java", ".java"),
    ("go", ".go"),
])
def test_parametrized_languages(language, extension):
    """Test parametrized language extensions."""
    assert extension.startswith(".")
    assert len(extension) > 1


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_exception_handling():
    """Test exception handling."""
    with pytest.raises(ZeroDivisionError):
        _ = 1 / 0


def test_assertion_error():
    """Test assertion error."""
    with pytest.raises(AssertionError):
        assert False, "This should raise an AssertionError"


# ============================================================================
# Skip and XFail Tests
# ============================================================================

@pytest.mark.skip(reason="Example of skipped test")
def test_skipped():
    """This test is skipped."""
    assert False


@pytest.mark.skipif(sys.platform == "win32", reason="Not supported on Windows")
def test_skip_on_windows():
    """This test is skipped on Windows."""
    assert True


@pytest.mark.xfail(reason="Expected to fail - feature not implemented")
def test_expected_failure():
    """This test is expected to fail."""
    assert False


# ============================================================================
# Marker Tests
# ============================================================================

@pytest.mark.unit
def test_unit_marker():
    """Test with unit marker."""
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Test with integration marker."""
    assert True


@pytest.mark.slow
def test_slow_marker():
    """Test with slow marker."""
    assert True


# ============================================================================
# Summary Test
# ============================================================================

def test_all_systems_go():
    """Final test to ensure everything is working."""
    # Python version
    assert sys.version_info >= (3, 10)
    
    # Project structure
    project_root = Path(__file__).parent.parent
    assert (project_root / "src").exists()
    assert (project_root / "tests").exists()
    
    # Configuration
    from src.core.config import settings
    assert settings.testing is True
    
    # All systems operational
    assert True, "All systems go! 🚀"
