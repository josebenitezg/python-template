"""
Settings and configuration management using Pydantic Settings.

This module provides type-safe configuration management with support for:
- Environment variables
- YAML configuration files
- Environment-specific overrides
- Validation and type conversion
"""

import os
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    url: str = Field(default="sqlite:///./app.db", description="Database URL")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max connection overflow")
    echo: bool = Field(default=False, description="Echo SQL queries")

    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    max_connections: int = Field(default=20, description="Max Redis connections")
    socket_timeout: float = Field(default=5.0, description="Socket timeout in seconds")

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class APISettings(BaseSettings):
    """API configuration settings."""
    host: str = Field(default="localhost", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Auto-reload on changes")
    workers: int = Field(default=1, ge=1, description="Number of worker processes")

    # Security settings
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for signing")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"], description="Allowed hosts")
    cors_origins: List[str] = Field(default_factory=list, description="CORS allowed origins")

    model_config = SettingsConfigDict(env_prefix="API_")

    @validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        if v == "your-secret-key-here":
            raise ValueError("Please set a proper secret key")
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v


class Settings(BaseSettings):
    """
    Main application settings.

    This class centralizes all configuration management and supports:
    - Environment variable overrides
    - YAML file configuration
    - Environment-specific settings
    - Type validation and conversion
    """

    # Application settings
    app_name: str = Field(default="Python Template", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")

    # Logging settings
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file: Optional[Path] = Field(default=None, description="Log file path")
    log_rotation: bool = Field(default=True, description="Enable log rotation")
    log_max_size: str = Field(default="10MB", description="Max log file size")
    log_backup_count: int = Field(default=5, description="Number of log backups to keep")

    # Directory settings
    data_dir: Path = Field(default_factory=lambda: Path("data"), description="Data directory")
    cache_dir: Path = Field(default_factory=lambda: Path("cache"), description="Cache directory")
    temp_dir: Path = Field(default_factory=lambda: Path("tmp"), description="Temporary directory")

    # Feature flags
    enable_metrics: bool = Field(default=False, description="Enable metrics collection")
    enable_profiling: bool = Field(default=False, description="Enable profiling")
    enable_caching: bool = Field(default=True, description="Enable caching")

    # External service settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    api: APISettings = Field(default_factory=APISettings)

    # Custom settings (can be extended)
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom application settings")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow"
    )

    @validator("data_dir", "cache_dir", "temp_dir", pre=True)
    def ensure_path(cls, v: Any) -> Path:
        """Ensure directory paths are Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    @validator("environment", pre=True)
    def validate_environment(cls, v: Any) -> Environment:
        """Validate and normalize environment."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings with YAML file support."""
        # Load settings from YAML file if it exists
        yaml_settings = self._load_yaml_settings()

        # Merge with kwargs, giving priority to kwargs
        final_settings = {**yaml_settings, **kwargs}

        super().__init__(**final_settings)

        # Create directories if they don't exist
        self._create_directories()

    def _load_yaml_settings(self) -> Dict[str, Any]:
        """Load settings from YAML configuration files."""
        settings = {}

        # Project root directory
        project_root = Path(__file__).parent.parent.parent.parent
        config_dir = project_root / "config"

        # Load base settings
        base_config = config_dir / "settings.yaml"
        if base_config.exists():
            with open(base_config) as f:
                settings.update(yaml.safe_load(f) or {})

        # Load environment-specific settings
        env = os.getenv("ENVIRONMENT", "development").lower()
        env_config = config_dir / f"settings_{env}.yaml"
        if env_config.exists():
            with open(env_config) as f:
                env_settings = yaml.safe_load(f) or {}
                settings.update(env_settings)

        return settings

    def _create_directories(self) -> None:
        """Create necessary directories."""
        directories = [self.data_dir, self.cache_dir, self.temp_dir]

        if self.log_file:
            directories.append(self.log_file.parent)

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    def get_database_url(self) -> str:
        """Get database URL with environment-specific modifications."""
        if self.is_testing:
            return "sqlite:///./test.db"
        return self.database.url

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.dict()

    def update_custom_setting(self, key: str, value: Any) -> None:
        """Update a custom setting at runtime."""
        self.custom_settings[key] = value

    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get a custom setting value."""
        return self.custom_settings.get(key, default)


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function uses LRU cache to ensure we only create the settings instance once.
    Use this function throughout your application to get the current settings.

    Returns:
        Settings instance
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Reload settings by clearing the cache and creating a new instance.

    Useful for testing or when configuration changes at runtime.

    Returns:
        New Settings instance
    """
    get_settings.cache_clear()
    return get_settings()
