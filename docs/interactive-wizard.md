# Interactive Configuration Wizard

The AgentScript interactive wizard provides a user-friendly terminal interface for configuring your project. It guides you through selecting plugins, configuring options, and generating configuration files.

## Overview

The wizard is a step-by-step interface that helps you:

1. **Select a target framework** (Django, FastAPI, Flask, TUI, or Pandas)
2. **Configure application settings** (name, database, authentication, API)
3. **Choose framework-specific options** (admin interfaces, async support, themes)
4. **Review your configuration** before proceeding
5. **Save configuration** to a file (YAML, JSON, or TOML)

## Getting Started

### Prerequisites

The interactive wizard requires the `rich` library:

```bash
pip install rich
```

### Basic Usage

Run the wizard with:

```bash
agentscript init
```

Or with an optional AgentScript source file:

```bash
agentscript init pipeline.ags
```

## Wizard Steps

### Step 1: Welcome Screen

The wizard displays a welcome message explaining what it will help you configure.

### Step 2: Plugin Selection

Choose your target framework from the available plugins:

```
Available Plugins
┌───┬──────────┬─────────────────────────┬───────────────────────┐
│ # │ Plugin   │ Description             │ Features              │
├───┼──────────┼─────────────────────────┼───────────────────────┤
│ 1 │ Django   │ Generate Django web...  │ 🌐 Web 💾 DB 🔐 Auth │
│ 2 │ Fastapi  │ Generate modern async...│ ⚡ Async 🌐 Web ...  │
│ 3 │ Flask    │ Generate Flask web...   │ 🌐 Web 💾 DB 🔐 Auth │
│ 4 │ Tui      │ Generate interactive... │ ⚡ Async              │
└───┴──────────┴─────────────────────────┴───────────────────────┘

Select a plugin: 
```

After selecting, you'll see detailed information about the plugin including:
- Version
- Full description
- Capabilities (Web, Async, Database, Auth)
- Dependencies

### Step 3: Application Name

Configure your application name:

```
Application Configuration
Enter application name [myapp]: data_pipeline
✓ Application name: data_pipeline
```

The wizard automatically sanitizes the name (lowercase, underscores).

### Step 4: Database Configuration

For plugins that support databases:

```
Database Configuration
Enable database? [y/n] (y): y

Database Engines:
  1. SQLite (file-based, no server required)
  2. PostgreSQL (recommended for production)
  3. MySQL (alternative production option)

Select database engine [1/2/3] (1): 2
Database name [agentscript_db]: myapp_db
Database host [localhost]: localhost
Database port (5432): 5432
Database user [dbuser]: admin

Note: Set password via DATABASE_PASSWORD environment variable
✓ Database: postgresql
```

### Step 5: Authentication Configuration

For plugins that support authentication:

```
Authentication Configuration
Enable authentication? [y/n] (n): y
Allow user registration? [y/n] (y): y
Require email verification? [y/n] (n): n
Minimum password length (8): 12
Token expiry (hours) (24): 48

Note: Set SECRET_KEY via environment variable
✓ Authentication enabled
```

### Step 6: API Configuration

For web framework plugins:

```
API Configuration
Enable REST API? [y/n] (y): y
API host [0.0.0.0]: 0.0.0.0
API port (8000): 8000
Enable CORS? [y/n] (y): y
Note: CORS origins can be configured in the config file
Enable API documentation? [y/n] (y): y
✓ API configured
```

### Step 7: Framework-Specific Options

Each framework has specific options:

#### Django

```
Django-Specific Options
Enable Django Admin? [y/n] (y): y
Use Django REST Framework? [y/n] (y): y
Enable Celery for async tasks? [y/n] (n): n
✓ Framework options configured
```

#### FastAPI

```
FastAPI-Specific Options
Use async/await? [y/n] (y): y
Use SQLModel? [y/n] (y): y
Enable background tasks? [y/n] (y): y
✓ Framework options configured
```

#### Flask

```
Flask-Specific Options
Enable Flask-Admin? [y/n] (y): y
Use blueprints? [y/n] (y): y
Enable Flask-Migrate? [y/n] (y): y
✓ Framework options configured
```

#### TUI

```
TUI-Specific Options

Themes:
  1. Dark
  2. Light
  3. Monokai

Select theme [1/2/3] (1): 1
Enable mouse support? [y/n] (y): y
Refresh rate (ms) (1000): 500
✓ Framework options configured
```

### Step 8: Configuration Review

Review all your selections in a tree view:

```
Configuration Review

┌─ 📋 Final Configuration ─────────────────────┐
│ Target: django                                │
│ App Name: data_pipeline                       │
│ ├─ Database                                   │
│ │  ├─ Engine: postgresql                      │
│ │  ├─ Name: myapp_db                         │
│ │  └─ Host: localhost:5432                   │
│ ├─ Authentication                             │
│ │  ├─ Registration: Enabled                   │
│ │  ├─ Email Verification: Optional           │
│ │  └─ Min Password Length: 12                │
│ ├─ API                                        │
│ │  ├─ Host: 0.0.0.0                          │
│ │  ├─ Port: 8000                             │
│ │  ├─ CORS: Enabled                          │
│ │  └─ Documentation: Enabled                 │
│ └─ Framework Options                          │
│    ├─ admin: True                            │
│    └─ rest_framework: True                   │
└───────────────────────────────────────────────┘

Proceed with this configuration? [y/n] (y):
```

### Step 9: Save Configuration

