# Configuration for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from pydantic import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "CustomerTUI"
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
