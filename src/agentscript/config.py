"""
AgentScript Configuration System

Provides centralized configuration management for AgentScript and its plugins.
Supports configuration files in YAML, JSON, and TOML formats with environment
variable override support.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ConfigFormat(Enum):
    """Supported configuration file formats"""
    YAML = "yaml"
    JSON = "json"
    TOML = "toml"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    engine: str = "sqlite"
    name: str = "agentscript.db"
    host: str = "localhost"
    port: int = 5432
    user: str = ""
    password: str = ""
    connection_pool_size: int = 10
    echo_sql: bool = False
    
    def get_connection_string(self) -> str:
        """Generate database connection string"""
        if self.engine == "sqlite":
            return f"sqlite:///{self.name}"
        elif self.engine == "postgresql":
            auth = f"{self.user}:{self.password}@" if self.user else ""
            return f"postgresql://{auth}{self.host}:{self.port}/{self.name}"
        elif self.engine == "mysql":
            auth = f"{self.user}:{self.password}@" if self.user else ""
            return f"mysql://{auth}{self.host}:{self.port}/{self.name}"
        else:
            raise ValueError(f"Unsupported database engine: {self.engine}")


@dataclass
class AuthenticationConfig:
    """Authentication and authorization configuration"""
    enabled: bool = False
    secret_key: str = ""
    token_expiry_hours: int = 24
    password_min_length: int = 8
    require_email_verification: bool = False
    allow_registration: bool = True
    session_timeout_minutes: int = 60
    jwt_algorithm: str = "HS256"


@dataclass
class APIConfig:
    """API configuration"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = False
    rate_limit_per_minute: int = 60
    enable_docs: bool = True
    api_prefix: str = "/api"


