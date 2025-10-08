# Configuration settings for FastAPI application
# Generated from AgentScript source: sample_pipeline.ags

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "customer_service"
    DEBUG: bool = True
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:8080',
    ]

    
    class Config:
        env_file = '.env'

settings = Settings()