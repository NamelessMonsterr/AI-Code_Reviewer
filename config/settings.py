from pydantic_settings import BaseSettings
from pydantic import validator, Fieldfrom typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings with validation"""

    # AI Provider API Keys (Required)
    OPENAI_API_KEY: str = Field(..., min_length=20)
    CLAUDE_API_KEY: Optional[str] = None
    GOOGLE_AI_KEY: Optional[str] = None

    # Security (Required)
    JWT_SECRET: str = Field(..., min_length=32)
    DB_PASSWORD: str = Field(..., min_length=8)
    REDIS_PASSWORD: Optional[str] = None

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/review_bot"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379")

    # GitHub Integration
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None

    # Application Settings
    ENVIRONMENT: str = Field(default="development", regex="^(development|staging|production)$")
    DEBUG: bool = False
    LOG_LEVEL: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    PORT: int = Field(default=8080, ge=1024, le=65535)
    WORKERS: int = Field(default=4, ge=1, le=16)

    # Feature Flags
    ENABLE_AUTO_FIX: bool = True
    ENABLE_TEST_GENERATION: bool = True
    ENABLE_COMPLIANCE_CHECKS: bool = True
    ENABLE_REDIS_CACHE: bool = True

    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MODEL_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=1.0)
    OPENAI_TIMEOUT_MS: int = Field(default=60000, ge=5000)
    OPENAI_RETRIES: int = Field(default=3, ge=1, le=10)
    OPENAI_CONCURRENCY_LIMIT: int = Field(default=4, ge=1, le=20)

    # Review Settings
    MAX_FILES: int = Field(default=60, ge=1)
    REVIEW_COMMENT_LGTM: bool = False

    # Rate Limiting
    RATE_LIMIT_PER_USER: int = Field(default=60, ge=1)
    RATE_LIMIT_PER_IP: int = Field(default=100, ge=1)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)

    # Cache Settings
    CACHE_TTL: int = Field(default=3600, ge=60)

    # Compliance Standards
    COMPLIANCE_STANDARDS: List[str] = Field(
        default=["SOC2", "HIPAA", "PCI_DSS", "GDPR"]
    )

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True

    @validator('JWT_SECRET')
    def jwt_secret_validation(cls, v):
        if len(v) < 32:
            raise ValueError('JWT_SECRET must be at least 32 characters long')
        if v == 'your-jwt-secret-key-at-least-32-characters-long-please-change-this':
            raise ValueError('JWT_SECRET must be changed from default value')
        return v

    @validator('DB_PASSWORD')
    def db_password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('DB_PASSWORD must be at least 8 characters long')
        if v in ['password', '12345678', 'admin']:
            raise ValueError('DB_PASSWORD is too weak')
        return v

    @validator('OPENAI_API_KEY')
    def openai_key_validation(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('OPENAI_API_KEY must start with "sk-"')
        return v

    @validator('DATABASE_URL')
    def database_url_validation(cls, v):
        if 'postgresql://' not in v and 'postgres://' not in v:
            raise ValueError('DATABASE_URL must be a PostgreSQL connection string')
        return v

    @validator('ENVIRONMENT')
    def environment_validation(cls, v, values):
        if v == 'production' and values.get('DEBUG', False):
            raise ValueError('DEBUG must be False in production environment')
        return v

    class Config:
        env_file = '.env'
        case_sensitive = True

    def validate_all(self) -> List[str]:
        """Validate all settings and return warnings"""
        warnings = []

        # Warn about optional features
        if not self.CLAUDE_API_KEY:
            warnings.append("CLAUDE_API_KEY not set - Claude AI provider disabled")

        if not self.GOOGLE_AI_KEY:
            warnings.append("GOOGLE_AI_KEY not set - Gemini AI provider disabled")

        if not self.GITHUB_TOKEN:
            warnings.append("GITHUB_TOKEN not set - GitHub integration disabled")

        if self.ENVIRONMENT == 'production' and not self.SENTRY_DSN:
            warnings.append("SENTRY_DSN not set - Error tracking disabled in production")

        if not self.REDIS_PASSWORD:
            warnings.append("REDIS_PASSWORD not set - Redis is unprotected")

        return warnings
