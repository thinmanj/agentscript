"""
Interactive TUI for AgentScript Configuration

Provides an interactive terminal interface for selecting plugins and
configuring options when generating code from AgentScript files.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import sys

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich import box
    from rich.markdown import Markdown
except ImportError:
    print("Error: Rich library is required for interactive mode.", file=sys.stderr)
    print("Install with: pip install rich", file=sys.stderr)
    sys.exit(1)

from .plugins import get_registry
from .config import AgentScriptConfig, ConfigManager, ConfigFormat


console = Console()


class InteractiveConfigWizard:
    """Interactive wizard for configuring AgentScript plugins"""
    
    def __init__(self):
        self.registry = get_registry()
        self.config = AgentScriptConfig()
        self.console = console
    
    def run(self, source_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run the interactive configuration wizard
        
        Args:
            source_file: Optional AgentScript source file path
            
        Returns:
            Configuration dictionary with selected options
        """
        self._show_welcome()
        
        # Step 1: Select plugin/target framework
        plugin_name = self._select_plugin()
        
        # Step 2: Configure basic settings
        app_name = self._configure_app_name()
        
        # Step 3: Configure database
        database_config = self._configure_database(plugin_name)
        
        # Step 4: Configure authentication
        auth_config = self._configure_authentication(plugin_name)
        
        # Step 5: Configure API settings
        api_config = self._configure_api(plugin_name)
        
        # Step 6: Framework-specific options
        framework_options = self._configure_framework_specific(plugin_name)
        
        # Step 7: Review and confirm
        final_config = {
            'target': plugin_name,
            'app_name': app_name,
            'database': database_config,
            'authentication': auth_config,
            'api': api_config,
            **framework_options
        }
        
        if self._review_configuration(final_config):
            # Step 8: Save configuration
            self._save_configuration_prompt(final_config)
            return final_config
        else:
            console.print("[yellow]Configuration cancelled[/yellow]")
            return {}
    
    def _show_welcome(self):
        """Display welcome screen"""
        welcome_text = """
# 🚀 AgentScript Interactive Configuration Wizard

Welcome! This wizard will help you configure AgentScript to generate
applications for your chosen framework.

You'll be guided through selecting a target framework, configuring
databases, authentication, APIs, and framework-specific options.
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="Welcome",
            border_style="bright_blue",
            box=box.ROUNDED
        ))
        self.console.print()
    
    def _select_plugin(self) -> str:
        """Interactive plugin selection"""
        plugins = self.registry.list_plugins()
        
        if not plugins:
            console.print("[red]Error: No plugins available[/red]")
            sys.exit(1)
        
        # Display plugins table
        table = Table(title="Available Plugins", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Plugin", style="green bold")
        table.add_column("Description", style="white")
        table.add_column("Features", style="yellow")
        
        for idx, plugin_name in enumerate(sorted(plugins), 1):
            info = self.registry.get_plugin_info(plugin_name)
            if info:
                features = []
                if info['supports_web']:
                    features.append("🌐 Web")
                if info['supports_async']:
                    features.append("⚡ Async")
                if info['supports_database']:
                    features.append("💾 DB")
                if info['supports_auth']:
                    features.append("🔐 Auth")
                
                table.add_row(
                    str(idx),
                    plugin_name.capitalize(),
                    info['description'][:50] + "..." if len(info['description']) > 50 else info['description'],
                    " ".join(features)
                )
        
        console.print(table)
        console.print()
        
        # Get user selection
        while True:
            choice = Prompt.ask(
                "Select a plugin",
                choices=[str(i) for i in range(1, len(plugins) + 1)]
            )
            selected_plugin = sorted(plugins)[int(choice) - 1]
            
            # Show detailed plugin info
            info = self.registry.get_plugin_info(selected_plugin)
            self._show_plugin_details(selected_plugin, info)
            
            if Confirm.ask(f"Use [bold green]{selected_plugin}[/bold green]?", default=True):
                return selected_plugin
    
    def _show_plugin_details(self, name: str, info: Dict[str, Any]):
        """Show detailed plugin information"""
        tree = Tree(f"[bold cyan]{name.capitalize()}[/bold cyan] Plugin")
        tree.add(f"[dim]Version:[/dim] {info['version']}")
        tree.add(f"[dim]Description:[/dim] {info['description']}")
        
        capabilities = tree.add("[yellow]Capabilities[/yellow]")
        if info['supports_web']:
            capabilities.add("🌐 Web Framework")
        if info['supports_async']:
            capabilities.add("⚡ Async/Await Support")
        if info['supports_database']:
            capabilities.add("💾 Database Integration")
        if info['supports_auth']:
            capabilities.add("🔐 Authentication")
        
        if info['dependencies']:
            deps = tree.add("[blue]Dependencies[/blue]")
            for dep in info['dependencies'][:5]:  # Show first 5
                deps.add(f"📦 {dep}")
        
        console.print(Panel(tree, box=box.ROUNDED))
        console.print()
    
    def _configure_app_name(self) -> str:
        """Configure application name"""
        console.print("\n[bold cyan]Application Configuration[/bold cyan]")
        
        app_name = Prompt.ask(
            "Enter application name",
            default="myapp"
        )
        
        # Validate and sanitize
        app_name = app_name.lower().replace(" ", "_").replace("-", "_")
        console.print(f"✓ Application name: [green]{app_name}[/green]\n")
        
        return app_name
    
    def _configure_database(self, plugin_name: str) -> Dict[str, Any]:
        """Configure database settings"""
        plugin_info = self.registry.get_plugin_info(plugin_name)
        
        if not plugin_info or not plugin_info['supports_database']:
            return {'enabled': False}
        
        console.print("\n[bold cyan]Database Configuration[/bold cyan]")
        
        if not Confirm.ask("Enable database?", default=True):
            return {'enabled': False}
        
        # Select database engine
        db_engines = {
            '1': 'sqlite',
            '2': 'postgresql',
            '3': 'mysql'
        }
        
        console.print("\n[yellow]Database Engines:[/yellow]")
        console.print("  1. SQLite (file-based, no server required)")
        console.print("  2. PostgreSQL (recommended for production)")
        console.print("  3. MySQL (alternative production option)")
        
        choice = Prompt.ask(
            "\nSelect database engine",
            choices=['1', '2', '3'],
            default='1'
        )
        
        engine = db_engines[choice]
        
        config = {
            'enabled': True,
            'engine': engine
        }
        
        if engine == 'sqlite':
            db_name = Prompt.ask("Database file name", default="app.db")
            config['name'] = db_name
        else:
            config['name'] = Prompt.ask("Database name", default="agentscript_db")
            config['host'] = Prompt.ask("Database host", default="localhost")
            config['port'] = IntPrompt.ask(
                "Database port",
                default=5432 if engine == 'postgresql' else 3306
            )
            config['user'] = Prompt.ask("Database user", default="dbuser")
            
            console.print("[dim]Note: Set password via DATABASE_PASSWORD environment variable[/dim]")
        
        console.print(f"✓ Database: [green]{engine}[/green]\n")
        return config
    
    def _configure_authentication(self, plugin_name: str) -> Dict[str, Any]:
        """Configure authentication settings"""
        plugin_info = self.registry.get_plugin_info(plugin_name)
        
        if not plugin_info or not plugin_info['supports_auth']:
            return {'enabled': False}
        
        console.print("\n[bold cyan]Authentication Configuration[/bold cyan]")
        
        if not Confirm.ask("Enable authentication?", default=False):
            return {'enabled': False}
        
        config = {'enabled': True}
        
        config['allow_registration'] = Confirm.ask(
            "Allow user registration?",
            default=True
        )
        
        config['require_email_verification'] = Confirm.ask(
            "Require email verification?",
            default=False
        )
        
        config['password_min_length'] = IntPrompt.ask(
            "Minimum password length",
            default=8
        )
        
        config['token_expiry_hours'] = IntPrompt.ask(
            "Token expiry (hours)",
            default=24
        )
        
        console.print("[dim]Note: Set SECRET_KEY via environment variable[/dim]")
        console.print("✓ Authentication enabled\n")
        
        return config
    
    def _configure_api(self, plugin_name: str) -> Dict[str, Any]:
        """Configure API settings"""
        plugin_info = self.registry.get_plugin_info(plugin_name)
        
        if not plugin_info or not plugin_info['supports_web']:
            return {'enabled': False}
        
        console.print("\n[bold cyan]API Configuration[/bold cyan]")
        
        if not Confirm.ask("Enable REST API?", default=True):
            return {'enabled': False}
        
        config = {'enabled': True}
        
        config['host'] = Prompt.ask("API host", default="0.0.0.0")
        config['port'] = IntPrompt.ask("API port", default=8000)
        
        config['cors_enabled'] = Confirm.ask(
            "Enable CORS?",
            default=True
        )
        
        if config['cors_enabled']:
            console.print("[dim]CORS origins can be configured in the config file[/dim]")
        
        config['enable_docs'] = Confirm.ask(
            "Enable API documentation?",
            default=True
        )
        
        console.print("✓ API configured\n")
        return config
    
    def _configure_framework_specific(self, plugin_name: str) -> Dict[str, Any]:
        """Configure framework-specific options"""
        console.print(f"\n[bold cyan]{plugin_name.capitalize()}-Specific Options[/bold cyan]")
        
        options = {}
        
        if plugin_name == 'django':
            options['admin'] = Confirm.ask("Enable Django Admin?", default=True)
            options['rest_framework'] = Confirm.ask("Use Django REST Framework?", default=True)
            options['celery'] = Confirm.ask("Enable Celery for async tasks?", default=False)
        
        elif plugin_name == 'fastapi':
            options['async_mode'] = Confirm.ask("Use async/await?", default=True)
            options['sql_model'] = Confirm.ask("Use SQLModel?", default=True)
            options['background_tasks'] = Confirm.ask("Enable background tasks?", default=True)
        
        elif plugin_name == 'flask':
            options['admin'] = Confirm.ask("Enable Flask-Admin?", default=True)
            options['blueprints'] = Confirm.ask("Use blueprints?", default=True)
            options['migrate'] = Confirm.ask("Enable Flask-Migrate?", default=True)
        
        elif plugin_name == 'tui':
            themes = {
                '1': 'dark',
                '2': 'light',
                '3': 'monokai'
            }
            console.print("\n[yellow]Themes:[/yellow]")
            console.print("  1. Dark")
            console.print("  2. Light")
            console.print("  3. Monokai")
            
            theme_choice = Prompt.ask("Select theme", choices=['1', '2', '3'], default='1')
            options['theme'] = themes[theme_choice]
            
            options['enable_mouse'] = Confirm.ask("Enable mouse support?", default=True)
            options['refresh_rate'] = IntPrompt.ask("Refresh rate (ms)", default=1000)
        
        if options:
            console.print("✓ Framework options configured\n")
        
        return options
    
    def _review_configuration(self, config: Dict[str, Any]) -> bool:
        """Review and confirm configuration"""
        console.print("\n[bold cyan]Configuration Review[/bold cyan]\n")
        
        # Create configuration tree
        tree = Tree("📋 [bold]Final Configuration[/bold]")
        
        tree.add(f"[cyan]Target:[/cyan] {config['target']}")
        tree.add(f"[cyan]App Name:[/cyan] {config['app_name']}")
        
        if config.get('database', {}).get('enabled'):
            db_branch = tree.add("[yellow]Database[/yellow]")
            db_config = config['database']
            db_branch.add(f"Engine: {db_config['engine']}")
            db_branch.add(f"Name: {db_config.get('name', 'N/A')}")
            if 'host' in db_config:
                db_branch.add(f"Host: {db_config['host']}:{db_config.get('port', 'N/A')}")
        
        if config.get('authentication', {}).get('enabled'):
            auth_branch = tree.add("[green]Authentication[/green]")
            auth_config = config['authentication']
            auth_branch.add(f"Registration: {'Enabled' if auth_config.get('allow_registration') else 'Disabled'}")
            auth_branch.add(f"Email Verification: {'Required' if auth_config.get('require_email_verification') else 'Optional'}")
            auth_branch.add(f"Min Password Length: {auth_config.get('password_min_length', 8)}")
        
        if config.get('api', {}).get('enabled'):
            api_branch = tree.add("[blue]API[/blue]")
            api_config = config['api']
            api_branch.add(f"Host: {api_config.get('host', '0.0.0.0')}")
            api_branch.add(f"Port: {api_config.get('port', 8000)}")
            api_branch.add(f"CORS: {'Enabled' if api_config.get('cors_enabled') else 'Disabled'}")
            api_branch.add(f"Documentation: {'Enabled' if api_config.get('enable_docs') else 'Disabled'}")
        
        # Framework-specific options
        framework_keys = [k for k in config.keys() 
                         if k not in ['target', 'app_name', 'database', 'authentication', 'api']]
        if framework_keys:
            fw_branch = tree.add("[magenta]Framework Options[/magenta]")
            for key in framework_keys:
                fw_branch.add(f"{key}: {config[key]}")
        
        console.print(Panel(tree, box=box.ROUNDED))
        console.print()
        
        return Confirm.ask("Proceed with this configuration?", default=True)
    
    def _save_configuration_prompt(self, config: Dict[str, Any]):
        """Prompt to save configuration to file"""
        console.print("\n[bold cyan]Save Configuration[/bold cyan]")
        
        if not Confirm.ask("Save configuration to file?", default=True):
            return
        
        # Select format
        formats = {
            '1': ('yaml', ConfigFormat.YAML),
            '2': ('json', ConfigFormat.JSON),
            '3': ('toml', ConfigFormat.TOML)
        }
        
        console.print("\n[yellow]Configuration Formats:[/yellow]")
        console.print("  1. YAML (recommended)")
        console.print("  2. JSON")
        console.print("  3. TOML")
        
        format_choice = Prompt.ask(
            "Select format",
            choices=['1', '2', '3'],
            default='1'
        )
        
        ext, format_enum = formats[format_choice]
        
        default_name = f"agentscript.{ext}"
        filename = Prompt.ask("Configuration filename", default=default_name)
        
        # Create config object and save
        full_config = AgentScriptConfig()
        full_config.plugin.target = config['target']
        full_config.plugin.app_name = config['app_name']
        
        if config.get('database', {}).get('enabled'):
            db = config['database']
            full_config.plugin.database.engine = db.get('engine', 'sqlite')
            full_config.plugin.database.name = db.get('name', 'app.db')
            if 'host' in db:
                full_config.plugin.database.host = db['host']
                full_config.plugin.database.port = db.get('port', 5432)
                full_config.plugin.database.user = db.get('user', '')
        
        if config.get('authentication', {}).get('enabled'):
            auth = config['authentication']
            full_config.plugin.authentication.enabled = True
            full_config.plugin.authentication.allow_registration = auth.get('allow_registration', True)
            full_config.plugin.authentication.require_email_verification = auth.get('require_email_verification', False)
            full_config.plugin.authentication.password_min_length = auth.get('password_min_length', 8)
            full_config.plugin.authentication.token_expiry_hours = auth.get('token_expiry_hours', 24)
        
        if config.get('api', {}).get('enabled'):
            api = config['api']
            full_config.plugin.api.enabled = True
            full_config.plugin.api.host = api.get('host', '0.0.0.0')
            full_config.plugin.api.port = api.get('port', 8000)
            full_config.plugin.api.cors_enabled = api.get('cors_enabled', True)
            full_config.plugin.api.enable_docs = api.get('enable_docs', True)
        
        # Save framework-specific options
        framework_opts = {k: v for k, v in config.items() 
                         if k not in ['target', 'app_name', 'database', 'authentication', 'api']}
        full_config.plugin.custom_options = framework_opts
        
        try:
            manager = ConfigManager()
            output_path = Path(filename)
            manager.save(full_config, output_path, format_enum)
            console.print(f"\n✅ Configuration saved to [green]{filename}[/green]")
        except Exception as e:
            console.print(f"\n[red]Error saving configuration: {e}[/red]")


def run_interactive_wizard(source_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run the interactive configuration wizard
    
    Args:
        source_file: Optional AgentScript source file
        
    Returns:
        Configuration dictionary
    """
    wizard = InteractiveConfigWizard()
    return wizard.run(source_file)


if __name__ == '__main__':
    # Test the wizard
    config = run_interactive_wizard()
    console.print("\n[bold green]Configuration complete![/bold green]")
    console.print(config)
