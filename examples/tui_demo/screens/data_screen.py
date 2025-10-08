# Data screen for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Label, Input, TabbedContent, TabPane
from textual.reactive import reactive

from ..widgets.data_viewer import DataViewer

class DataScreen(Screen):
    """Screen for viewing and analyzing data."""
    
    BINDINGS = [
        ('r', 'refresh', 'Refresh'),
        ('e', 'export', 'Export'),
        ('f', 'filter', 'Filter'),
    ]

    def __init__(self, executor):
        super().__init__()
        self.executor = executor

    def compose(self) -> ComposeResult:
        """Create the data screen layout."""
        with Container(id='data-container'):
            with TabbedContent(id='data-tabs'):
                with TabPane('Input Data', id='input-tab'):
                    yield DataViewer(id='input-viewer')
                
                with TabPane('Output Data', id='output-tab'):
                    yield DataViewer(id='output-viewer')
                
                with TabPane('Statistics', id='stats-tab'):
                    yield Static('Data statistics will appear here', id='stats-display')

    def action_refresh(self):
        """Refresh data views."""
        # Implementation would refresh data
        pass

    def action_export(self):
        """Export current data view."""
        # Implementation would export data
        pass

    def action_filter(self):
        """Open filter dialog."""
        # Implementation would show filter dialog
        pass
