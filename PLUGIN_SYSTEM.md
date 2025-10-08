# AgentScript Plugin System - Complete Implementation

## Overview

The AgentScript Plugin System is a comprehensive framework for generating code from AgentScript pipelines targeting multiple backend frameworks. This system transforms data processing pipelines into full-featured applications with web APIs, terminal interfaces, and more.

## Architecture

### Core Components

1. **Base Plugin Architecture** (`src/agentscript/plugins/base.py`)
   - Abstract `BasePlugin` class defining the plugin interface
   - `PluginConfig` dataclass for plugin configuration
   - `GenerationContext` for compilation context
   - `PluginRegistry` for plugin discovery and management

2. **Plugin Registry** (`src/agentscript/plugins/__init__.py`)
   - Auto-discovery of plugins
   - Plugin lifecycle management
   - Dependency validation

3. **CLI Integration** (`src/agentscript/main.py`)
   - Extended `compile` command with `--target` option
   - New `plugins` command for listing available plugins
   - Framework-specific option support

## Available Plugins

### 1. Django Plugin (`django_plugin.py`)
**Target:** `django`

Generates complete Django web applications with:
- **Models:** Django ORM models for pipeline data tracking
- **Views:** REST API views using Django REST Framework
- **Serializers:** DRF serializers for API responses
- **URLs:** URL routing configuration
- **Admin:** Django admin interface integration
- **Management Commands:** Custom Django commands for pipeline execution

**Generated Files:**
- `CustomerApp/models.py` - Django models
- `CustomerApp/views.py` - API views
- `CustomerApp/serializers.py` - DRF serializers
- `CustomerApp/urls.py` - URL patterns
- `CustomerApp/admin.py` - Admin configuration
- `CustomerApp/management/commands/run_pipeline.py` - Management command
- `requirements.txt` - Dependencies
- `settings_additions.py` - Django settings

**Dependencies:** `django>=4.0`, `djangorestframework>=3.14`

### 2. FastAPI Plugin (`fastapi_plugin.py`)
**Target:** `fastapi`

Generates modern async FastAPI applications with:
- **Async API:** FastAPI with async/await support
- **Pydantic Models:** Type-safe data models
- **Background Tasks:** Async pipeline execution
- **Docker Support:** Complete containerization setup
- **Database Integration:** SQLAlchemy async support
- **Configuration:** Settings management with Pydantic

**Generated Files:**
- `main.py` - FastAPI application
- `models.py` - Pydantic models
- `routers/pipelines.py` - API routes
- `tasks.py` - Background task execution
- `config.py` - Application settings
- `dependencies.py` - FastAPI dependencies
- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-service setup
- `requirements.txt` - Dependencies

**Dependencies:** `fastapi[all]>=0.104.0`, `uvicorn[standard]>=0.24.0`, `pydantic>=2.0`

### 3. TUI Plugin (`tui_plugin.py`)
**Target:** `tui`

Generates interactive terminal user interfaces with:
- **Rich Terminal UI:** Beautiful terminal interfaces using Rich/Textual
- **Interactive Screens:** Multiple screens for different functions
- **Data Visualization:** Terminal-based data viewing and charts
- **Real-time Updates:** Live pipeline monitoring
- **Keyboard Navigation:** Full keyboard control

**Generated Files:**
- `main.py` - Main TUI application
- `screens/main_screen.py` - Main interface screen
- `screens/pipeline_screen.py` - Pipeline execution screen
- `screens/data_screen.py` - Data viewing screen
- `widgets/pipeline_widget.py` - Pipeline selection widget
- `widgets/data_viewer.py` - Data display widget
- `widgets/log_viewer.py` - Log viewer widget
- `executor.py` - Pipeline execution engine
- `models.py` - Data models
- `config.py` - Configuration
- `requirements.txt` - Dependencies

**Dependencies:** `rich>=13.0`, `textual>=0.45.0`, `pandas>=1.3.0`

## Usage Examples

### Command Line Interface

#### List Available Plugins
```bash
cd /Volumes/Projects/agentscript
PYTHONPATH=src python3 -c "
from agentscript.main import list_plugins
list_plugins(verbose=True)
"
```

#### Compile to Django
```bash
cd /Volumes/Projects/agentscript/examples
PYTHONPATH=../src python3 -c "
from pathlib import Path
from agentscript.main import compile_file
compile_file(
    Path('sample_pipeline.ags'),
    Path('my_django_app'),
    'django',
    app_name='MyApp'
)
"
```

#### Compile to FastAPI
```bash
cd /Volumes/Projects/agentscript/examples
PYTHONPATH=../src python3 -c "
from pathlib import Path
from agentscript.main import compile_file
compile_file(
    Path('sample_pipeline.ags'),
    Path('my_fastapi_app'),
    'fastapi',
    app_name='my_api_service'
)
"
```

#### Compile to TUI
```bash
cd /Volumes/Projects/agentscript/examples
PYTHONPATH=../src python3 -c "
from pathlib import Path
from agentscript.main import compile_file
compile_file(
    Path('sample_pipeline.ags'),
    Path('my_tui_app'),
    'tui',
    app_name='DataProcessorTUI'
)
"
```

### Python API Usage

