# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # AI Providers
    openai_api_key: str
    claude_api_key: Optional[str] = None
    google_ai_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    # Security
    jwt_secret: str
    db_password: str
    redis_password: Optional[str] = None
    
    # Database
    database_url: str
    redis_url: str
    sqlalchemy_pool_size: int = 20
    sqlalchemy_max_overflow: int = 40
    
    # GitHub
    github_token: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # Feature Flags
    enable_auto_fix: bool = True
    enable_test_generation: bool = True
    enable_compliance_checks: bool = True
    
    # Application
    environment: str = "development"
    debug: bool = False
    workers: int = 4
    port: int = 8080
    
    # OpenAI Settings
    openai_model: str = "gpt-4"
    openai_model_temperature: float = 0.2
    openai_concurrency_limit: int = 4
    openai_timeout_ms: int = 60000
    openai_retries: int = 3
    
    # Review Settings
    max_files: int = 60
    review_comment_lgtm: bool = False
    path_filters: List[str] = ["**/*.py", "**/*.js", "**/*.java"]
    exclude_patterns: List[str] = ["**/node_modules/**", "**/dist/**"]
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = True
    log_level: str = "INFO"
    
    # Rate Limiting
    rate_limit_per_user: int = 60
    rate_limit_per_ip: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()