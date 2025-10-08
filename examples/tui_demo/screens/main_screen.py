# Main screen for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import Screen
from textual.widgets import (
    Header, Footer, Button, Static, Label, ProgressBar, DataTable, Log
)
from textual.reactive import reactive
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
import asyncio

from ..widgets.pipeline_widget import PipelineWidget
from ..widgets.log_viewer import LogViewer

class MainScreen(Screen):
    """Main dashboard screen."""
    
    BINDINGS = [
        ('r', 'refresh', 'Refresh'),
        ('p', 'run_pipeline', 'Run Pipeline'),
        ('c', 'clear_logs', 'Clear Logs'),
    ]

    def __init__(self, executor):
        super().__init__()
        self.executor = executor
        self.pipeline_count = reactive(0)
        self.active_executions = reactive(0)

    def compose(self) -> ComposeResult:
        """Create the main screen layout."""
        with Container(id='main-container'):
            with Horizontal(id='top-section'):
                with Vertical(id='status-panel', classes='panel'):
                    yield Label('Pipeline Status', id='status-title')
                    yield Static('Available Pipelines: 2', id='pipeline-count')
                    yield Static('Active Executions: 0', id='active-count')
                    yield ProgressBar(total=100, show_eta=False, id='overall-progress')

                with Vertical(id='quick-actions', classes='panel'):
                    yield Label('Quick Actions', id='actions-title')
                    yield Button("CustomerAnalysis", id="run-customer_analysis", classes="pipeline-button")
                    yield Button("SalesReport", id="run-sales_report", classes="pipeline-button")

            with Horizontal(id='bottom-section'):
                with Container(id='recent-activity', classes='panel'):
                    yield Label('Recent Activity', id='activity-title')
                    yield LogViewer(id='activity-log')

                with Container(id='system-info', classes='panel'):
                    yield Label('System Information', id='system-title')
                    yield Static(self._get_system_info(), id='system-details')

    def _get_system_info(self) -> str:
        """Get system information display."""
        import platform
        import psutil
        
        return f"""OS: {platform.system()} {platform.release()}
CPU: {psutil.cpu_count()} cores
Memory: {psutil.virtual_memory().total // (1024**3)} GB
Python: {platform.python_version()}"""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == 'run-customer_analysis':
            await self._execute_pipeline('CustomerAnalysis')

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == 'run-sales_report':
            await self._execute_pipeline('SalesReport')

    async def _execute_pipeline(self, intent_name: str) -> None:
        """Execute a pipeline and update the UI."""
        try:
            self.active_executions += 1
            self._update_active_count()
            
            # Log the start
            log_widget = self.query_one('#activity-log')
            log_widget.write(f'Starting pipeline: {intent_name}')
            
            # Execute the pipeline
            result = await self.executor.execute_pipeline(intent_name)
            
            # Log completion
            log_widget.write(f'Pipeline {intent_name} completed: {result.get("records_processed", 0)} records')
            
        except Exception as e:
            # Log error
            log_widget = self.query_one('#activity-log')
            log_widget.write(f'Pipeline {intent_name} failed: {e}')
            
        finally:
            self.active_executions -= 1
            self._update_active_count()

    def _update_active_count(self) -> None:
        """Update the active executions counter."""
        counter = self.query_one('#active-count')
        counter.update(f'Active Executions: {self.active_executions}')

    def action_refresh(self) -> None:
        """Refresh the screen data."""
        self.refresh()

    def action_run_pipeline(self) -> None:
        """Show pipeline selection dialog."""
        self.app.switch_screen('pipeline')

    def action_clear_logs(self) -> None:
        """Clear the activity log."""
        log_widget = self.query_one('#activity-log')
        log_widget.clear()