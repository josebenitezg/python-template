"""
Custom logging configuration for the Python Template.

This module provides a flexible logging system that supports:
- YAML-based configuration
- Rich console formatting
- File and console handlers
- Environment-specific log levels
- Structured logging with context
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from rich.console import Console
from rich.logging import RichHandler

# Global console instance for rich formatting
console = Console()

# Cache for configured loggers
_loggers: Dict[str, logging.Logger] = {}


def load_logging_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load logging configuration from YAML file.

    Args:
        config_path: Path to the logging configuration file.
                    If None, uses default config/logging.yaml

    Returns:
        Dictionary containing logging configuration
    """
    if config_path is None:
        # Default to config/logging.yaml in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "logging.yaml"

    if not config_path.exists():
        # Return default configuration if file doesn't exist
        return get_default_logging_config()

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config if config is not None else get_default_logging_config()
    except Exception as e:
        print(f"Warning: Could not load logging config from {config_path}: {e}")
        return get_default_logging_config()


def get_default_logging_config() -> Dict[str, Any]:
    """
    Get default logging configuration.

    Returns:
        Default logging configuration dictionary
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'rich.logging.RichHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'show_path': False,
                'show_time': False,
                'rich_tracebacks': True,
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
            },
        },
        'loggers': {
            'python_template': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False,
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console'],
        }
    }


def setup_logging(
    config_path: Optional[Path] = None,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> None:
    """
    Setup logging configuration.

    Args:
        config_path: Path to logging configuration file
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Override log file path
    """
    # Load configuration
    config = load_logging_config(config_path)

    # Override log level if provided
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
        config['root']['level'] = level
        if 'python_template' in config['loggers']:
            config['loggers']['python_template']['level'] = level

    # Override log file if provided
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        if 'file' in config['handlers']:
            config['handlers']['file']['filename'] = str(log_file)

    # Ensure log directory exists
    if 'file' in config['handlers']:
        log_path = Path(config['handlers']['file']['filename'])
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Apply configuration
    try:
        logging.config.dictConfig(config)
    except Exception as e:
        # Fallback to basic configuration if YAML config fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                RichHandler(console=console, show_path=False, show_time=False),
            ]
        )
        logging.getLogger(__name__).warning(
            f"Could not apply logging config, using basic config: {e}"
        )


def get_logger(
    name: Optional[str] = None,
    setup_if_needed: bool = True
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name. If None, uses the calling module's name
        setup_if_needed: Whether to setup logging if not already configured

    Returns:
        Configured logger instance
    """
    if name is None:
        # Get the calling module's name
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', 'python_template')

    # Check if we already have this logger configured
    if name in _loggers:
        return _loggers[name]

    # Setup logging if needed and not already done
    if setup_if_needed and not logging.getLogger().handlers:
        setup_logging()

    # Create and cache logger
    logger = logging.getLogger(name)
    _loggers[name] = logger

    return logger


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.

    Usage:
        class MyClass(LoggerMixin):
            def some_method(self):
                self.logger.info("This is a log message")
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        if not hasattr(self, '_logger'):
            class_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
            self._logger = get_logger(class_name)
        return self._logger


def log_function_call(func: Any) -> Any:
    """
    Decorator to log function calls with arguments and return values.

    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return "result"
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = get_logger(func.__module__)
        func_name = f"{func.__module__}.{func.__name__}"

        # Log function entry
        args_str = ', '.join([repr(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))

        logger.debug(f"Calling {func_name}({all_args})")

        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {repr(result)}")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised {type(e).__name__}: {e}")
            raise

    return wrapper


# Initialize logging on import
setup_logging()