@dataclass
class PluginConfig:
    """Plugin-specific configuration"""
    target: str = "pandas"
    app_name: str = "myapp"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    authentication: AuthenticationConfig = field(default_factory=AuthenticationConfig)
    api: APIConfig = field(default_factory=APIConfig)
    enable_admin: bool = False
    enable_async: bool = False
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompilerConfig:
    """Compiler configuration"""
    optimization_level: int = 1
    generate_type_hints: bool = True
    strict_mode: bool = False
    output_format: str = "python"
    include_comments: bool = True
    code_style: str = "pep8"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class AgentScriptConfig:
    """Main AgentScript configuration"""
    version: str = "1.0.0"
    project_name: str = "agentscript_project"
    plugin: PluginConfig = field(default_factory=PluginConfig)
    compiler: CompilerConfig = field(default_factory=CompilerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    environment: str = "development"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentScriptConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        if 'version' in data:
            config.version = data['version']
        if 'project_name' in data:
            config.project_name = data['project_name']
        if 'environment' in data:
            config.environment = data['environment']
        
        # Parse plugin config
        if 'plugin' in data:
            plugin_data = data['plugin']
            config.plugin = PluginConfig(
                target=plugin_data.get('target', 'pandas'),
                app_name=plugin_data.get('app_name', 'myapp'),
                enable_admin=plugin_data.get('enable_admin', False),
                enable_async=plugin_data.get('enable_async', False),
                custom_options=plugin_data.get('custom_options', {})
            )
            
            # Parse database config
            if 'database' in plugin_data:
                db_data = plugin_data['database']
                config.plugin.database = DatabaseConfig(**db_data)
            
            # Parse authentication config
            if 'authentication' in plugin_data:
                auth_data = plugin_data['authentication']
                config.plugin.authentication = AuthenticationConfig(**auth_data)
            
            # Parse API config
            if 'api' in plugin_data:
                api_data = plugin_data['api']
                config.plugin.api = APIConfig(**api_data)
        
        # Parse compiler config
        if 'compiler' in data:
            config.compiler = CompilerConfig(**data['compiler'])
        
        # Parse logging config
        if 'logging' in data:
            config.logging = LoggingConfig(**data['logging'])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    def apply_env_overrides(self):
        """Apply environment variable overrides"""
        # Database overrides
        if os.getenv('DATABASE_ENGINE'):
            self.plugin.database.engine = os.getenv('DATABASE_ENGINE')
        if os.getenv('DATABASE_NAME'):
            self.plugin.database.name = os.getenv('DATABASE_NAME')
        if os.getenv('DATABASE_HOST'):
            self.plugin.database.host = os.getenv('DATABASE_HOST')
        if os.getenv('DATABASE_PORT'):
            self.plugin.database.port = int(os.getenv('DATABASE_PORT'))
        if os.getenv('DATABASE_USER'):
            self.plugin.database.user = os.getenv('DATABASE_USER')
        if os.getenv('DATABASE_PASSWORD'):
            self.plugin.database.password = os.getenv('DATABASE_PASSWORD')
        
        # Authentication overrides
        if os.getenv('SECRET_KEY'):
            self.plugin.authentication.secret_key = os.getenv('SECRET_KEY')
        if os.getenv('TOKEN_EXPIRY_HOURS'):
            self.plugin.authentication.token_expiry_hours = int(os.getenv('TOKEN_EXPIRY_HOURS'))
        
        # API overrides
        if os.getenv('API_HOST'):
            self.plugin.api.host = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            self.plugin.api.port = int(os.getenv('API_PORT'))
        if os.getenv('CORS_ORIGINS'):
            self.plugin.api.cors_origins = os.getenv('CORS_ORIGINS').split(',')
        
        # Logging overrides
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            self.logging.file = os.getenv('LOG_FILE')


class ConfigManager:
    """Manages configuration loading and saving"""
    
    DEFAULT_CONFIG_NAMES = [
        "agentscript.yaml",
        "agentscript.yml",
        "agentscript.json",
        "agentscript.toml",
        ".agentscript",
    ]
    
    def __init__(self):
        self._config: Optional[AgentScriptConfig] = None
        self._config_file: Optional[Path] = None
    
    def load(self, config_path: Optional[Path] = None, auto_discover: bool = True) -> AgentScriptConfig:
        """
        Load configuration from file or auto-discover
        
        Args:
            config_path: Explicit path to config file
            auto_discover: If True, search for config files in current directory
        
        Returns:
            Loaded configuration
        """
        if config_path:
            return self._load_from_file(config_path)
        
        if auto_discover:
            discovered = self._discover_config()
            if discovered:
                return self._load_from_file(discovered)
        
        # No config found, return default
        config = AgentScriptConfig()
        config.apply_env_overrides()
        return config
    
    def _discover_config(self) -> Optional[Path]:
        """Discover configuration file in current directory"""
        cwd = Path.cwd()
        
        for config_name in self.DEFAULT_CONFIG_NAMES:
            config_path = cwd / config_name
            if config_path.exists():
                return config_path
        
        return None
    
    def _load_from_file(self, config_path: Path) -> AgentScriptConfig:
        """Load configuration from specific file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine format from extension
        suffix = config_path.suffix.lower()
        
        if suffix in ['.yaml', '.yml']:
            return self._load_yaml(config_path)
        elif suffix == '.json':
            return self._load_json(config_path)
        elif suffix == '.toml':
            return self._load_toml(config_path)
        else:
            # Try JSON as fallback
            return self._load_json(config_path)
    
    def _load_json(self, config_path: Path) -> AgentScriptConfig:
        """Load JSON configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        config = AgentScriptConfig.from_dict(data)
        config.apply_env_overrides()
        self._config = config
        self._config_file = config_path
        return config
    
    def _load_yaml(self, config_path: Path) -> AgentScriptConfig:
        """Load YAML configuration"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            config = AgentScriptConfig.from_dict(data)
            config.apply_env_overrides()
            self._config = config
            self._config_file = config_path
            return config
        except ImportError:
            raise ImportError("PyYAML is required to load YAML config files. Install with: pip install pyyaml")
    
    def _load_toml(self, config_path: Path) -> AgentScriptConfig:
        """Load TOML configuration"""
        try:
            import tomllib if hasattr(__builtins__, 'tomllib') else __import__('tomli')  # Python 3.11+
            with open(config_path, 'rb') as f:
                data = tomllib.load(f) if hasattr(__builtins__, 'tomllib') else __import__('tomli').load(f)
            
            config = AgentScriptConfig.from_dict(data)
            config.apply_env_overrides()
            self._config = config
            self._config_file = config_path
            return config
        except ImportError:
            raise ImportError("tomli is required to load TOML config files. Install with: pip install tomli")
    
    def save(self, config: AgentScriptConfig, output_path: Path, format: ConfigFormat = ConfigFormat.YAML):
        """Save configuration to file"""
        data = config.to_dict()
        
        if format == ConfigFormat.JSON:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        elif format == ConfigFormat.YAML:
            try:
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            except ImportError:
                raise ImportError("PyYAML is required to save YAML config. Install with: pip install pyyaml")
        
        elif format == ConfigFormat.TOML:
            try:
                import tomli_w
                with open(output_path, 'wb') as f:
                    tomli_w.dump(data, f)
            except ImportError:
                raise ImportError("tomli-w is required to save TOML config. Install with: pip install tomli-w")
    
    def generate_default_config(self, output_path: Path, format: ConfigFormat = ConfigFormat.YAML):
        """Generate a default configuration file with comments"""
        config = AgentScriptConfig()
        self.save(config, output_path, format)


# Global config manager instance
_config_manager = ConfigManager()


def load_config(config_path: Optional[Path] = None) -> AgentScriptConfig:
    """Load configuration (convenience function)"""
    return _config_manager.load(config_path)


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance"""
    return _config_manager
