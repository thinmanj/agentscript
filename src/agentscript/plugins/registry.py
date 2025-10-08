"""
Plugin Registry Helper

This module provides utility functions for working with the plugin registry.
"""

from .base import PluginRegistry

# Global registry instance
_registry = None

def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry instance."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
        # Auto-discover and register built-in plugins
        _registry.discover_plugins()
    return _registry