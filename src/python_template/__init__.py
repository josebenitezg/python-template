"""
Python Template - A modern Python project template.

This package provides a well-structured foundation for Python projects with:
- Custom logging configuration
- Environment-based configuration management
- Type hints and modern Python practices
- UV package management
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .logger import get_logger
from .config.settings import get_settings

__all__ = ["get_logger", "get_settings", "__version__"]
