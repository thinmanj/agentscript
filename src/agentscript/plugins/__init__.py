"""
AgentScript Plugin System

This module provides a pluggable architecture for generating code in different
target frameworks and interfaces from AgentScript source files.

Supported Targets:
- pandas (default): Pure pandas data processing
- django: Django web framework with models, views, and APIs
- fastapi: FastAPI async web framework with Pydantic models  
- flask: Flask web framework with SQLAlchemy and blueprints
- tui: Terminal User Interface applications using Rich/Textual
- cli: Command-line applications with argument parsing

Each plugin converts AgentScript 'intent' declarations into framework-specific
code structures while maintaining the original data processing logic.
"""

from .base import BasePlugin, PluginRegistry
from .registry import get_plugin_registry

__all__ = ['BasePlugin', 'PluginRegistry', 'get_plugin_registry']

# Plugin registry instance
_registry = None

def get_registry():
    """Get the global plugin registry instance."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
        # Auto-register built-in plugins
        _registry.discover_plugins()
    return _registry