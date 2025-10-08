# Pipeline screen for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, Select
from textual.reactive import reactive
import asyncio

from ..widgets.pipeline_widget import PipelineWidget

class PipelineScreen(Screen):
    """Screen for managing and monitoring pipelines."""
    
    BINDINGS = [
        ('r', 'refresh', 'Refresh'),
        ('a', 'run_all', 'Run All'),
        ('s', 'stop_all', 'Stop All'),
    ]

    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def compose(self) -> ComposeResult:
        """Create the pipeline screen layout."""
        with Container(id='pipeline-container'):
            with Horizontal(id='pipeline-controls'):
                yield Input(placeholder='Input file path...', id='input-file')
                yield Input(placeholder='Output file path...', id='output-file')
                yield Button('Browse Input', id='browse-input')
                yield Button('Browse Output', id='browse-output')
            
            with Grid(id='pipeline-grid'):
                yield PipelineWidget("CustomerAnalysis", id="widget-customer_analysis")
                yield PipelineWidget("SalesReport", id="widget-sales_report")

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button press events."""
        if event.button.id == 'browse-input':
            # Would open file browser
            pass
        elif event.button.id == 'browse-output':
            # Would open file browser
            pass

    def action_run_all(self):
        """Run all pipelines."""
        # Implementation would run all pipelines
        pass

    def action_stop_all(self):
        """Stop all running pipelines."""
        # Implementation would stop all pipelines
        pass
