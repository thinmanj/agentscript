# Data viewer widget for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from textual.widget import Widget
from textual.widgets import DataTable, Static, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
import pandas as pd
from typing import Optional, Dict, Any
import json

class DataViewer(Widget):
    """Widget for viewing and exploring processed data."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data: Optional[pd.DataFrame] = None
        self.current_page = reactive(0)
        self.page_size = 50
        
    def compose(self):
        """Compose the data viewer widget."""
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
        """Load data into the viewer."""
        self.data = data
        self._update_table()

    def _update_table(self):
        """Update the data table display."""
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
        page_info.update(f'Page {self.current_page + 1} of {total_pages}')

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button press events."""
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
        """Export current data to file."""
        if self.data is None:
            return
            
        # Simple CSV export
        filename = f'export_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'
        self.data.to_csv(filename, index=False)
        self.notify(f'Data exported to {filename}')
