# AgentScript Configuration System

The AgentScript configuration system provides centralized management of compiler settings, plugin options, database configurations, authentication, APIs, and more.

## Configuration File Formats

AgentScript supports multiple configuration file formats:

- **YAML**: `agentscript.yaml` or `agentscript.yml` (recommended)
- **JSON**: `agentscript.json`
- **TOML**: `agentscript.toml`

## Auto-Discovery

AgentScript automatically discovers configuration files in the current directory. It searches for files in this order:

1. `agentscript.yaml`
2. `agentscript.yml`
3. `agentscript.json`
4. `agentscript.toml`
5. `.agentscript`

## Configuration Structure

### Top-Level Settings

```yaml
version: "1.0.0"
project_name: "my_project"
environment: "development"  # development, production, testing
```

### Plugin Configuration

```yaml
plugin:
  target: "django"  # pandas, django, fastapi, flask, tui
  app_name: "myapp"
  enable_admin: true
  enable_async: false
```

#### Database Configuration

```yaml
plugin:
  database:
    engine: "postgresql"  # sqlite, postgresql, mysql
    name: "mydb"
    host: "localhost"
    port: 5432
    user: "dbuser"
    password: ""  # Use environment variable
    connection_pool_size: 10
    echo_sql: false
```

**Connection Strings Generated:**

- SQLite: `sqlite:///mydb.db`
- PostgreSQL: `postgresql://user:password@localhost:5432/mydb`
- MySQL: `mysql://user:password@localhost:3306/mydb`

#### Authentication Configuration

```yaml
plugin:
  authentication:
    enabled: true
    secret_key: ""  # Required - use SECRET_KEY env var
    token_expiry_hours: 24
    password_min_length: 8
    require_email_verification: false
    allow_registration: true
    session_timeout_minutes: 60
    jwt_algorithm: "HS256"
```

#### API Configuration

```yaml
plugin:
  api:
    enabled: true
    host: "0.0.0.0"
    port: 8000
    cors_enabled: true
    cors_origins:
      - "http://localhost:3000"
      - "https://myapp.com"
    rate_limit_enabled: true
    rate_limit_per_minute: 60
    enable_docs: true
    api_prefix: "/api"
```

#### Custom Plugin Options

```yaml
plugin:
  custom_options:
    celery_enabled: true
    redis_url: "redis://localhost:6379"
    s3_bucket: "my-bucket"
    custom_middleware: true
```

### Compiler Configuration

```yaml
compiler:
  optimization_level: 1  # 0-3
  generate_type_hints: true
  strict_mode: false
  output_format: "python"
  include_comments: true
  code_style: "pep8"  # pep8, black, google
```

### Logging Configuration

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/agentscript.log"  # null for no file logging
  max_file_size_mb: 10
  backup_count: 5
```

## Environment Variable Overrides

Environment variables override config file settings:

### Database

- `DATABASE_ENGINE` → database.engine
- `DATABASE_NAME` → database.name
- `DATABASE_HOST` → database.host
- `DATABASE_PORT` → database.port
- `DATABASE_USER` → database.user
- `DATABASE_PASSWORD` → database.password

### Authentication

- `SECRET_KEY` → authentication.secret_key
- `TOKEN_EXPIRY_HOURS` → authentication.token_expiry_hours

### API

- `API_HOST` → api.host
- `API_PORT` → api.port
- `CORS_ORIGINS` → api.cors_origins (comma-separated)

### Logging

- `LOG_LEVEL` → logging.level
- `LOG_FILE` → logging.file

## Usage Examples

### Python API

```python
from agentscript.config import load_config, ConfigManager

# Auto-discover configuration
config = load_config()

# Load specific config file
from pathlib import Path
config = load_config(Path("my_config.yaml"))

# Access configuration
print(config.plugin.target)
print(config.plugin.database.get_connection_string())
print(config.plugin.authentication.enabled)