Choose how to save your configuration:

```
Save Configuration
Save configuration to file? [y/n] (y): y

Configuration Formats:
  1. YAML (recommended)
  2. JSON
  3. TOML

Select format [1/2/3] (1): 1
Configuration filename [agentscript.yaml]: agentscript.yaml

✅ Configuration saved to agentscript.yaml

✅ Configuration complete! Use 'agentscript compile' to generate code.
```

## Output

The wizard generates a complete configuration file in your chosen format. For example, a YAML configuration:

```yaml
version: '1.0.0'
project_name: agentscript_project
environment: development

plugin:
  target: django
  app_name: data_pipeline
  enable_admin: true
  enable_async: false
  
  database:
    engine: postgresql
    name: myapp_db
    host: localhost
    port: 5432
    user: admin
    password: ''
    connection_pool_size: 10
    echo_sql: false
  
  authentication:
    enabled: true
    secret_key: ''
    token_expiry_hours: 48
    password_min_length: 12
    require_email_verification: false
    allow_registration: true
    session_timeout_minutes: 60
    jwt_algorithm: HS256
  
  api:
    enabled: true
    host: 0.0.0.0
    port: 8000
    cors_enabled: true
    cors_origins:
      - '*'
    rate_limit_enabled: false
    rate_limit_per_minute: 60
    enable_docs: true
    api_prefix: /api
  
  custom_options:
    admin: true
    rest_framework: true

compiler:
  optimization_level: 1
  generate_type_hints: true
  strict_mode: false
  output_format: python
  include_comments: true
  code_style: pep8

logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: null
  max_file_size_mb: 10
  backup_count: 5
```

## Using the Generated Configuration

After saving the configuration, use it with the compile command:

```bash
# Auto-discovers agentscript.yaml in current directory
agentscript compile pipeline.ags

# Or specify the config file explicitly
agentscript compile pipeline.ags --config agentscript.yaml
```

## Features

### Visual Interface

- **Rich Tables**: Clear display of available plugins and features
- **Tree Views**: Hierarchical display of configuration review
- **Colored Output**: Color-coded prompts and status messages
- **Panels**: Organized sections with borders and titles
- **Progress Indicators**: Visual feedback during operations

### Smart Defaults

- Framework-appropriate default values
- Database port defaults (5432 for PostgreSQL, 3306 for MySQL)
- Reasonable security settings (min password length, token expiry)
- Production-ready configurations

### Validation

- Application name sanitization (lowercase, underscores)
- Port number validation
- Choice validation for all options
- Required field enforcement

### Flexibility

- Skip optional features
- Cancel at any time
- Review before committing
- Choose configuration format
- Custom filenames

## Python API

You can also use the wizard programmatically:

```python
from agentscript.interactive import run_interactive_wizard
from pathlib import Path

# Run wizard
config = run_interactive_wizard()

# Or with source file
config = run_interactive_wizard(Path("pipeline.ags"))

# config is a dictionary with all settings
print(config['target'])  # e.g., 'django'
print(config['app_name'])  # e.g., 'data_pipeline'
```

## Tips and Best Practices

### 1. Use for New Projects

The wizard is perfect for starting new projects:

```bash
# Create project directory
mkdir my_pipeline
cd my_pipeline

# Run wizard
agentscript init

# Add your AgentScript files
# Then generate code
agentscript compile pipeline.ags
```

### 2. Different Environments

Create different configurations for different environments:

```bash
# Development
agentscript init
# Save as agentscript.dev.yaml

# Production
agentscript init
# Save as agentscript.prod.yaml
```

### 3. Team Standardization

Use the wizard to ensure team members use consistent settings:

1. Lead developer runs wizard
2. Commits generated config to repository
3. Team members use the config file

### 4. Experimentation

Try different plugins quickly:

```bash
# Try Django
agentscript init  # Select Django, save as django-config.yaml

# Try FastAPI
agentscript init  # Select FastAPI, save as fastapi-config.yaml

# Compare generated code
agentscript compile pipeline.ags --config django-config.yaml
agentscript compile pipeline.ags --config fastapi-config.yaml
```

## Troubleshooting

### Wizard Won't Start

```bash
# Install Rich library
pip install rich

# Verify installation
python -c "import rich; print(rich.__version__)"
```

### Configuration Not Saved

- Check directory permissions
- Ensure filename is valid
- Try a different format (YAML, JSON, TOML)

### Can't Find Saved Configuration

- Check current directory
- Configuration files are saved in the working directory
- Use absolute paths if needed

## Keyboard Shortcuts

- **Enter**: Accept default value
- **Ctrl+C**: Cancel wizard (at any prompt)
- **↑/↓**: Navigate history (for repeated prompts)

## Advanced Usage

### Automated Configuration

For CI/CD or scripts, use configuration files instead of the wizard:

```bash
# Generate base config with wizard once
agentscript init

# Edit config file programmatically
# Then use in automation
agentscript compile pipeline.ags --config agentscript.yaml
```

### Custom Wizard Extensions

Create custom wizards for specific workflows:

```python
from agentscript.interactive import InteractiveConfigWizard

class CustomWizard(InteractiveConfigWizard):
    def _configure_custom_options(self, plugin_name):
        # Add custom configuration steps
        pass

wizard = CustomWizard()
config = wizard.run()
```

## See Also

- [Configuration System](configuration.md)
- [Plugin System](plugins.md)
- [CLI Reference](cli.md)
- [Getting Started Guide](getting-started.md)
