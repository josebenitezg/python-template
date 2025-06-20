"""
Tests for the logger module.
"""

import pytest
import logging
import tempfile
from pathlib import Path

from python_template.logger import (
    get_logger,
    setup_logging,
    LoggerMixin,
    log_function_call,
    load_logging_config,
    get_default_logging_config
)


class TestLoggerFunctions:
    """Test logger utility functions."""

    def test_get_logger_default_name(self):
        """Test getting a logger with default name."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "python_template.logger"

    def test_get_logger_custom_name(self):
        """Test getting a logger with custom name."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_default_logging_config(self):
        """Test default logging configuration."""
        config = get_default_logging_config()

        assert isinstance(config, dict)
        assert config["version"] == 1
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config
        assert "root" in config

    def test_load_logging_config_nonexistent_file(self):
        """Test loading config from non-existent file."""
        config = load_logging_config(Path("/nonexistent/path.yaml"))

        # Should return default config
        default_config = get_default_logging_config()
        assert config == default_config

    def test_setup_logging_with_overrides(self):
        """Test setup logging with parameter overrides."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            setup_logging(log_level="DEBUG", log_file=log_file)

            # Test that log file was created
            assert log_file.parent.exists()


class TestLoggerMixin:
    """Test the LoggerMixin class."""

    def test_logger_mixin(self):
        """Test that LoggerMixin provides logger property."""
        class TestClass(LoggerMixin):
            def test_method(self):
                return self.logger.name

        test_obj = TestClass()
        assert hasattr(test_obj, 'logger')
        assert isinstance(test_obj.logger, logging.Logger)
        assert "TestClass" in test_obj.logger.name

    def test_logger_mixin_caching(self):
        """Test that logger is cached on the instance."""
        class TestClass(LoggerMixin):
            pass

        test_obj = TestClass()
        logger1 = test_obj.logger
        logger2 = test_obj.logger

        # Should be the same instance
        assert logger1 is logger2


class TestLogFunctionCallDecorator:
    """Test the log_function_call decorator."""

    def test_function_call_logging(self, caplog):
        """Test that function calls are logged."""
        @log_function_call
        def test_function(x, y):
            return x + y

        result = test_function(1, 2)

        assert result == 3
        assert "Calling" in caplog.text
        assert "test_function" in caplog.text
        assert "returned" in caplog.text

    def test_function_exception_logging(self, caplog):
        """Test that function exceptions are logged."""
        @log_function_call
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        assert "failing_function" in caplog.text
        assert "raised ValueError" in caplog.text
        assert "Test error" in caplog.text


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_to_file(self):
        """Test that logging to file works."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            setup_logging(log_file=log_file)
            logger = get_logger("test")

            logger.info("Test message")

            # Check that log file was created and contains message
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_different_log_levels(self, caplog):
        """Test logging at different levels."""
        logger = get_logger("test")

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Check that messages were logged
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text
