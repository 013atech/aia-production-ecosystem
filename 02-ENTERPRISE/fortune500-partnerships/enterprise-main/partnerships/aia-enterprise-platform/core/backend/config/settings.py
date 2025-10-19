"""
AIA Enterprise Platform - Configuration Settings
==============================================

Centralized configuration management with environment-specific settings,
security considerations, and validation.
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Application settings with validation and environment variable loading"""

    # Application
    app_name: str = Field(default="AIA Enterprise Platform", env="APP_NAME")
    version: str = Field(default="4.0.0", env="APP_VERSION")
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")

    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")

    # Security
    secret_key: str = Field(env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    encrypt_key: Optional[str] = Field(default=None, env="ENCRYPT_KEY")
    allowed_origins: List[str] = Field(
        default=[
            "https://013a.tech",
            "https://www.013a.tech"
        ],
        env="ALLOWED_ORIGINS"
    )

    # Database
    database_url: str = Field(
        default="postgresql://aia:aia@localhost:5432/aia_enterprise",
        env="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    db_pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")

    # Knowledge Graph
    knowledge_graph_path: Optional[str] = Field(
        default=None,
        env="KNOWLEDGE_GRAPH_PATH"
    )
    knowledge_graph_embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="KNOWLEDGE_GRAPH_EMBEDDING_MODEL"
    )

    # AI/ML Services
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    vertex_ai_project: Optional[str] = Field(default=None, env="VERTEX_AI_PROJECT")
    vertex_ai_location: str = Field(default="us-central1", env="VERTEX_AI_LOCATION")

    # External Services
    stripe_api_key: Optional[str] = Field(default=None, env="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    sendgrid_api_key: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")

    # Performance & Monitoring
    max_request_size: int = Field(default=10 * 1024 * 1024, env="MAX_REQUEST_SIZE")  # 10MB
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")  # seconds
    circuit_breaker_failure_threshold: int = Field(default=5, env="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: int = Field(default=60, env="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")  # per minute
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")

    # Enterprise Features
    enable_enterprise_features: bool = Field(default=True, env="ENABLE_ENTERPRISE_FEATURES")
    enterprise_license_key: Optional[str] = Field(default=None, env="ENTERPRISE_LICENSE_KEY")
    partner_api_keys: dict = Field(default_factory=dict, env="PARTNER_API_KEYS")

    # 3D Rendering & Frontend
    enable_3d_rendering: bool = Field(default=True, env="ENABLE_3D_RENDERING")
    max_3d_scene_complexity: int = Field(default=50000, env="MAX_3D_SCENE_COMPLEXITY")  # vertices
    webgl_debug: bool = Field(default=False, env="WEBGL_DEBUG")

    # File Storage
    upload_directory: str = Field(default="./uploads", env="UPLOAD_DIRECTORY")
    max_upload_size: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB

    @validator("debug", pre=True)
    def validate_debug(cls, v):
        """Validate debug setting"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @validator("allowed_origins", pre=True)
    def validate_allowed_origins(cls, v):
        """Parse comma-separated allowed origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("partner_api_keys", pre=True)
    def validate_partner_api_keys(cls, v):
        """Parse JSON partner API keys"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Ensure secret key is provided and secure"""
        if not v:
            raise ValueError("SECRET_KEY must be provided")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT

    @property
    def database_config(self) -> dict:
        """Get database configuration"""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "echo": self.debug
        }

    @property
    def redis_config(self) -> dict:
        """Get Redis configuration"""
        return {
            "url": self.redis_url,
            "encoding": "utf-8",
            "decode_responses": True,
            "max_connections": 20
        }

    @property
    def cors_config(self) -> dict:
        """Get CORS configuration"""
        origins = list(self.allowed_origins)

        # Add development origins in non-production
        if not self.is_production:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ])

        return {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["*"],
            "expose_headers": ["X-Request-ID", "X-Response-Time", "X-RateLimit-Remaining"]
        }

    @property
    def security_config(self) -> dict:
        """Get security configuration"""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.jwt_algorithm,
            "token_expiration_hours": self.jwt_expiration_hours,
            "encrypt_key": self.encrypt_key
        }

    @property
    def circuit_breaker_config(self) -> dict:
        """Get circuit breaker configuration"""
        return {
            "failure_threshold": self.circuit_breaker_failure_threshold,
            "recovery_timeout": self.circuit_breaker_recovery_timeout
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Environment-specific configurations
def get_environment_config(env: Environment) -> dict:
    """Get environment-specific configuration overrides"""
    configs = {
        Environment.DEVELOPMENT: {
            "debug": True,
            "log_level": LogLevel.DEBUG,
            "reload": True,
            "workers": 1,
            "enable_metrics": True
        },
        Environment.STAGING: {
            "debug": False,
            "log_level": LogLevel.INFO,
            "reload": False,
            "workers": 2,
            "enable_metrics": True
        },
        Environment.PRODUCTION: {
            "debug": False,
            "log_level": LogLevel.WARNING,
            "reload": False,
            "workers": 4,
            "enable_metrics": True
        }
    }
    return configs.get(env, {})


def validate_settings():
    """Validate settings for production readiness"""
    issues = []

    if settings.is_production:
        # Production-specific validations
        if settings.debug:
            issues.append("Debug mode should be disabled in production")

        if "localhost" in settings.database_url:
            issues.append("Production should not use localhost database")

        if not settings.encrypt_key:
            issues.append("Encryption key is required for production")

        if len(settings.allowed_origins) == 0:
            issues.append("Allowed origins must be configured for production")

    # General validations
    if not settings.secret_key:
        issues.append("Secret key is required")

    if issues:
        raise ValueError(f"Configuration validation failed: {'; '.join(issues)}")

    return True


# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    import logging
    logging.warning(f"Configuration issues detected: {e}")