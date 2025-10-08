# AgentScript TUI Application
# Generated from AgentScript source: sample_pipeline.ags
# Generated at: 2025-10-07 22:18:35

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, TabbedContent, TabPane
from textual.binding import Binding
import asyncio
import logging

from .screens.main_screen import MainScreen
from .screens.pipeline_screen import PipelineScreen
from .screens.data_screen import DataScreen
from .config import settings
from .executor import PipelineExecutor

class AgentScriptTUI(App):
    """AgentScript Terminal User Interface Application."""
    
    TITLE = "CustomerTUI"
    SUB_TITLE = "Interactive Data Pipeline Processing"

    CSS_PATH = 'styles.css'
    
    BINDINGS = [
        Binding('q', 'quit', 'Quit'),
        Binding('d', 'toggle_dark', 'Toggle Dark Mode'),
        Binding('s', 'screenshot', 'Screenshot'),
        Binding('1', 'switch_screen("main")', 'Main'),
        Binding('2', 'switch_screen("pipeline")', 'Pipelines'),
        Binding('3', 'switch_screen("data")', 'Data'),
    ]

    def __init__(self):
        super().__init__()
        self.executor = PipelineExecutor()
        self.dark = True

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = self.TITLE
        self.sub_title = self.SUB_TITLE
        self.install_screen(MainScreen(self.executor), name='main')
        self.install_screen(PipelineScreen(self.executor), name='pipeline')
        self.install_screen(DataScreen(self.executor), name='data')
        self.switch_screen('main')

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_switch_screen(self, screen: str) -> None:
        """Switch to a specific screen."""
        self.switch_screen(screen)

    def action_screenshot(self) -> None:
        """Take a screenshot."""
        path = self.save_screenshot()
        self.notify(f'Screenshot saved to {path}')

    async def execute_customer_analysis(self, **kwargs):
        """Execute CustomerAnalysis pipeline."""
        return await self.executor.execute_pipeline('CustomerAnalysis', **kwargs)

    async def execute_sales_report(self, **kwargs):
        """Execute SalesReport pipeline."""
        return await self.executor.execute_pipeline('SalesReport', **kwargs)

def main():
    """Main entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tui_app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run the TUI application
    app = AgentScriptTUI()
    app.run()

if __name__ == '__main__':
    main()