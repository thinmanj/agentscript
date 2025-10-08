"""
Base Plugin Architecture for AgentScript Code Generation

This module defines the abstract base classes and interfaces that all
AgentScript plugins must implement to generate code for different frameworks.
"""

import os
import importlib
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field

from ..ast_nodes import Program, IntentDeclaration


@dataclass
class PluginConfig:
    """Configuration settings for a plugin."""
    name: str
    description: str
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    templates_dir: Optional[Path] = None
    output_extension: str = ".py"
    supports_async: bool = False
    supports_web: bool = False
    supports_database: bool = False
    supports_auth: bool = False


@dataclass
class GenerationContext:
    """Context information passed to plugins during code generation."""
    source_file: Path
    output_dir: Path
    target_framework: str
    options: Dict[str, Any] = field(default_factory=dict)
    templates: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


class BasePlugin(ABC):
    """
    Abstract base class for all AgentScript code generation plugins.
    
    Each plugin must implement methods to generate framework-specific code
    from AgentScript AST nodes while maintaining data processing semantics.
    """
    
    def __init__(self, config: PluginConfig):
        self.config = config
        self._templates = {}
        self._load_templates()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name identifier."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable plugin description."""
        pass
    
    @abstractmethod
    def generate_code(self, ast: Program, context: GenerationContext) -> Dict[str, str]:
        """
        Generate framework-specific code from AgentScript AST.
        
        Args:
            ast: Parsed AgentScript program AST
            context: Generation context with options and paths
            
        Returns:
            Dictionary mapping file paths to generated code content
        """
        pass
    
    @abstractmethod
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """
        Get list of required dependencies for generated code.
        
        Args:
            context: Generation context
            
        Returns:
            List of dependency specifications (e.g., "django>=4.0", "fastapi[all]")
        """
        pass
    
    def supports_feature(self, feature: str) -> bool:
        """Check if plugin supports a specific feature."""
        return getattr(self.config, f'supports_{feature}', False)
    
    def validate_context(self, context: GenerationContext) -> List[str]:
        """
        Validate generation context and return any errors.
        
        Args:
            context: Generation context to validate
            
        Returns:
            List of error messages, empty if valid
        """
        errors = []
        
        # Check required dependencies are available
        for dep in self.config.dependencies:
            if not self._is_dependency_available(dep):
                errors.append(f"Required dependency not available: {dep}")
        
        return errors
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get a template by name."""
        return self._templates.get(template_name)
    
    def _load_templates(self):
        """Load templates from the plugin's templates directory."""
        if not self.config.templates_dir or not self.config.templates_dir.exists():
            return
            
        for template_file in self.config.templates_dir.glob("*.j2"):
            template_name = template_file.stem
            self._templates[template_name] = template_file.read_text(encoding='utf-8')
    
    def _is_dependency_available(self, dependency: str) -> bool:
        """Check if a dependency is available."""
        try:
            # Extract package name from dependency specification
            package_name = dependency.split('>=')[0].split('==')[0].split('[')[0]
            importlib.import_module(package_name.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def _generate_imports(self, ast: Program, context: GenerationContext) -> List[str]:
        """Generate import statements for the target framework."""
        return []
    
    def _generate_models(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate data models for the target framework."""
        return ""
    
    def _generate_views(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate views/endpoints for the target framework."""
        return ""
    
    def _generate_config(self, context: GenerationContext) -> str:
        """Generate configuration files for the target framework.""" 
        return ""


class PluginRegistry:
    """Registry for managing available code generation plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, Type[BasePlugin]] = {}
        self._instances: Dict[str, BasePlugin] = {}
    
    def register(self, plugin_class: Type[BasePlugin]):
        """Register a plugin class."""
        # Create temporary instance to get name
        temp_config = PluginConfig(
            name=getattr(plugin_class, 'plugin_name', plugin_class.__name__),
            description=getattr(plugin_class, 'plugin_description', ''),
        )
        temp_instance = plugin_class(temp_config)
        
        self._plugins[temp_instance.name] = plugin_class
    
    def get_plugin(self, name: str, **config_overrides) -> Optional[BasePlugin]:
        """Get a plugin instance by name."""
        if name not in self._plugins:
            return None
            
        # Use cached instance or create new one
        cache_key = f"{name}_{hash(str(sorted(config_overrides.items())))}"
        
        if cache_key not in self._instances:
            plugin_class = self._plugins[name]
            
            # Get default config and apply overrides
            config = self._get_plugin_config(name, plugin_class)
            for key, value in config_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            self._instances[cache_key] = plugin_class(config)
        
        return self._instances[cache_key]
    
    def list_plugins(self) -> List[str]:
        """Get list of registered plugin names."""
        return list(self._plugins.keys())
    
    def get_plugin_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin."""
        if name not in self._plugins:
            return None
            
        plugin = self.get_plugin(name)
        if not plugin:
            return None
            
        return {
            'name': plugin.config.name,
            'description': plugin.config.description,
            'version': plugin.config.version,
            'dependencies': plugin.config.dependencies,
            'optional_dependencies': plugin.config.optional_dependencies,
            'output_extension': plugin.config.output_extension,
            'supports_async': plugin.config.supports_async,
            'supports_web': plugin.config.supports_web,
            'supports_database': plugin.config.supports_database,
            'supports_auth': plugin.config.supports_auth,
        }
    
    def discover_plugins(self):
        """Auto-discover and register plugins from the plugins directory."""
        plugins_dir = Path(__file__).parent
        
        for plugin_file in plugins_dir.glob("*_plugin.py"):
            module_name = f"agentscript.plugins.{plugin_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                # Find plugin classes in module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BasePlugin) and 
                        obj != BasePlugin and 
                        not obj.__name__.startswith('_')):
                        self.register(obj)
                        
            except ImportError as e:
                # Skip plugins with missing dependencies
                pass
    
    def _get_plugin_config(self, name: str, plugin_class: Type[BasePlugin]) -> PluginConfig:
        """Get default configuration for a plugin."""
        # Try to get config from plugin class attributes
        config = PluginConfig(
            name=getattr(plugin_class, 'plugin_name', name),
            description=getattr(plugin_class, 'plugin_description', ''),
            version=getattr(plugin_class, 'plugin_version', '1.0.0'),
            dependencies=getattr(plugin_class, 'plugin_dependencies', []),
            optional_dependencies=getattr(plugin_class, 'plugin_optional_dependencies', []),
            output_extension=getattr(plugin_class, 'plugin_output_extension', '.py'),
            supports_async=getattr(plugin_class, 'plugin_supports_async', False),
            supports_web=getattr(plugin_class, 'plugin_supports_web', False),
            supports_database=getattr(plugin_class, 'plugin_supports_database', False),
            supports_auth=getattr(plugin_class, 'plugin_supports_auth', False),
        )
        
        # Set templates directory
        templates_dir = Path(__file__).parent / "templates" / name
        if templates_dir.exists():
            config.templates_dir = templates_dir
            
        return config