# Generate default configuration
manager = ConfigManager()
manager.generate_default_config(Path("agentscript.yaml"))
```

### CLI Usage

```bash
# Generate default configuration file
agentscript config init

# Generate with specific format
agentscript config init --format json
agentscript config init --format toml

# Validate configuration
agentscript config validate

# Show current configuration
agentscript config show

# Compile with config file
agentscript compile pipeline.ags --config agentscript.yaml
```

## Configuration Presets

### Development (Default)

```yaml
environment: "development"
plugin:
  database:
    engine: "sqlite"
    echo_sql: true
  authentication:
    enabled: false
compiler:
  optimization_level: 0
  include_comments: true
logging:
  level: "DEBUG"
```

### Production

```yaml
environment: "production"
plugin:
  database:
    engine: "postgresql"
    echo_sql: false
    connection_pool_size: 20
  authentication:
    enabled: true
    require_email_verification: true
  api:
    rate_limit_enabled: true
    enable_docs: false
compiler:
  optimization_level: 3
  strict_mode: true
  include_comments: false
logging:
  level: "WARNING"
  file: "/var/log/agentscript/app.log"
```

### Testing

```yaml
environment: "testing"
plugin:
  database:
    engine: "sqlite"
    name: ":memory:"
  authentication:
    enabled: false
compiler:
  optimization_level: 0
logging:
  level: "ERROR"
```

## Framework-Specific Examples

### Django Configuration

```yaml
plugin:
  target: "django"
  app_name: "data_api"
  enable_admin: true
  database:
    engine: "postgresql"
    name: "django_db"
  authentication:
    enabled: true
  custom_options:
    use_rest_framework: true
    celery_enabled: true
    cors_allowed_origins:
      - "http://localhost:3000"
```

### FastAPI Configuration

```yaml
plugin:
  target: "fastapi"
  app_name: "api_service"
  enable_async: true
  database:
    engine: "postgresql"
  api:
    enable_docs: true
    api_prefix: "/api/v1"
  custom_options:
    use_sql_model: true
    background_tasks: true
```

### Flask Configuration

```yaml
plugin:
  target: "flask"
  app_name: "web_app"
  enable_admin: true
  database:
    engine: "mysql"
  authentication:
    enabled: true
  custom_options:
    use_blueprints: true
    session_type: "redis"
```

### TUI Configuration

```yaml
plugin:
  target: "tui"
  app_name: "data_dashboard"
  enable_async: true
  custom_options:
    theme: "dark"
    refresh_rate: 1000
    enable_mouse: true
```

## Best Practices

1. **Never commit secrets**: Use environment variables for sensitive data
2. **Use different configs per environment**: `agentscript.dev.yaml`, `agentscript.prod.yaml`
3. **Version control your configs**: Commit config files (without secrets) to git
4. **Document custom options**: Add comments explaining custom plugin options
5. **Validate before deployment**: Run `agentscript config validate` in CI/CD
6. **Use presets**: Start with environment presets and customize as needed

## Troubleshooting

### Configuration not found

```bash
# Check current directory for config files
ls -la agentscript.*

# Use explicit config path
agentscript compile pipeline.ags --config /path/to/config.yaml
```

### Invalid configuration

```bash
# Validate configuration
agentscript config validate

# Show configuration with resolved values
agentscript config show --resolved
```

### Environment variables not applied

```bash
# Print effective configuration
export DATABASE_PASSWORD=secret
agentscript config show --env

# Check environment variables
env | grep -E "(DATABASE_|API_|SECRET_)"
```

## Migration from Previous Versions

If upgrading from an older version:

```bash
# Generate new config with current settings
agentscript config migrate old_config.json --output agentscript.yaml

# Review and test new configuration
agentscript config validate agentscript.yaml
```

## See Also

- [Plugin System Documentation](plugins.md)
- [CLI Reference](cli.md)
- [Environment Variables](environment.md)
- [Example Configurations](../examples/)
