"""
TUI Plugin for AgentScript

This plugin generates Terminal User Interface applications from AgentScript pipeline definitions.
It creates interactive terminal applications using Rich and Textual for real-time data processing,
visualization, and pipeline monitoring.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .base import BasePlugin, GenerationContext, PluginConfig
from ..ast_nodes import Program, IntentDeclaration, PipelineStage, FunctionCall, AttributeAccess, Literal


class TUIPlugin(BasePlugin):
    """Terminal User Interface application generator."""
    
    plugin_name = "tui"
    plugin_description = "Generate interactive Terminal User Interface applications"
    plugin_version = "1.0.0"
    plugin_dependencies = ["rich>=13.0", "textual>=0.45.0", "pandas>=1.3.0"]
    plugin_optional_dependencies = ["matplotlib>=3.5", "plotly>=5.0", "asyncio-mqtt"]
    plugin_output_extension = ".py"
    plugin_supports_async = True
    plugin_supports_web = False
    plugin_supports_database = False
    plugin_supports_auth = False
    
    @property
    def name(self) -> str:
        return "tui"
    
    @property
    def description(self) -> str:
        return "Generate interactive Terminal User Interface applications with Rich/Textual"
    
    def generate_code(self, ast: Program, context: GenerationContext) -> Dict[str, str]:
        """Generate TUI application code from AgentScript AST."""
        files = {}
        
        # Extract intents from AST
        intents = [stmt for stmt in ast.statements if isinstance(stmt, IntentDeclaration)]
        
        if not intents:
            return files
        
        # Generate main TUI application
        files["main.py"] = self._generate_main_app(intents, context)
        
        # Generate widgets and screens
        files["widgets/__init__.py"] = ""
        files["widgets/pipeline_widget.py"] = self._generate_pipeline_widget(intents, context)
        files["widgets/data_viewer.py"] = self._generate_data_viewer_widget(context)
        files["widgets/log_viewer.py"] = self._generate_log_viewer_widget(context)
        
        # Generate screens
        files["screens/__init__.py"] = ""
        files["screens/main_screen.py"] = self._generate_main_screen(intents, context)
        files["screens/pipeline_screen.py"] = self._generate_pipeline_screen(intents, context)
        files["screens/data_screen.py"] = self._generate_data_screen(context)
        
        # Generate data models
        files["models.py"] = self._generate_models_file(intents, context)
        
        # Generate pipeline executor
        files["executor.py"] = self._generate_pipeline_executor(intents, context)
        
        # Generate configuration
        files["config.py"] = self._generate_config_file(context)
        
        # Generate utilities
        files["utils.py"] = self._generate_utils_file(context)
        
        # Generate requirements
        files["requirements.txt"] = self._generate_requirements(context)
        
        # Generate startup script
        files["run.py"] = self._generate_run_script(context)
        
        return files
    
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """Get required dependencies for TUI project."""
        deps = self.plugin_dependencies.copy()
        
        # Add visualization dependencies
        if context.options.get('visualization', True):
            deps.extend(['matplotlib>=3.5', 'plotly>=5.0'])
        
        # Add real-time data support
        if context.options.get('realtime', False):
            deps.extend(['asyncio-mqtt>=0.11', 'websockets>=11.0'])
        
        return deps
    
    def _generate_main_app(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate main TUI application."""
        lines = [
            f"# AgentScript TUI Application",
            f"# Generated from AgentScript source: {context.source_file.name}",
            f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "from textual.app import App, ComposeResult",
            "from textual.containers import Container, Horizontal, Vertical",
            "from textual.widgets import Header, Footer, Button, Static, TabbedContent, TabPane",
            "from textual.binding import Binding",
            "import asyncio",
            "import logging",
            "",
            "from .screens.main_screen import MainScreen",
            "from .screens.pipeline_screen import PipelineScreen",
            "from .screens.data_screen import DataScreen",
            "from .config import settings",
            "from .executor import PipelineExecutor",
            "",
            f"class AgentScriptTUI(App):",
            f'    """AgentScript Terminal User Interface Application."""',
            f'    ',
            f'    TITLE = "{context.options.get("app_name", "AgentScript TUI")}"',
            f'    SUB_TITLE = "Interactive Data Pipeline Processing"',
            "",
            "    CSS_PATH = 'styles.css'",
            "    ",
            "    BINDINGS = [",
            "        Binding('q', 'quit', 'Quit'),",
            "        Binding('d', 'toggle_dark', 'Toggle Dark Mode'),",
            "        Binding('s', 'screenshot', 'Screenshot'),",
            "        Binding('1', 'switch_screen(\"main\")', 'Main'),",
            "        Binding('2', 'switch_screen(\"pipeline\")', 'Pipelines'),",
            "        Binding('3', 'switch_screen(\"data\")', 'Data'),",
            "    ]",
            "",
            "    def __init__(self):",
            "        super().__init__()",
            "        self.executor = PipelineExecutor()",
            "        self.dark = True",
            "",
            "    def on_mount(self) -> None:",
            '        """Called when app starts."""',
            "        self.title = self.TITLE",
            "        self.sub_title = self.SUB_TITLE",
            "        self.install_screen(MainScreen(self.executor), name='main')",
            "        self.install_screen(PipelineScreen(self.executor), name='pipeline')",
            "        self.install_screen(DataScreen(self.executor), name='data')",
            "        self.switch_screen('main')",
            "",
            "    def action_toggle_dark(self) -> None:",
            '        """Toggle dark mode."""',
            "        self.dark = not self.dark",
            "",
            "    def action_switch_screen(self, screen: str) -> None:",
            '        """Switch to a specific screen."""',
            "        self.switch_screen(screen)",
            "",
            "    def action_screenshot(self) -> None:",
            '        """Take a screenshot."""',
            "        path = self.save_screenshot()",
            "        self.notify(f'Screenshot saved to {path}')",
            "",
        ]
        
        # Add intent-specific methods
        for intent in intents:
            method_name = self._to_snake_case(intent.name)
            lines.extend([
                f"    async def execute_{method_name}(self, **kwargs):",
                f'        """Execute {intent.name} pipeline."""',
                f"        return await self.executor.execute_pipeline('{intent.name}', **kwargs)",
                "",
            ])
        
        lines.extend([
            "def main():",
            '    """Main entry point."""',
            "    # Setup logging",
            "    logging.basicConfig(",
            "        level=logging.INFO,",
            "        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',",
            "        handlers=[",
            "            logging.FileHandler('tui_app.log'),",
            "            logging.StreamHandler()",
            "        ]",
            "    )",
            "    ",
            "    # Run the TUI application",
            "    app = AgentScriptTUI()",
            "    app.run()",
            "",
            "if __name__ == '__main__':",
            "    main()",
        ])
        
        return "\n".join(lines)
    
    def _generate_main_screen(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate main screen with overview and quick actions."""
        lines = [
            f"# Main screen for AgentScript TUI",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from textual.app import ComposeResult",
            "from textual.containers import Container, Horizontal, Vertical, Grid",
            "from textual.screen import Screen",
            "from textual.widgets import (",
            "    Header, Footer, Button, Static, Label, ProgressBar, DataTable, Log",
            ")",
            "from textual.reactive import reactive",
            "from rich.text import Text",
            "from rich.table import Table",
            "from rich.panel import Panel",
            "import asyncio",
            "",
            "from ..widgets.pipeline_widget import PipelineWidget",
            "from ..widgets.log_viewer import LogViewer",
            "",
            "class MainScreen(Screen):",
            '    """Main dashboard screen."""',
            "    ",
            "    BINDINGS = [",
            "        ('r', 'refresh', 'Refresh'),",
            "        ('p', 'run_pipeline', 'Run Pipeline'),",
            "        ('c', 'clear_logs', 'Clear Logs'),",
            "    ]",
            "",
            "    def __init__(self, executor):",
            "        super().__init__()",
            "        self.executor = executor",
            "        self.pipeline_count = reactive(0)",
            "        self.active_executions = reactive(0)",
            "",
            "    def compose(self) -> ComposeResult:",
            '        """Create the main screen layout."""',
            "        with Container(id='main-container'):",
            "            with Horizontal(id='top-section'):",
            "                with Vertical(id='status-panel', classes='panel'):",
            "                    yield Label('Pipeline Status', id='status-title')",
        ]
        
        # Generate pipeline count line
        pipeline_names = [f'"{intent.name}"' for intent in intents]
        lines.append(f"                    yield Static('Available Pipelines: {len(intents)}', id='pipeline-count')")
        lines.extend([
            "                    yield Static('Active Executions: 0', id='active-count')",
            "                    yield ProgressBar(total=100, show_eta=False, id='overall-progress')",
            "",
            "                with Vertical(id='quick-actions', classes='panel'):",
            "                    yield Label('Quick Actions', id='actions-title')",
        ])
        
        # Add quick action buttons for each intent
        for intent in intents:
            button_id = f"run-{self._to_snake_case(intent.name)}"
            lines.append(f'                    yield Button("{intent.name}", id="{button_id}", classes="pipeline-button")')
        
        lines.extend([
            "",
            "            with Horizontal(id='bottom-section'):",
            "                with Container(id='recent-activity', classes='panel'):",
            "                    yield Label('Recent Activity', id='activity-title')",
            "                    yield LogViewer(id='activity-log')",
            "",
            "                with Container(id='system-info', classes='panel'):",
            "                    yield Label('System Information', id='system-title')",
            "                    yield Static(self._get_system_info(), id='system-details')",
            "",
            "    def _get_system_info(self) -> str:",
            '        """Get system information display."""',
            "        import platform",
            "        import psutil",
            "        ",
            "        return f\"\"\"OS: {platform.system()} {platform.release()}",
            "CPU: {psutil.cpu_count()} cores",
            "Memory: {psutil.virtual_memory().total // (1024**3)} GB",
            "Python: {platform.python_version()}\"\"\"",
            "",
        ])
        
        # Add action handlers for each pipeline button
        for intent in intents:
            method_name = f"run_{self._to_snake_case(intent.name)}"
            button_id = f"run-{self._to_snake_case(intent.name)}"
            
            lines.extend([
                f"    async def on_button_pressed(self, event: Button.Pressed) -> None:",
                f'        """Handle button press events."""',
                f"        if event.button.id == '{button_id}':",
                f"            await self._execute_pipeline('{intent.name}')",
                "",
            ])
        
        lines.extend([
            "    async def _execute_pipeline(self, intent_name: str) -> None:",
            '        """Execute a pipeline and update the UI."""',
            "        try:",
            "            self.active_executions += 1",
            "            self._update_active_count()",
            "            ",
            "            # Log the start",
            "            log_widget = self.query_one('#activity-log')",
            "            log_widget.write(f'Starting pipeline: {intent_name}')",
            "            ",
            "            # Execute the pipeline",
            "            result = await self.executor.execute_pipeline(intent_name)",
            "            ",
            "            # Log completion",
            "            log_widget.write(f'Pipeline {intent_name} completed: {result.get(\"records_processed\", 0)} records')",
            "            ",
            "        except Exception as e:",
            "            # Log error",
            "            log_widget = self.query_one('#activity-log')",
            "            log_widget.write(f'Pipeline {intent_name} failed: {e}')",
            "            ",
            "        finally:",
            "            self.active_executions -= 1",
            "            self._update_active_count()",
            "",
            "    def _update_active_count(self) -> None:",
            '        """Update the active executions counter."""',
            "        counter = self.query_one('#active-count')",
            "        counter.update(f'Active Executions: {self.active_executions}')",
            "",
            "    def action_refresh(self) -> None:",
            '        """Refresh the screen data."""',
            "        self.refresh()",
            "",
            "    def action_run_pipeline(self) -> None:",
            '        """Show pipeline selection dialog."""',
            "        self.app.switch_screen('pipeline')",
            "",
            "    def action_clear_logs(self) -> None:",
            '        """Clear the activity log."""',
            "        log_widget = self.query_one('#activity-log')",
            "        log_widget.clear()",
        ])
        
        return "\n".join(lines)
    
    def _generate_pipeline_widget(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate pipeline widget for displaying pipeline status."""
        lines = [
            f"# Pipeline widget for AgentScript TUI",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from textual.widget import Widget",
            "from textual.reactive import reactive",
            "from textual.containers import Container, Vertical, Horizontal",
            "from textual.widgets import Static, ProgressBar, Button, Label",
            "from rich.panel import Panel",
            "from rich.table import Table",
            "from rich.progress import Progress, SpinnerColumn, TextColumn",
            "from typing import Dict, Any, Optional",
            "",
            "class PipelineWidget(Widget):",
            '    """Widget for displaying pipeline execution status."""',
            "    ",
            "    def __init__(self, pipeline_name: str, **kwargs):",
            "        super().__init__(**kwargs)",
            "        self.pipeline_name = pipeline_name",
            "        self.status = reactive('idle')",
            "        self.progress = reactive(0.0)",
            "        self.records_processed = reactive(0)",
            "        self.error_message = reactive('')",
            "",
            "    def compose(self):",
            '        """Compose the pipeline widget."""',
            "        with Container(classes='pipeline-widget'):",
            "            yield Label(self.pipeline_name, classes='pipeline-title')",
            "            yield Static(self.status, id='pipeline-status')",
            "            yield ProgressBar(total=100, show_eta=True, id='pipeline-progress')",
            "            yield Static(f'Records: {self.records_processed}', id='record-count')",
            "            with Horizontal():",
            "                yield Button('Start', id='start-btn', variant='primary')",
            "                yield Button('Stop', id='stop-btn', variant='warning')",
            "                yield Button('Reset', id='reset-btn')",
            "",
            "    def watch_status(self, status: str) -> None:",
            '        """React to status changes."""',
            "        status_widget = self.query_one('#pipeline-status')",
            "        status_widget.update(status.capitalize())",
            "        ",
            "        # Update button states based on status",
            "        start_btn = self.query_one('#start-btn')",
            "        stop_btn = self.query_one('#stop-btn')",
            "        ",
            "        if status == 'running':",
            "            start_btn.disabled = True",
            "            stop_btn.disabled = False",
            "        else:",
            "            start_btn.disabled = False",
            "            stop_btn.disabled = True",
            "",
            "    def watch_progress(self, progress: float) -> None:",
            '        """React to progress changes."""',
            "        progress_bar = self.query_one('#pipeline-progress')",
            "        progress_bar.progress = progress",
            "",
            "    def watch_records_processed(self, count: int) -> None:",
            '        """React to record count changes."""',
            "        record_widget = self.query_one('#record-count')",
            "        record_widget.update(f'Records: {count}')",
            "",
            "    async def on_button_pressed(self, event: Button.Pressed) -> None:",
            '        """Handle button press events."""',
            "        if event.button.id == 'start-btn':",
            "            await self._start_pipeline()",
            "        elif event.button.id == 'stop-btn':",
            "            await self._stop_pipeline()",
            "        elif event.button.id == 'reset-btn':",
            "            await self._reset_pipeline()",
            "",
            "    async def _start_pipeline(self) -> None:",
            '        """Start pipeline execution."""',
            "        self.status = 'running'",
            "        self.progress = 0.0",
            "        # Implementation would connect to actual executor",
            "",
            "    async def _stop_pipeline(self) -> None:",
            '        """Stop pipeline execution."""',
            "        self.status = 'stopped'",
            "",
            "    async def _reset_pipeline(self) -> None:",
            '        """Reset pipeline state."""',
            "        self.status = 'idle'",
            "        self.progress = 0.0",
            "        self.records_processed = 0",
            "        self.error_message = ''",
        ]
        
        return "\n".join(lines)
    
    def _generate_pipeline_executor(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate pipeline executor for running AgentScript pipelines."""
        lines = [
            f"# Pipeline executor for AgentScript TUI",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "import asyncio",
            "import logging",
            "import pandas as pd",
            "import json",
            "from pathlib import Path",
            "from typing import Dict, Any, List, Optional, Callable",
            "from datetime import datetime",
            "",
            "from .models import ExecutionResult, PipelineStatus",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "class PipelineExecutor:",
            '    """Executes AgentScript pipelines with real-time updates."""',
            "    ",
            "    def __init__(self):",
            "        self.active_executions: Dict[str, asyncio.Task] = {}",
            "        self.execution_history: List[ExecutionResult] = []",
            "        self.progress_callbacks: Dict[str, List[Callable]] = {}",
            "",
        ]
        
        # Add pipeline execution methods for each intent
        for intent in intents:
            method_name = self._to_snake_case(intent.name)
            lines.extend([
                f"    async def execute_{method_name}(",
                "        self,",
                "        input_file: Optional[str] = None,",
                "        output_file: Optional[str] = None,",
                "        progress_callback: Optional[Callable] = None",
                "    ) -> ExecutionResult:",
                f'        """Execute {intent.name} pipeline."""',
                f"        return await self._execute_pipeline_impl(",
                f"            '{intent.name}',",
                "            input_file,",
                "            output_file,",
                "            progress_callback",
                "        )",
                "",
            ])
        
        lines.extend([
            "    async def execute_pipeline(",
            "        self,",
            "        intent_name: str,",
            "        input_file: Optional[str] = None,",
            "        output_file: Optional[str] = None,",
            "        progress_callback: Optional[Callable] = None",
            "    ) -> ExecutionResult:",
            '        """Execute a pipeline by intent name."""',
            "        ",
            "        # Route to specific pipeline method",
        ])
        
        # Add routing logic
        for i, intent in enumerate(intents):
            method_name = self._to_snake_case(intent.name)
            condition = "if" if i == 0 else "elif"
            lines.extend([
                f"        {condition} intent_name == '{intent.name}':",
                f"            return await self.execute_{method_name}(input_file, output_file, progress_callback)",
            ])
        
        lines.extend([
            "        else:",
            "            raise ValueError(f'Unknown intent: {intent_name}')",
            "",
            "    async def _execute_pipeline_impl(",
            "        self,",
            "        intent_name: str,",
            "        input_file: Optional[str],",
            "        output_file: Optional[str],",
            "        progress_callback: Optional[Callable]",
            "    ) -> ExecutionResult:",
            '        """Core pipeline execution implementation."""',
            "        ",
            "        execution_id = f'{intent_name}_{datetime.now().isoformat()}'",
            "        ",
            "        try:",
            "            logger.info(f'Starting pipeline execution: {execution_id}')",
            "            ",
            "            # Update progress",
            "            if progress_callback:",
            "                await progress_callback(0, 'Starting pipeline...')",
            "            ",
            "            # Simulate pipeline execution (replace with actual AgentScript execution)",
            "            records_processed = 0",
            "            total_records = 1000  # Would be determined from actual data",
            "            ",
            "            for i in range(total_records):",
            "                # Simulate processing",
            "                await asyncio.sleep(0.001)  # Simulate work",
            "                records_processed += 1",
            "                ",
            "                # Update progress every 100 records",
            "                if records_processed % 100 == 0 and progress_callback:",
            "                    progress = (records_processed / total_records) * 100",
            "                    await progress_callback(progress, f'Processed {records_processed} records')",
            "            ",
            "            # Final progress update",
            "            if progress_callback:",
            "                await progress_callback(100, 'Pipeline completed')",
            "            ",
            "            result = ExecutionResult(",
            "                execution_id=execution_id,",
            "                intent_name=intent_name,",
            "                status=PipelineStatus.COMPLETED,",
            "                records_processed=records_processed,",
            "                input_file=input_file,",
            "                output_file=output_file,",
            "                start_time=datetime.now(),",
            "                end_time=datetime.now(),",
            "                error_message=None",
            "            )",
            "            ",
            "            self.execution_history.append(result)",
            "            logger.info(f'Pipeline execution completed: {execution_id}')",
            "            ",
            "            return result",
            "            ",
            "        except Exception as e:",
            "            logger.error(f'Pipeline execution failed: {execution_id} - {e}')",
            "            ",
            "            error_result = ExecutionResult(",
            "                execution_id=execution_id,",
            "                intent_name=intent_name,",
            "                status=PipelineStatus.FAILED,",
            "                records_processed=records_processed,",
            "                input_file=input_file,",
            "                output_file=output_file,",
            "                start_time=datetime.now(),",
            "                end_time=datetime.now(),",
            "                error_message=str(e)",
            "            )",
            "            ",
            "            self.execution_history.append(error_result)",
            "            raise",
            "",
            "    def get_execution_history(self) -> List[ExecutionResult]:",
            '        """Get execution history."""',
            "        return self.execution_history.copy()",
            "",
            "    def get_active_executions(self) -> List[str]:",
            '        """Get list of active execution IDs."""',
            "        return list(self.active_executions.keys())",
            "",
            "    async def stop_execution(self, execution_id: str) -> bool:",
            '        """Stop an active execution."""',
            "        if execution_id in self.active_executions:",
            "            task = self.active_executions[execution_id]",
            "            task.cancel()",
            "            del self.active_executions[execution_id]",
            "            return True",
            "        return False",
        ])
        
        return "\n".join(lines)
    
    def _generate_models_file(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate data models for TUI application."""
        lines = [
            f"# Data models for AgentScript TUI",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from dataclasses import dataclass",
            "from typing import Optional, List, Dict, Any",
            "from datetime import datetime",
            "from enum import Enum",
            "",
            "class PipelineStatus(str, Enum):",
            '    """Pipeline execution status."""',
            "    IDLE = 'idle'",
            "    RUNNING = 'running'",
            "    COMPLETED = 'completed'",
            "    FAILED = 'failed'",
            "    STOPPED = 'stopped'",
            "",
            "@dataclass",
            "class ExecutionResult:",
            '    """Result of a pipeline execution."""',
            "    execution_id: str",
            "    intent_name: str",
            "    status: PipelineStatus",
            "    records_processed: int",
            "    input_file: Optional[str] = None",
            "    output_file: Optional[str] = None",
            "    start_time: Optional[datetime] = None",
            "    end_time: Optional[datetime] = None",
            "    error_message: Optional[str] = None",
            "    metadata: Dict[str, Any] = None",
            "",
            "    def __post_init__(self):",
            "        if self.metadata is None:",
            "            self.metadata = {}",
            "",
            "@dataclass", 
            "class PipelineConfig:",
            '    """Configuration for a pipeline."""',
            "    name: str",
            "    description: str",
            "    input_formats: List[str]",
            "    output_formats: List[str]",
            "    parameters: Dict[str, Any] = None",
            "",
            "    def __post_init__(self):",
            "        if self.parameters is None:",
            "            self.parameters = {}",
        ]
        
        # Add pipeline-specific config classes
        for intent in intents:
            class_name = self._to_class_name(intent.name)
            lines.extend([
                "",
                f"@dataclass",
                f"class {class_name}Config(PipelineConfig):",
                f'    """Configuration for {intent.name} pipeline."""',
                f'    name: str = "{intent.name}"',
                f'    description: str = "{intent.description or f"Process data with {intent.name} pipeline"}"',
                "    input_formats: List[str] = None",
                "    output_formats: List[str] = None",
                "",
                "    def __post_init__(self):",
                "        if self.input_formats is None:",
                "            self.input_formats = ['csv', 'json']",
                "        if self.output_formats is None:",
                "            self.output_formats = ['csv', 'json']",
                "        super().__post_init__()",
            ])
        
        return "\n".join(lines)
    
    def _generate_data_viewer_widget(self, context: GenerationContext) -> str:
        """Generate data viewer widget for displaying processed data."""
        return f"""# Data viewer widget for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

from textual.widget import Widget
from textual.widgets import DataTable, Static, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
import pandas as pd
from typing import Optional, Dict, Any
import json

class DataViewer(Widget):
    \"\"\"Widget for viewing and exploring processed data.\"\"\"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data: Optional[pd.DataFrame] = None
        self.current_page = reactive(0)
        self.page_size = 50
        
    def compose(self):
        \"\"\"Compose the data viewer widget.\"\"\"
        with Container(classes='data-viewer'):
            with Horizontal(classes='data-controls'):
                yield Input(placeholder='Search...', id='search-input')
                yield Button('Filter', id='filter-btn')
                yield Button('Export', id='export-btn')
                yield Button('Refresh', id='refresh-btn')
            
            yield DataTable(id='data-table', zebra_stripes=True)
            
            with Horizontal(classes='pagination'):
                yield Button('◀ Previous', id='prev-btn')
                yield Static('Page 1 of 1', id='page-info')
                yield Button('Next ▶', id='next-btn')

    def load_data(self, data: pd.DataFrame):
        \"\"\"Load data into the viewer.\"\"\"
        self.data = data
        self._update_table()

    def _update_table(self):
        \"\"\"Update the data table display.\"\"\"
        if self.data is None:
            return
            
        table = self.query_one('#data-table')
        table.clear(columns=True)
        
        # Add columns
        for col in self.data.columns:
            table.add_column(str(col))
        
        # Add rows for current page
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.data.iloc[start_idx:end_idx]
        
        for _, row in page_data.iterrows():
            table.add_row(*[str(val) for val in row])
        
        # Update pagination info
        total_pages = (len(self.data) - 1) // self.page_size + 1
        page_info = self.query_one('#page-info')
        page_info.update(f'Page {{self.current_page + 1}} of {{total_pages}}')

    async def on_button_pressed(self, event: Button.Pressed):
        \"\"\"Handle button press events.\"\"\"
        if event.button.id == 'prev-btn':
            if self.current_page > 0:
                self.current_page -= 1
                self._update_table()
        elif event.button.id == 'next-btn':
            if self.data is not None:
                total_pages = (len(self.data) - 1) // self.page_size + 1
                if self.current_page < total_pages - 1:
                    self.current_page += 1
                    self._update_table()
        elif event.button.id == 'export-btn':
            await self._export_data()
        elif event.button.id == 'refresh-btn':
            self._update_table()

    async def _export_data(self):
        \"\"\"Export current data to file.\"\"\"
        if self.data is None:
            return
            
        # Simple CSV export
        filename = f'export_{{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}}.csv'
        self.data.to_csv(filename, index=False)
        self.notify(f'Data exported to {{filename}}')
"""
    
    def _generate_log_viewer_widget(self, context: GenerationContext) -> str:
        """Generate log viewer widget for displaying application logs."""
        return f"""# Log viewer widget for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

from textual.widget import Widget
from textual.widgets import Log, Button, Input
from textual.containers import Container, Horizontal
from textual.reactive import reactive
import logging
from typing import List

class LogViewer(Log):
    \"\"\"Enhanced log viewer with filtering and search.\"\"\"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_levels = reactive(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.filter_text = reactive('')
        
    def write(self, content: str, level: str = 'INFO'):
        \"\"\"Write a log entry with level.\"\"\"
        if level in self.log_levels and (
            not self.filter_text or self.filter_text.lower() in content.lower()
        ):
            timestamp = pd.Timestamp.now().strftime('%H:%M:%S')
            super().write(f'[{{timestamp}}] {{level}}: {{content}}')

    def set_level_filter(self, levels: List[str]):
        \"\"\"Set which log levels to display.\"\"\"
        self.log_levels = levels

    def set_text_filter(self, text: str):
        \"\"\"Set text filter for log entries.\"\"\"
        self.filter_text = text
"""
    
    def _generate_pipeline_screen(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate pipeline management screen."""
        return f"""# Pipeline screen for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, Select
from textual.reactive import reactive
import asyncio

from ..widgets.pipeline_widget import PipelineWidget

class PipelineScreen(Screen):
    \"\"\"Screen for managing and monitoring pipelines.\"\"\"
    
    BINDINGS = [
        ('r', 'refresh', 'Refresh'),
        ('a', 'run_all', 'Run All'),
        ('s', 'stop_all', 'Stop All'),
    ]

    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def compose(self) -> ComposeResult:
        \"\"\"Create the pipeline screen layout.\"\"\"
        with Container(id='pipeline-container'):
            with Horizontal(id='pipeline-controls'):
                yield Input(placeholder='Input file path...', id='input-file')
                yield Input(placeholder='Output file path...', id='output-file')
                yield Button('Browse Input', id='browse-input')
                yield Button('Browse Output', id='browse-output')
            
            with Grid(id='pipeline-grid'):
{chr(10).join(f'                yield PipelineWidget("{intent.name}", id="widget-{self._to_snake_case(intent.name)}")' for intent in intents)}

    async def on_button_pressed(self, event: Button.Pressed):
        \"\"\"Handle button press events.\"\"\"
        if event.button.id == 'browse-input':
            # Would open file browser
            pass
        elif event.button.id == 'browse-output':
            # Would open file browser
            pass

    def action_run_all(self):
        \"\"\"Run all pipelines.\"\"\"
        # Implementation would run all pipelines
        pass

    def action_stop_all(self):
        \"\"\"Stop all running pipelines.\"\"\"
        # Implementation would stop all pipelines
        pass
"""
    
    def _generate_data_screen(self, context: GenerationContext) -> str:
        """Generate data viewing screen."""
        return f"""# Data screen for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, TabbedContent, TabPane
from textual.reactive import reactive

from ..widgets.data_viewer import DataViewer

class DataScreen(Screen):
    \"\"\"Screen for viewing and analyzing data.\"\"\"
    
    BINDINGS = [
        ('r', 'refresh', 'Refresh'),
        ('e', 'export', 'Export'),
        ('f', 'filter', 'Filter'),
    ]

    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def compose(self) -> ComposeResult:
        \"\"\"Create the data screen layout.\"\"\"
        with Container(id='data-container'):
            with TabbedContent(id='data-tabs'):
                with TabPane('Input Data', id='input-tab'):
                    yield DataViewer(id='input-viewer')
                
                with TabPane('Output Data', id='output-tab'):
                    yield DataViewer(id='output-viewer')
                
                with TabPane('Statistics', id='stats-tab'):
                    yield Static('Data statistics will appear here', id='stats-display')

    def action_refresh(self):
        \"\"\"Refresh data views.\"\"\"
        # Implementation would refresh data
        pass

    def action_export(self):
        \"\"\"Export current data view.\"\"\"
        # Implementation would export data
        pass

    def action_filter(self):
        \"\"\"Open filter dialog.\"\"\"
        # Implementation would show filter dialog
        pass
"""
    
    def _generate_config_file(self, context: GenerationContext) -> str:
        """Generate configuration file."""
        return f"""# Configuration for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

from pydantic import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    \"\"\"Application settings.\"\"\"
    app_name: str = "{context.options.get('app_name', 'AgentScript TUI')}"
    debug: bool = True
    log_level: str = "INFO"
    
    # UI Settings
    theme: str = "dark"
    auto_refresh: bool = True
    refresh_interval: int = 5  # seconds
    
    # Data Settings
    default_input_dir: str = "./data/input"
    default_output_dir: str = "./data/output"
    max_display_rows: int = 1000
    
    # Pipeline Settings
    max_concurrent_pipelines: int = 3
    pipeline_timeout: int = 300  # seconds
    
    class Config:
        env_file = ".env"

settings = Settings()
"""
    
    def _generate_utils_file(self, context: GenerationContext) -> str:
        """Generate utility functions."""
        return f"""# Utility functions for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

import pandas as pd
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from rich.table import Table
from rich.console import Console

def load_data_file(file_path: Union[str, Path]) -> pd.DataFrame:
    \"\"\"Load data from various file formats.\"\"\"
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix.lower() == '.json':
        return pd.read_json(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {{file_path.suffix}}")

def save_data_file(data: pd.DataFrame, file_path: Union[str, Path]) -> None:
    \"\"\"Save data to various file formats.\"\"\"
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.csv':
        data.to_csv(file_path, index=False)
    elif file_path.suffix.lower() == '.json':
        data.to_json(file_path, orient='records', indent=2)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        data.to_excel(file_path, index=False)
    else:
        raise ValueError(f"Unsupported file format: {{file_path.suffix}}")

def format_file_size(size_bytes: int) -> str:
    \"\"\"Format file size in human readable format.\"\"\"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{{size_bytes:.1f}} {{unit}}"
        size_bytes /= 1024.0
    return f"{{size_bytes:.1f}} TB"

def create_data_summary(data: pd.DataFrame) -> Dict[str, Any]:
    \"\"\"Create a summary of the DataFrame.\"\"\"
    return {{
        'rows': len(data),
        'columns': len(data.columns),
        'memory_usage': data.memory_usage(deep=True).sum(),
        'column_types': data.dtypes.to_dict(),
        'null_counts': data.isnull().sum().to_dict(),
        'numeric_summary': data.describe().to_dict() if len(data.select_dtypes(include='number').columns) > 0 else {{}}
    }}
"""
    
    def _generate_requirements(self, context: GenerationContext) -> str:
        """Generate requirements.txt file."""
        deps = self.get_dependencies(context)
        return "\n".join(deps) + "\n"
    
    def _generate_run_script(self, context: GenerationContext) -> str:
        """Generate run script for the TUI application."""
        return f"""#!/usr/bin/env python3
# Run script for AgentScript TUI
# Generated from AgentScript source: {context.source_file.name}

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    main()
"""
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        return "".join(word.capitalize() for word in name.replace("_", " ").split())
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()