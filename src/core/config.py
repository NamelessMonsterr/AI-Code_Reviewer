"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "AI Code Reviewer"
    version: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
