# FastAPI Application for AgentScript Pipelines
# Generated from AgentScript source: sample_pipeline.ags
# Generated at: 2025-10-07 22:18:46

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .routers import pipelines
from .models import *

# Create FastAPI application
app = FastAPI(
    title="customer_service",
    description="Generated FastAPI application for data processing pipelines",
    version="1.0.0",
    docs_url='/docs',
    redoc_url='/redoc',
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(pipelines.router, prefix='/api/v1', tags=['pipelines'])

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )