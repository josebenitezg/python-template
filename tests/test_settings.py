"""
Tests for the settings and configuration module.
"""

import pytest
import os
import tempfile
from pathlib import Path
import yaml

from python_template.config.settings import (
    Settings,
    get_settings,
    reload_settings,
    Environment,
    LogLevel,
    DatabaseSettings,
    RedisSettings,
    APISettings,
)


class TestSettings:
    """Test the Settings class."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.app_name == "Python Template"
        assert settings.version == "0.1.0"
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.debug is False
        assert settings.log_level == LogLevel.INFO
        
    def test_environment_properties(self):
        """Test environment checking properties."""
        dev_settings = Settings(environment=Environment.DEVELOPMENT)
        prod_settings = Settings(environment=Environment.PRODUCTION)
        test_settings = Settings(environment=Environment.TESTING)
        
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        assert dev_settings.is_testing is False
        
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True
        assert prod_settings.is_testing is False
        
        assert test_settings.is_development is False
        assert test_settings.is_production is False
        assert test_settings.is_testing is True
        
    def test_database_url_override(self):
        """Test database URL override for testing."""
        settings = Settings(environment=Environment.TESTING)
        
        db_url = settings.get_database_url()
        assert db_url == "sqlite:///./test.db"
        
    def test_custom_settings(self):
        """Test custom settings functionality."""
        settings = Settings()
        
        # Test setting and getting custom settings
        settings.update_custom_setting("test_key", "test_value")
        assert settings.get_custom_setting("test_key") == "test_value"
        
        # Test default value
        assert settings.get_custom_setting("nonexistent", "default") == "default"
        
    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = Settings()
        settings_dict = settings.to_dict()
        
        assert isinstance(settings_dict, dict)
        assert "app_name" in settings_dict
        assert "version" in settings_dict
        assert "environment" in settings_dict
        

class TestEnvironmentOverrides:
    """Test environment variable overrides."""
    
    def test_environment_variable_override(self):
        """Test that environment variables override settings."""
        # Set environment variable
        os.environ["APP_NAME"] = "Test App Override"
        os.environ["DEBUG"] = "true"
        
        try:
            settings = Settings()
            assert settings.app_name == "Test App Override"
            assert settings.debug is True
        finally:
            # Clean up
            if "APP_NAME" in os.environ:
                del os.environ["APP_NAME"]
            if "DEBUG" in os.environ:
                del os.environ["DEBUG"]
                
    def test_nested_environment_override(self):
        """Test nested environment variable overrides."""
        os.environ["DB__URL"] = "postgresql://test:test@localhost/test"
        os.environ["API__PORT"] = "9000"
        
        try:
            settings = Settings()
            assert settings.database.url == "postgresql://test:test@localhost/test"
            assert settings.api.port == 9000
        finally:
            # Clean up
            if "DB__URL" in os.environ:
                del os.environ["DB__URL"]
            if "API__PORT" in os.environ:
                del os.environ["API__PORT"]


class TestYAMLConfiguration:
    """Test YAML configuration loading."""
    
    def test_yaml_config_loading(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "app_name": "YAML Test App",
            "debug": True,
            "custom_settings": {
                "test_key": "test_value"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_settings.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            # Mock the config directory path for this test
            original_load_yaml = Settings._load_yaml_settings
            
            def mock_load_yaml(self):
                with open(config_file) as f:
                    return yaml.safe_load(f) or {}
            
            Settings._load_yaml_settings = mock_load_yaml
            
            try:
                settings = Settings()
                assert settings.app_name == "YAML Test App"
                assert settings.debug is True
                assert settings.get_custom_setting("test_key") == "test_value"
            finally:
                Settings._load_yaml_settings = original_load_yaml


class TestSubSettings:
    """Test sub-settings classes."""
    
    def test_database_settings(self):
        """Test DatabaseSettings class."""
        db_settings = DatabaseSettings()
        
        assert db_settings.url == "sqlite:///./app.db"
        assert db_settings.pool_size == 5
        assert db_settings.max_overflow == 10
        assert db_settings.echo is False
        
    def test_redis_settings(self):
        """Test RedisSettings class."""
        redis_settings = RedisSettings()
        
        assert redis_settings.url == "redis://localhost:6379/0"
        assert redis_settings.max_connections == 20
        assert redis_settings.socket_timeout == 5.0
        
    def test_api_settings(self):
        """Test APISettings class."""
        api_settings = APISettings()
        
        assert api_settings.host == "localhost"
        assert api_settings.port == 8000
        assert api_settings.debug is False
        assert api_settings.reload is False
        assert api_settings.workers == 1
        
    def test_api_settings_secret_key_validation(self):
        """Test API settings secret key validation."""
        with pytest.raises(ValueError, match="Please set a proper secret key"):
            APISettings(secret_key="your-secret-key-here")
            
        with pytest.raises(ValueError, match="at least 32 characters"):
            APISettings(secret_key="short")
            
        # Should work with proper key
        api_settings = APISettings(secret_key="a" * 32)
        assert len(api_settings.secret_key) == 32


class TestSettingsCache:
    """Test settings caching functionality."""
    
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same instance
        assert settings1 is settings2
        
    def test_reload_settings(self):
        """Test settings reload functionality."""
        original_settings = get_settings()
        reloaded_settings = reload_settings()
        
        # Should be different instances after reload
        assert original_settings is not reloaded_settings
        
        # But get_settings should now return the new instance
        current_settings = get_settings()
        assert current_settings is reloaded_settings 