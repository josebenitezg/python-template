"""
Main CLI application for Python Template.

This module provides the command-line interface for the Python Template application
using Typer for modern CLI functionality.
"""

from typing import Optional
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .logger import get_logger, setup_logging, LoggerMixin
from .config.settings import get_settings, reload_settings, Environment

# Initialize Typer app
app = typer.Typer(
    name="python-template",
    help="A modern Python project template with logging and configuration management",
    add_completion=False,
)

# Rich console for output
console = Console()

# Logger for this module
logger = get_logger(__name__)


class TemplateApp(LoggerMixin):
    """Main application class with logging capabilities."""
    
    def __init__(self):
        """Initialize the application."""
        self.settings = get_settings()
        
    def run_example(self) -> None:
        """Run an example task to demonstrate the template."""
        self.logger.info("Starting example task")
        
        # Demonstrate configuration access
        self.logger.info(f"Application: {self.settings.app_name} v{self.settings.version}")
        self.logger.info(f"Environment: {self.settings.environment}")
        self.logger.info(f"Debug mode: {self.settings.debug}")
        
        # Demonstrate feature flags
        if self.settings.enable_metrics:
            self.logger.info("Metrics collection is enabled")
        
        if self.settings.enable_profiling:
            self.logger.info("Profiling is enabled")
            
        # Demonstrate custom settings
        batch_size = self.settings.get_custom_setting("batch_size", 100)
        self.logger.info(f"Processing with batch size: {batch_size}")
        
        # Simulate some work
        for i in range(3):
            self.logger.debug(f"Processing item {i + 1}")
            
        self.logger.info("Example task completed successfully")


@app.command()
def run(
    log_level: Optional[str] = typer.Option(
        None,
        "--log-level",
        "-l",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
    ),
    environment: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Set environment (development, staging, production, testing)",
    ),
) -> None:
    """Run the main application."""
    
    # Setup logging with command line overrides
    if log_level:
        setup_logging(log_level=log_level)
        logger.info(f"Log level set to {log_level}")
    
    # Override environment if specified
    if environment:
        import os
        os.environ["ENVIRONMENT"] = environment
        reload_settings()  # Reload settings with new environment
        logger.info(f"Environment set to {environment}")
    
    # Create and run the application
    template_app = TemplateApp()
    
    try:
        template_app.run_example()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def info() -> None:
    """Display application information."""
    settings = get_settings()
    
    # Create a rich table for displaying information
    table = Table(title="Python Template Information")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    # Application info
    table.add_row("Name", settings.app_name)
    table.add_row("Version", settings.version)
    table.add_row("Environment", settings.environment.value)
    table.add_row("Debug", str(settings.debug))
    
    # Directories
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Cache Directory", str(settings.cache_dir))
    table.add_row("Temp Directory", str(settings.temp_dir))
    
    # Feature flags
    table.add_row("Metrics Enabled", str(settings.enable_metrics))
    table.add_row("Profiling Enabled", str(settings.enable_profiling))
    table.add_row("Caching Enabled", str(settings.enable_caching))
    
    # Database info
    table.add_row("Database URL", settings.database.url)
    
    console.print(table)


@app.command()
def config() -> None:
    """Display current configuration."""
    settings = get_settings()
    
    console.print("[bold cyan]Current Configuration:[/bold cyan]")
    
    # Convert settings to dict and display as JSON-like structure
    config_dict = settings.to_dict()
    
    for key, value in config_dict.items():
        if isinstance(value, dict):
            console.print(f"[bold]{key}:[/bold]")
            for sub_key, sub_value in value.items():
                console.print(f"  {sub_key}: {sub_value}")
        else:
            console.print(f"[bold]{key}:[/bold] {value}")


@app.command()
def test_logging() -> None:
    """Test logging functionality at different levels."""
    logger = get_logger(__name__)
    
    console.print("[bold cyan]Testing logging at different levels:[/bold cyan]")
    
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")
    
    # Test structured logging
    logger.info("User action", extra={
        "user_id": "12345",
        "action": "login",
        "ip_address": "192.168.1.1"
    })
    
    console.print("[green]Logging test completed. Check console and log files.[/green]")


@app.command()
def init_project(
    name: str = typer.Argument(..., help="Project name"),
    directory: Optional[Path] = typer.Option(
        None,
        "--dir",
        "-d",
        help="Target directory (defaults to current directory)"
    ),
) -> None:
    """Initialize a new project from this template."""
    
    if directory is None:
        directory = Path.cwd()
    
    project_path = directory / name
    
    if project_path.exists():
        console.print(f"[red]Error: Directory {project_path} already exists[/red]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Creating new project '{name}' in {project_path}[/cyan]")
    
    # This is a placeholder - in a real template, you'd copy the template structure
    # and customize it for the new project
    project_path.mkdir(parents=True)
    
    # Create basic structure
    (project_path / "src").mkdir()
    (project_path / "tests").mkdir()
    (project_path / "config").mkdir()
    (project_path / "data").mkdir()
    (project_path / "logs").mkdir()
    
    console.print(f"[green]Project '{name}' created successfully at {project_path}[/green]")


def main() -> None:
    """Entry point for the application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    main() 