"""
Tests for the main application module.
"""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile
import os

from python_template.main import app, TemplateApp
from python_template.config.settings import get_settings, reload_settings


class TestTemplateApp:
    """Test the main TemplateApp class."""

    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        template_app = TemplateApp()
        assert template_app.settings is not None
        assert hasattr(template_app, 'logger')

    def test_run_example(self, caplog):
        """Test the run_example method."""
        template_app = TemplateApp()
        template_app.run_example()

        # Check that log messages were created
        assert "Starting example task" in caplog.text
        assert "Example task completed successfully" in caplog.text


class TestCLI:
    """Test the CLI application."""

    def setup_method(self):
        """Setup test runner."""
        self.runner = CliRunner()

    def test_run_command(self):
        """Test the run command."""
        result = self.runner.invoke(app, ["run"])
        assert result.exit_code == 0

    def test_info_command(self):
        """Test the info command."""
        result = self.runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Python Template Information" in result.stdout

    def test_config_command(self):
        """Test the config command."""
        result = self.runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Current Configuration" in result.stdout

    def test_test_logging_command(self):
        """Test the test-logging command."""
        result = self.runner.invoke(app, ["test-logging"])
        assert result.exit_code == 0
        assert "Testing logging at different levels" in result.stdout

    def test_run_with_log_level(self):
        """Test run command with log level override."""
        result = self.runner.invoke(app, ["run", "--log-level", "DEBUG"])
        assert result.exit_code == 0

    def test_run_with_environment(self):
        """Test run command with environment override."""
        result = self.runner.invoke(app, ["run", "--env", "testing"])
        assert result.exit_code == 0

    def test_init_project_command(self):
        """Test the init-project command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = self.runner.invoke(
                app,
                ["init-project", "test-project", "--dir", str(temp_path)]
            )
            assert result.exit_code == 0

            # Check that project directory was created
            project_path = temp_path / "test-project"
            assert project_path.exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "config").exists()

    def test_init_project_existing_directory(self):
        """Test init-project command with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            existing_project = temp_path / "existing-project"
            existing_project.mkdir()

            result = self.runner.invoke(
                app,
                ["init-project", "existing-project", "--dir", str(temp_path)]
            )
            assert result.exit_code == 1
            assert "already exists" in result.stdout


class TestIntegration:
    """Integration tests for the complete application."""

    def test_settings_integration(self):
        """Test that settings are properly integrated."""
        template_app = TemplateApp()
        settings = template_app.settings

        # Test that settings are loaded
        assert settings.app_name == "Python Template"
        assert settings.version == "0.1.0"

    def test_logging_integration(self):
        """Test that logging is properly integrated."""
        template_app = TemplateApp()

        # Test that logger is available
        assert hasattr(template_app, 'logger')

        # Test that we can log messages
        template_app.logger.info("Test message")

    def test_environment_override(self):
        """Test environment variable overrides."""
        # Set environment variable
        os.environ["ENVIRONMENT"] = "testing"

        try:
            # Reload settings to pick up environment change
            reload_settings()
            settings = get_settings()

            assert settings.environment.value == "testing"
        finally:
            # Clean up
            if "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            reload_settings()


# Fixtures for common test data
@pytest.fixture
def sample_config():
    """Provide sample configuration data."""
    return {
        "app_name": "Test App",
        "version": "1.0.0",
        "debug": True,
        "log_level": "DEBUG"
    }


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary configuration file."""
    import yaml

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_config, f)
        temp_file = f.name

    yield Path(temp_file)

    # Cleanup
    Path(temp_file).unlink(missing_ok=True)
