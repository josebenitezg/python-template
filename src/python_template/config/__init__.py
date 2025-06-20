"""
Configuration management for Python Template.

This package provides environment-based configuration management using Pydantic Settings.
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
