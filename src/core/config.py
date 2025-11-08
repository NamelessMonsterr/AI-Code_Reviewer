"""
Configuration Module
~~~~~~~~~~~~~~~~~~~~

Application configuration using Pydantic settings.
"""

import os
from typing import Optional, List
from pathlib import Path

from pydantic import Field, validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    
    app_name: str = Field(default="AI Code Reviewer", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    workers: int = Field(default=4, description="Number of worker processes")
    port: int = Field(default=8080, description="API port")
    
    # ========================================================================
    # AI Provider API Keys
    # ========================================================================
    
    openai_api_key: str = Field(..., description="OpenAI API key")
    claude_api_key: Optional[str] = Field(default=None, description="Claude API key")
    google_ai_key: Optional[str] = Field(default=None, description="Google AI API key")
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    
    # ========================================================================
    # Security & Authentication
    # ========================================================================
    
    jwt_secret: str = Field(..., min_length=32, description="JWT secret key")
    db_password: str = Field(..., description="Database password")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/review_bot",
        description="Database URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis URL"
    )
    sqlalchemy_pool_size: int = Field(default=20, description="SQLAlchemy pool size")
    sqlalchemy_max_overflow: int = Field(default=40, description="SQLAlchemy max overflow")
    db_pool_size: int = Field(default=20, description="Database pool size")
    db_pool_timeout: int = Field(default=30, description="Database pool timeout")
    db_statement_timeout: int = Field(default=60, description="Database statement timeout")
    
    # ========================================================================
    # Redis Configuration
    # ========================================================================
    
    redis_pool_size: int = Field(default=10, description="Redis pool size")
    redis_max_connection_age: int = Field(default=300, description="Redis max connection age")
    
    # ========================================================================
    # GitHub Integration
    # ========================================================================
    
    github_token: Optional[str] = Field(default=None, description="GitHub personal access token")
    github_webhook_secret: Optional[str] = Field(default=None, description="GitHub webhook secret")
    github_app_id: Optional[str] = Field(default=None, description="GitHub App ID")
    github_app_private_key: Optional[str] = Field(default=None, description="GitHub App private key")
    github_app_installation_id: Optional[str] = Field(default=None, description="GitHub App installation ID")
    
    # ========================================================================
    # GitLab Integration
    # ========================================================================
    
    gitlab_token: Optional[str] = Field(default=None, description="GitLab token")
    gitlab_webhook_secret: Optional[str] = Field(default=None, description="GitLab webhook secret")
    
    # ========================================================================
    # Bitbucket Integration
    # ========================================================================
    
    bitbucket_token: Optional[str] = Field(default=None, description="Bitbucket token")
    bitbucket_webhook_secret: Optional[str] = Field(default=None, description="Bitbucket webhook secret")
    
    # ========================================================================
    # Azure DevOps Integration
    # ========================================================================
    
    azure_devops_token: Optional[str] = Field(default=None, description="Azure DevOps token")
    azure_devops_org: Optional[str] = Field(default=None, description="Azure DevOps organization")
    
    # ========================================================================
    # Feature Flags
    # ========================================================================
    
    enable_auto_fix: bool = Field(default=True, description="Enable auto-fix")
    enable_test_generation: bool = Field(default=True, description="Enable test generation")
    enable_compliance_checks: bool = Field(default=True, description="Enable compliance checks")
    enable_documentation_gen: bool = Field(default=True, description="Enable documentation generation")
    enable_performance_profiling: bool = Field(default=True, description="Enable performance profiling")
    enable_semantic_search: bool = Field(default=True, description="Enable semantic search")
    enable_interactive_chat: bool = Field(default=True, description="Enable interactive chat")
    
    # ========================================================================
    # OpenAI Settings
    # ========================================================================
    
    openai_model: str = Field(default="gpt-4", description="OpenAI model")
    openai_model_temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="OpenAI model temperature")
    openai_concurrency_limit: int = Field(default=4, description="OpenAI concurrency limit")
    openai_timeout_ms: int = Field(default=60000, description="OpenAI timeout (ms)")
    openai_retries: int = Field(default=3, description="OpenAI retries")
    max_tokens: int = Field(default=2000, description="Max tokens per request")
    
    # ========================================================================
    # Review Settings
    # ========================================================================
    
    max_files: int = Field(default=60, description="Max files to review per PR")
    max_tokens_for_extra_content: int = Field(default=4000, description="Max tokens for extra content")
    review_comment_lgtm: bool = Field(default=False, description="Comment on LGTM reviews")
    path_filters: str = Field(default="**/*.py,**/*.js,**/*.java,**/*.ts,**/*.go", description="Path filters")
    exclude_patterns: str = Field(
        default="**/node_modules/**,**/dist/**,**/build/**,**/__pycache__/**,**/.git/**",
        description="Exclude patterns"
    )
    
    # ========================================================================
    # Compliance Standards
    # ========================================================================
    
    compliance_standards: str = Field(default="SOC2,HIPAA,PCI_DSS,GDPR", description="Compliance standards")
    severity_threshold_critical: float = Field(default=0.9, ge=0.0, le=1.0, description="Critical severity threshold")
    severity_threshold_high: float = Field(default=0.7, ge=0.0, le=1.0, description="High severity threshold")
    severity_threshold_medium: float = Field(default=0.5, ge=0.0, le=1.0, description="Medium severity threshold")
    
    # ========================================================================
    # Caching Configuration
    # ========================================================================
    
    cache_ttl: int = Field(default=3600, description="Cache TTL (seconds)")
    enable_redis_cache: bool = Field(default=True, description="Enable Redis caching")
    cache_key_prefix: str = Field(default="ai_review:", description="Cache key prefix")
    
    # ========================================================================
    # Logging Configuration
    # ========================================================================
    
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    log_max_bytes: int = Field(default=10485760, description="Log max bytes")
    log_backup_count: int = Field(default=5, description="Log backup count")
    
    # ========================================================================
    # Monitoring & Observability
    # ========================================================================
    
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    sentry_environment: str = Field(default="production", description="Sentry environment")
    sentry_traces_sample_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Sentry traces sample rate")
    prometheus_enabled: bool = Field(default=True, description="Prometheus enabled")
    grafana_user: str = Field(default="admin", description="Grafana user")
    grafana_password: str = Field(default="admin", description="Grafana password")
    
    # ========================================================================
    # Email Notifications
    # ========================================================================
    
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_user: Optional[str] = Field(default=None, description="SMTP user")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_from_email: str = Field(default="noreply@example.com", description="SMTP from email")
    smtp_use_tls: bool = Field(default=True, description="SMTP use TLS")
    
    # ========================================================================
    # Slack Integration
    # ========================================================================
    
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack webhook URL")
    slack_channel: str = Field(default="#code-reviews", description="Slack channel")
    slack_bot_token: Optional[str] = Field(default=None, description="Slack bot token")
    
    # ========================================================================
    # Teams Integration
    # ========================================================================
    
    teams_webhook_url: Optional[str] = Field(default=None, description="Teams webhook URL")
    
    # ========================================================================
    # Rate Limiting
    # ========================================================================
    
    rate_limit_per_user: int = Field(default=60, description="Requests per minute per user")
    rate_limit_per_ip: int = Field(default=100, description="Requests per minute per IP")
    rate_limit_window: int = Field(default=60, description="Rate limit window (seconds)")
    
    # ========================================================================
    # Security Scanning
    # ========================================================================
    
    enable_bandit: bool = Field(default=True, description="Enable Bandit")
    enable_semgrep: bool = Field(default=True, description="Enable Semgrep")
    enable_secret_detection: bool = Field(default=True, description="Enable secret detection")
    enable_dependency_scan: bool = Field(default=True, description="Enable dependency scan")
    semgrep_rules: str = Field(default="p/security-audit,p/owasp-top-ten", description="Semgrep rules")
    
    # ========================================================================
    # Storage Configuration
    # ========================================================================
    
    data_dir: Path = Field(default=Path("/app/data"), description="Data directory")
    logs_dir: Path = Field(default=Path("/app/logs"), description="Logs directory")
    config_dir: Path = Field(default=Path("/app/config"), description="Config directory")
    temp_dir: Path = Field(default=Path("/tmp/ai_review"), description="Temp directory")
    
    # ========================================================================
    # Backup Configuration
    # ========================================================================
    
    enable_backups: bool = Field(default=True, description="Enable backups")
    backup_schedule: str = Field(default="0 2 * * *", description="Backup schedule (cron)")
    backup_retention_days: int = Field(default=30, description="Backup retention days")
    backup_dir: Path = Field(default=Path("/app/backups"), description="Backup directory")
    
    # ========================================================================
    # Cost Management
    # ========================================================================
    
    monthly_budget_limit: float = Field(default=1000.0, description="Monthly budget limit (USD)")
    budget_alert_threshold: int = Field(default=80, ge=0, le=100, description="Budget alert threshold (%)")
    enable_cost_tracking: bool = Field(default=True, description="Enable cost tracking")
    
    # ========================================================================
    # CORS Configuration
    # ========================================================================
    
    allowed_origins: Optional[str] = Field(
        default=None,
        description="Allowed CORS origins (comma-separated)"
    )
    allowed_hosts: Optional[str] = Field(
        default=None,
        description="Allowed hosts (comma-separated)"
    )
    
    # ========================================================================
    # Webhook Configuration
    # ========================================================================
    
    webhook_secret: Optional[str] = Field(default=None, description="Webhook secret")
    webhook_timeout: int = Field(default=30, description="Webhook timeout (seconds)")
    webhook_max_retries: int = Field(default=3, description="Max webhook retries")
    
    # ========================================================================
    # Advanced Features
    # ========================================================================
    
    enable_experimental_features: bool = Field(default=False, description="Enable experimental features")
    ai_temperature: float = Field(default=0.2, ge=0.0, le=1.0, description="AI temperature")
    enable_streaming: bool = Field(default=False, description="Enable streaming responses")
    custom_rules_file: Optional[Path] = Field(default=None, description="Custom rules file")
    knowledge_base_file: Optional[Path] = Field(default=None, description="Knowledge base file")
    
    # ========================================================================
    # Testing
    # ========================================================================
    
    testing: bool = Field(default=False, description="Testing mode")
    test_mode: bool = Field(default=False, description="Test mode")
    mock_external_services: bool = Field(default=False, description="Mock external services")
    
    # ========================================================================
    # Model Configuration
    # ========================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ========================================================================
    # Validators
    # ========================================================================
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Format database URL with password."""
        if "${DB_PASSWORD}" in v:
            db_password = os.getenv("DB_PASSWORD", "postgres")
            v = v.replace("${DB_PASSWORD}", db_password)
        return v
    
    @field_validator("data_dir", "logs_dir", "config_dir", "temp_dir", "backup_dir")
    @classmethod
    def create_directories(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    # ========================================================================
    # Properties
    # ========================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    @property
    def compliance_standards_list(self) -> List[str]:
        """Get compliance standards as list."""
        return [s.strip() for s in self.compliance_standards.split(",")]
    
    @property
    def path_filters_list(self) -> List[str]:
        """Get path filters as list."""
        return [p.strip() for p in self.path_filters.split(",")]
    
    @property
    def exclude_patterns_list(self) -> List[str]:
        """Get exclude patterns as list."""
        return [p.strip() for p in self.exclude_patterns.split(",")]


# Create global settings instance
settings = Settings()
