"""
Pytest Configuration and Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shared fixtures and configuration for all tests.
"""

import os
import sys
import asyncio
from typing import Generator, AsyncGenerator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from redis import Redis
from fakeredis import FakeRedis
import httpx

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables BEFORE importing app
os.environ["TESTING"] = "True"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["OPENAI_API_KEY"] = "test-key-123"
os.environ["JWT_SECRET"] = "test-jwt-secret-key-at-least-32-characters-long"
os.environ["DB_PASSWORD"] = "test-password"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"

# Import after setting environment variables
from src.core.config import settings
from src.models import Base


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.
    
    Yields:
        asyncio.AbstractEventLoop: Event loop instance
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """
    Create a test database engine.
    
    Returns:
        Engine: SQLAlchemy engine
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Create a new database session for a test.
    
    Args:
        db_engine: Database engine
        
    Yields:
        Session: Database session
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db(db_session):
    """Alias for db_session."""
    return db_session


# ============================================================================
# Redis Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def redis_client():
    """
    Create a fake Redis client for testing.
    
    Returns:
        FakeRedis: Fake Redis client
    """
    client = FakeRedis(decode_responses=True)
    yield client
    client.flushall()


@pytest.fixture(scope="function")
def redis(redis_client):
    """
    Create a clean Redis instance for each test.
    
    Args:
        redis_client: Redis client
        
    Yields:
        FakeRedis: Redis client
    """
    redis_client.flushall()
    yield redis_client
    redis_client.flushall()


# ============================================================================
# FastAPI Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def app():
    """
    Create FastAPI application instance.
    
    Returns:
        FastAPI: Application instance
    """
    from src.api.server import app
    return app


@pytest.fixture(scope="function")
def client(app, db_session) -> Generator[TestClient, None, None]:
    """
    Create a test client.
    
    Args:
        app: FastAPI application
        db_session: Database session
        
    Yields:
        TestClient: Test client
    """
    from src.database import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(app):
    """
    Create an async test client.
    
    Args:
        app: FastAPI application
        
    Yields:
        AsyncClient: Async test client
    """
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# Authentication Fixtures
# ============================================================================

@pytest.fixture
def test_user():
    """
    Create a test user.
    
    Returns:
        dict: Test user data
    """
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
def test_superuser():
    """
    Create a test superuser.
    
    Returns:
        dict: Test superuser data
    """
    return {
        "id": "test-admin-456",
        "email": "admin@example.com",
        "username": "admin",
        "password": "adminpassword123",
        "is_active": True,
        "is_superuser": True,
    }


@pytest.fixture
def auth_token(test_user):
    """
    Create an authentication token.
    
    Args:
        test_user: Test user data
        
    Returns:
        str: JWT token
    """
    try:
        from src.core.security import auth_handler
        return auth_handler.encode_token(test_user["id"])
    except ImportError:
        # If security module doesn't exist, return a dummy token
        return "test-token-123"


@pytest.fixture
def auth_headers(auth_token):
    """
    Create authentication headers.
    
    Args:
        auth_token: JWT token
        
    Returns:
        dict: Headers with authorization
    """
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """
    Create a mock OpenAI response.
    
    Returns:
        dict: Mock response
    """
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This code looks good! No issues found."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_github_pr():
    """
    Create a mock GitHub pull request.
    
    Returns:
        dict: Mock PR data
    """
    return {
        "number": 123,
        "title": "Add new feature",
        "body": "This PR adds a new feature",
        "state": "open",
        "user": {
            "login": "testuser",
            "id": 12345
        },
        "head": {
            "ref": "feature-branch",
            "sha": "abc123"
        },
        "base": {
            "ref": "main",
            "sha": "def456"
        },
        "changed_files": 3,
        "additions": 100,
        "deletions": 20,
    }


@pytest.fixture
def mock_code_sample():
    """
    Create a mock code sample.
    
    Returns:
        dict: Mock code data
    """
    return {
        "file_path": "src/example.py",
        "language": "python",
        "content": '''
def hello_world():
    """Print hello world."""
    print("Hello, World!")

def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''.strip(),
    }


@pytest.fixture
def mock_review_request():
    """
    Create a mock review request.
    
    Returns:
        dict: Mock review request
    """
    return {
        "repository": "owner/repo",
        "pull_request": 123,
        "files": [
            {
                "path": "src/example.py",
                "status": "modified",
                "additions": 10,
                "deletions": 2,
                "changes": 12,
            }
        ],
    }


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """
    Create a temporary directory.
    
    Args:
        tmp_path: Pytest tmp_path fixture
        
    Returns:
        Path: Temporary directory path
    """
    return tmp_path


@pytest.fixture
def temp_repo(tmp_path):
    """
    Create a temporary Git repository.
    
    Args:
        tmp_path: Pytest tmp_path fixture
        
    Returns:
        Path: Repository path
    """
    import subprocess
    
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True
    )
    
    # Create initial commit
    test_file = repo_path / "README.md"
    test_file.write_text("# Test Repository")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True
    )
    
    return repo_path


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_settings():
    """
    Create test settings.
    
    Returns:
        Settings: Test settings
    """
    return settings


@pytest.fixture
def mock_env(monkeypatch):
    """
    Create a mock environment.
    
    Args:
        monkeypatch: Pytest monkeypatch fixture
        
    Returns:
        function: Function to set environment variables
    """
    def _set_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, str(value))
    
    return _set_env


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_python_code():
    """
    Sample Python code for testing.
    
    Returns:
        str: Python code
    """
    return '''
def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """Simple calculator class."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b
'''.strip()


@pytest.fixture
def sample_javascript_code():
    """
    Sample JavaScript code for testing.
    
    Returns:
        str: JavaScript code
    """
    return '''
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

class Calculator {
    add(a, b) {
        return a + b;
    }
    
    subtract(a, b) {
        return a - b;
    }
}

module.exports = { fibonacci, Calculator };
'''.strip()


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """
    Cleanup after each test.
    
    Yields:
        None
    """
    yield
    # Cleanup code here if needed


# ============================================================================
# Marker Helpers
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Modify test items during collection.
    
    Args:
        config: Pytest config
        items: Test items
    """
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
