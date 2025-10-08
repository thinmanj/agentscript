# Log viewer widget for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.widget import Widget
from textual.widgets import Log, Button, Input
from textual.containers import Container, Horizontal
from textual.reactive import reactive
import logging
from typing import List

class LogViewer(Log):
    """Enhanced log viewer with filtering and search."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_levels = reactive(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.filter_text = reactive('')
        
    def write(self, content: str, level: str = 'INFO'):
        """Write a log entry with level."""
        if level in self.log_levels and (
            not self.filter_text or self.filter_text.lower() in content.lower()
        ):
            timestamp = pd.Timestamp.now().strftime('%H:%M:%S')
            super().write(f'[{timestamp}] {level}: {content}')

    def set_level_filter(self, levels: List[str]):
        """Set which log levels to display."""
        self.log_levels = levels

    def set_text_filter(self, text: str):
        """Set text filter for log entries."""
        self.filter_text = text