```python
from agentscript.plugins import get_registry
from agentscript.plugins.base import GenerationContext
from agentscript.parser import parse_agentscript
from pathlib import Path

# Load plugin registry
registry = get_registry()

# Parse AgentScript
source = Path('sample_pipeline.ags').read_text()
ast = parse_agentscript(source, 'sample_pipeline.ags')

# Get plugin and generate code
plugin = registry.get_plugin('django')
context = GenerationContext(
    source_file=Path('sample_pipeline.ags'),
    output_dir=Path('output'),
    target_framework='django',
    options={'app_name': 'MyApp'}
)

files = plugin.generate_code(ast, context)
# files is a dict mapping file paths to generated content
```

## Demo Scripts

### Comprehensive Demo (`examples/comprehensive_demo.py`)
A complete demonstration that:
- Lists all available plugins
- Generates applications for all plugins
- Creates actual files on disk
- Shows directory structures
- Displays sample generated code

```bash
cd /Volumes/Projects/agentscript/examples
python3 comprehensive_demo.py --clean
python3 comprehensive_demo.py --plugin django
```

### Plugin Demo (`examples/plugin_demo.py`)
Basic demonstration of plugin capabilities:
- Plugin listing and information
- Code generation examples
- CLI usage examples

## Plugin Development

### Creating a New Plugin

1. **Create Plugin File:** `src/agentscript/plugins/my_plugin.py`

2. **Implement Plugin Class:**
```python
from .base import BasePlugin, PluginConfig

class MyPlugin(BasePlugin):
    plugin_name = "my_framework"
    plugin_description = "Generate applications for MyFramework"
    plugin_dependencies = ["myframework>=1.0"]
    plugin_supports_web = True
    
    @property
    def name(self) -> str:
        return "my_framework"
    
    @property
    def description(self) -> str:
        return "Generate MyFramework applications"
    
    def generate_code(self, ast, context):
        # Generate framework-specific code
        return {
            "main.py": "# Generated MyFramework app\n",
            "requirements.txt": "myframework>=1.0\n"
        }
    
    def get_dependencies(self, context):
        return ["myframework>=1.0"]
```

3. **Auto-Discovery:** The plugin will be automatically discovered on next import

### Plugin Capabilities

Plugins can declare support for various features:
- `supports_async`: Async/await support
- `supports_web`: Web application generation
- `supports_database`: Database integration
- `supports_auth`: Authentication/authorization

## Generated Application Examples

### Sample Django Model
```python
class PipelineExecution(models.Model):
    intent_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
```

### Sample FastAPI Route
```python
@router.post('/customer_analysis', response_model=CustomerAnalysisResponse)
async def execute_customer_analysis(
    request: CustomerAnalysisRequest,
    background_tasks: BackgroundTasks,
):
    execution_id = await create_execution_record('CustomerAnalysis')
    background_tasks.add_task(
        execute_pipeline_task,
        execution_id,
        'CustomerAnalysis',
        request.input_data
    )
    return CustomerAnalysisResponse(
        execution_id=execution_id,
        status=ExecutionStatus.PENDING
    )
```

### Sample TUI Screen
```python
class PipelineScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            PipelineWidget(id="pipeline-list"),
            DataViewer(id="data-view"),
        )
        yield Footer()
    
    def on_pipeline_selected(self, event):
        self.query_one("#data-view").show_pipeline_data(event.pipeline)
```

## Testing and Validation

### Dependency Validation
All plugins validate their dependencies before generating code:
```bash
# Will show dependency errors if Django is not installed
PYTHONPATH=../src python3 -c "
from pathlib import Path
from agentscript.main import compile_file
compile_file(Path('sample.ags'), Path('output'), 'django')
"
# Output: Error: Required dependency not available: django>=4.0
```

### Generated File Structure
Each plugin generates a complete, working application structure:

**Django Structure:**
```
django_demo/
├── CustomerApp/
│   ├── models.py
│   ├── views.py  
│   ├── urls.py
│   ├── admin.py
│   └── management/commands/
├── requirements.txt
└── settings_additions.py
```

**FastAPI Structure:**
```
fastapi_demo/
├── main.py
├── models.py
├── routers/pipelines.py
├── config.py
├── Dockerfile
└── docker-compose.yml
```

**TUI Structure:**
```
tui_demo/
├── main.py
├── screens/
├── widgets/  
├── executor.py
└── requirements.txt
```

## Current Status

✅ **Completed:**
- Base plugin architecture and registry
- Django plugin with full web application generation
- FastAPI plugin with async API generation  
- TUI plugin with Rich/Textual interface generation
- CLI integration with plugin support
- Comprehensive demo system
- Plugin discovery and validation
- Dependency checking
- File generation and writing

🎯 **Next Steps:**
- Flask plugin implementation
- Plugin templates system
- Configuration file support for plugin options
- Plugin testing framework
- Documentation generation from plugins
- Plugin marketplace/registry system

## Performance

The plugin system is designed for efficiency:
- **Lazy Loading:** Plugins are only loaded when needed
- **Caching:** Plugin instances are cached per configuration
- **Validation:** Early dependency validation prevents wasted work
- **Parallel Generation:** Multiple files can be generated concurrently

## Extensibility

The system is built for extensibility:
- **Plugin Interface:** Clear, documented interface for new plugins
- **Auto-Discovery:** New plugins are automatically found
- **Configuration:** Rich configuration system via PluginConfig
- **Templates:** Support for Jinja2 templates (extensible)
- **Hooks:** Pre/post generation hooks (planned)

This plugin system transforms AgentScript from a simple data processing compiler into a comprehensive application generator, supporting modern development workflows and multiple deployment targets.