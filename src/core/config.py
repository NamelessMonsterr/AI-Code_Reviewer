"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "AI Code Reviewer"
    version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    
    # API Keys
    openai_api_key: str = "your-api-key"
    
    # Security
    jwt_secret: str = "your-secret-key-min-32-chars"
    
    # Database
    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
