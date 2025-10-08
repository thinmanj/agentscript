# Pipeline widget for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ProgressBar, Button, Label
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Dict, Any, Optional

class PipelineWidget(Widget):
    """Widget for displaying pipeline execution status."""
    
    def __init__(self, pipeline_name: str, **kwargs):
        super().__init__(**kwargs)
        self.pipeline_name = pipeline_name
        self.status = reactive('idle')
        self.progress = reactive(0.0)
        self.records_processed = reactive(0)
        self.error_message = reactive('')

    def compose(self):
        """Compose the pipeline widget."""
        with Container(classes='pipeline-widget'):
            yield Label(self.pipeline_name, classes='pipeline-title')
            yield Static(self.status, id='pipeline-status')
            yield ProgressBar(total=100, show_eta=True, id='pipeline-progress')
            yield Static(f'Records: {self.records_processed}', id='record-count')
            with Horizontal():
                yield Button('Start', id='start-btn', variant='primary')
                yield Button('Stop', id='stop-btn', variant='warning')
                yield Button('Reset', id='reset-btn')

    def watch_status(self, status: str) -> None:
        """React to status changes."""
        status_widget = self.query_one('#pipeline-status')
        status_widget.update(status.capitalize())
        
        # Update button states based on status
        start_btn = self.query_one('#start-btn')
        stop_btn = self.query_one('#stop-btn')
        
        if status == 'running':
            start_btn.disabled = True
            stop_btn.disabled = False
        else:
            start_btn.disabled = False
            stop_btn.disabled = True

    def watch_progress(self, progress: float) -> None:
        """React to progress changes."""
        progress_bar = self.query_one('#pipeline-progress')
        progress_bar.progress = progress

    def watch_records_processed(self, count: int) -> None:
        """React to record count changes."""
        record_widget = self.query_one('#record-count')
        record_widget.update(f'Records: {count}')

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == 'start-btn':
            await self._start_pipeline()
        elif event.button.id == 'stop-btn':
            await self._stop_pipeline()
        elif event.button.id == 'reset-btn':
            await self._reset_pipeline()

    async def _start_pipeline(self) -> None:
        """Start pipeline execution."""
        self.status = 'running'
        self.progress = 0.0
        # Implementation would connect to actual executor

    async def _stop_pipeline(self) -> None:
        """Stop pipeline execution."""
        self.status = 'stopped'

    async def _reset_pipeline(self) -> None:
        """Reset pipeline state."""
        self.status = 'idle'
        self.progress = 0.0
        self.records_processed = 0
        self.error_message = ''