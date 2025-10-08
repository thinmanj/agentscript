"""
FastAPI Plugin for AgentScript

This plugin generates modern async FastAPI applications from AgentScript pipeline definitions.
It creates Pydantic models, async API endpoints with automatic OpenAPI documentation,
background task processing, and optional database integration.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .base import BasePlugin, GenerationContext, PluginConfig
from ..ast_nodes import Program, IntentDeclaration, PipelineStage, FunctionCall, AttributeAccess, Literal


class FastAPIPlugin(BasePlugin):
    """FastAPI async web framework code generator."""
    
    plugin_name = "fastapi"
    plugin_description = "Generate modern async FastAPI applications with Pydantic models"
    plugin_version = "1.0.0"
    plugin_dependencies = ["fastapi[all]>=0.104.0", "uvicorn[standard]>=0.24.0", "pydantic>=2.0"]
    plugin_optional_dependencies = ["sqlalchemy>=2.0", "asyncpg", "aiomysql", "celery", "redis"]
    plugin_output_extension = ".py"
    plugin_supports_async = True
    plugin_supports_web = True
    plugin_supports_database = True
    plugin_supports_auth = True
    
    @property
    def name(self) -> str:
        return "fastapi"
    
    @property
    def description(self) -> str:
        return "Generate modern async FastAPI applications with automatic OpenAPI docs"
    
    def generate_code(self, ast: Program, context: GenerationContext) -> Dict[str, str]:
        """Generate FastAPI application code from AgentScript AST."""
        files = {}
        
        # Extract intents from AST
        intents = [stmt for stmt in ast.statements if isinstance(stmt, IntentDeclaration)]
        
        if not intents:
            return files
        
        # Generate main FastAPI application
        files["main.py"] = self._generate_main_app(intents, context)
        
        # Generate Pydantic models
        files["models.py"] = self._generate_models_file(intents, context)
        
        # Generate API routes
        files["routers/__init__.py"] = ""
        files["routers/pipelines.py"] = self._generate_pipeline_routes(intents, context)
        
        # Generate background tasks
        files["tasks.py"] = self._generate_background_tasks(intents, context)
        
        # Generate database integration if enabled
        if context.options.get('database', False):
            files["database.py"] = self._generate_database_config(context)
            files["crud.py"] = self._generate_crud_operations(intents, context)
        
        # Generate configuration
        files["config.py"] = self._generate_config_file(context)
        
        # Generate dependencies
        files["dependencies.py"] = self._generate_dependencies(context)
        
        # Generate requirements
        files["requirements.txt"] = self._generate_requirements(context)
        
        # Generate Docker files
        files["Dockerfile"] = self._generate_dockerfile(context)
        files["docker-compose.yml"] = self._generate_docker_compose(context)
        
        # Generate startup script
        files["start.sh"] = self._generate_startup_script(context)
        
        return files
    
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """Get required dependencies for FastAPI project."""
        deps = self.plugin_dependencies.copy()
        
        # Add database dependencies
        if context.options.get('database', False):
            deps.append('sqlalchemy>=2.0')
            database = context.options.get('database_type', 'sqlite')
            if database == 'postgresql':
                deps.append('asyncpg>=0.28')
            elif database == 'mysql':
                deps.append('aiomysql>=0.1')
        
        # Add background task processing
        if context.options.get('background_tasks', True):
            deps.extend(['celery>=5.2', 'redis>=4.3'])
        
        # Add authentication
        if context.options.get('auth', False):
            deps.extend(['python-jose[cryptography]>=3.3', 'passlib[bcrypt]>=1.7'])
        
        return deps
    
    def _generate_main_app(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate main FastAPI application file."""
        lines = [
            f"# FastAPI Application for AgentScript Pipelines",
            f"# Generated from AgentScript source: {context.source_file.name}",
            f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from fastapi.responses import JSONResponse",
            "import uvicorn",
            "",
            "from .config import settings",
            "from .routers import pipelines",
            "from .models import *",
        ]
        
        if context.options.get('database', False):
            lines.extend([
                "from .database import engine, Base",
                "from .crud import *",
            ])
        
        lines.extend([
            "",
            "# Create FastAPI application",
            "app = FastAPI(",
            f'    title="{context.options.get("app_name", "AgentScript Pipelines")}",',
            f'    description="Generated FastAPI application for data processing pipelines",',
            f'    version="1.0.0",',
            "    docs_url='/docs',",
            "    redoc_url='/redoc',",
            ")",
            "",
            "# Add CORS middleware",
            "app.add_middleware(",
            "    CORSMiddleware,",
            "    allow_origins=settings.CORS_ORIGINS,",
            "    allow_credentials=True,",
            "    allow_methods=['*'],",
            "    allow_headers=['*'],",
            ")",
            "",
            "# Include routers",
            "app.include_router(pipelines.router, prefix='/api/v1', tags=['pipelines'])",
            "",
        ])
        
        # Add startup/shutdown events
        if context.options.get('database', False):
            lines.extend([
                "@app.on_event('startup')",
                "async def startup_event():",
                "    # Create database tables",
                "    async with engine.begin() as conn:",
                "        await conn.run_sync(Base.metadata.create_all)",
                "",
                "@app.on_event('shutdown')",
                "async def shutdown_event():",
                "    # Clean up resources",
                "    await engine.dispose()",
                "",
            ])
        
        # Add health check endpoint
        lines.extend([
            "@app.get('/health')",
            "async def health_check():",
            "    return {'status': 'healthy', 'version': '1.0.0'}",
            "",
            "if __name__ == '__main__':",
            "    uvicorn.run(",
            "        'main:app',",
            "        host=settings.HOST,",
            "        port=settings.PORT,",
            "        reload=settings.DEBUG,",
            "        workers=1 if settings.DEBUG else 4",
            "    )",
        ])
        
        return "\n".join(lines)
    
    def _generate_models_file(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate Pydantic models."""
        lines = [
            f"# Pydantic models for AgentScript pipelines",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from pydantic import BaseModel, Field, ConfigDict",
            "from typing import Optional, List, Dict, Any, Union",
            "from datetime import datetime",
            "from enum import Enum",
            "",
            "# Execution status enum",
            "class ExecutionStatus(str, Enum):",
            "    PENDING = 'pending'",
            "    RUNNING = 'running'",
            "    COMPLETED = 'completed'",
            "    FAILED = 'failed'",
            "",
            "# Base models",
            "class PipelineExecutionBase(BaseModel):",
            '    """Base model for pipeline execution."""',
            "    intent_name: str = Field(..., description='Name of the intent to execute')",
            "    input_file: Optional[str] = Field(None, description='Input file path')",
            "    output_file: Optional[str] = Field(None, description='Output file path')",
            "",
            "class PipelineExecutionCreate(PipelineExecutionBase):",
            '    """Model for creating a new pipeline execution."""',
            "    pass",
            "",
            "class PipelineExecution(PipelineExecutionBase):",
            '    """Complete pipeline execution model."""',
            "    model_config = ConfigDict(from_attributes=True)",
            "    ",
            "    id: int",
            "    status: ExecutionStatus = ExecutionStatus.PENDING",
            "    records_processed: int = 0",
            "    error_message: Optional[str] = None",
            "    created_at: datetime",
            "    updated_at: Optional[datetime] = None",
            "",
        ]
        
        # Generate models for each intent
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"class {model_name}Request(BaseModel):",
                f'    """Request model for {intent.name} pipeline."""',
                "    input_data: Optional[Dict[str, Any]] = None",
                "    options: Optional[Dict[str, Any]] = None",
                "",
                f"class {model_name}Response(BaseModel):",
                f'    """Response model for {intent.name} pipeline."""',
                "    execution_id: int",
                "    status: ExecutionStatus",
                "    message: str",
                "    data: Optional[List[Dict[str, Any]]] = None",
                "    records_processed: int = 0",
                "",
            ])
        
        # Add generic data models
        lines.extend([
            "class DataRecord(BaseModel):",
            '    """Generic data record model."""',
            "    id: Optional[int] = None",
            "    data: Dict[str, Any]",
            "    source_file: Optional[str] = None",
            "    source_row: Optional[int] = None",
            "    execution_id: int",
            "    created_at: datetime",
            "",
            "class PaginatedResponse(BaseModel):",
            '    """Paginated response model."""',
            "    items: List[Dict[str, Any]]",
            "    total: int",
            "    page: int = 1",
            "    size: int = 50",
            "    pages: int",
        ])
        
        return "\n".join(lines)
    
    def _generate_pipeline_routes(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate FastAPI router for pipeline operations."""
        lines = [
            f"# FastAPI routes for pipeline operations",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query",
            "from fastapi.responses import JSONResponse",
            "from typing import List, Optional",
            "import asyncio",
            "import logging",
            "",
            "from ..models import *",
            "from ..tasks import execute_pipeline_task",
        ]
        
        if context.options.get('database', False):
            lines.append("from ..crud import *")
            lines.append("from ..dependencies import get_db")
        
        lines.extend([
            "",
            "router = APIRouter()",
            "logger = logging.getLogger(__name__)",
            "",
            "@router.get('/executions', response_model=List[PipelineExecution])",
            "async def list_executions(",
            "    skip: int = Query(0, ge=0),",
            "    limit: int = Query(100, ge=1, le=1000),",
        ])
        
        if context.options.get('database', False):
            lines.append("    db = Depends(get_db)")
        
        lines.extend([
            "):",
            '    """List pipeline executions with pagination."""',
        ])
        
        if context.options.get('database', False):
            lines.extend([
                "    return await get_executions(db, skip=skip, limit=limit)",
            ])
        else:
            lines.extend([
                "    # In-memory storage (replace with database in production)",
                "    return []",
            ])
        
        lines.extend([
            "",
            "@router.get('/executions/{execution_id}', response_model=PipelineExecution)",
            "async def get_execution(",
            "    execution_id: int,",
        ])
        
        if context.options.get('database', False):
            lines.append("    db = Depends(get_db)")
        
        lines.extend([
            "):",
            '    """Get details of a specific execution."""',
        ])
        
        if context.options.get('database', False):
            lines.extend([
                "    execution = await get_execution_by_id(db, execution_id)",
                "    if not execution:",
                "        raise HTTPException(status_code=404, detail='Execution not found')",
                "    return execution",
            ])
        else:
            lines.extend([
                "    # Mock response for demonstration",
                "    raise HTTPException(status_code=404, detail='Execution not found')",
            ])
        
        # Generate endpoints for each intent
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            endpoint_name = self._to_snake_case(intent.name)
            
            lines.extend([
                "",
                f"@router.post('/{endpoint_name}', response_model={model_name}Response)",
                f"async def execute_{endpoint_name}(",
                f"    request: {model_name}Request,",
                "    background_tasks: BackgroundTasks,",
            ])
            
            if context.options.get('database', False):
                lines.append("    db = Depends(get_db)")
            
            lines.extend([
                "):",
                f'    """Execute {intent.name} pipeline asynchronously."""',
                "    try:",
                "        # Create execution record",
            ])
            
            if context.options.get('database', False):
                lines.extend([
                    "        execution = await create_execution(",
                    "            db,",
                    "            PipelineExecutionCreate(",
                    f"                intent_name='{intent.name}',",
                    "                input_file=request.input_data.get('input_file') if request.input_data else None,",
                    "                output_file=request.input_data.get('output_file') if request.input_data else None",
                    "            )",
                    "        )",
                ])
            else:
                lines.extend([
                    "        # Mock execution ID for demonstration",
                    "        execution_id = 1",
                ])
            
            lines.extend([
                "        ",
                "        # Start background task",
                "        background_tasks.add_task(",
                "            execute_pipeline_task,",
            ])
            
            if context.options.get('database', False):
                lines.extend([
                    "            execution.id,",
                    f"            '{intent.name}',",
                ])
            else:
                lines.extend([
                    "            execution_id,",
                    f"            '{intent.name}',",
                ])
            
            lines.extend([
                "            request.input_data or {},",
                "            request.options or {}",
                "        )",
                "        ",
                f"        return {model_name}Response(",
            ])
            
            if context.options.get('database', False):
                lines.extend([
                    "            execution_id=execution.id,",
                    "            status=execution.status,",
                ])
            else:
                lines.extend([
                    "            execution_id=execution_id,",
                    "            status=ExecutionStatus.PENDING,",
                ])
            
            lines.extend([
                f"            message='Pipeline {intent.name} started successfully'",
                "        )",
                "        ",
                "    except Exception as e:",
                "        logger.error(f'Failed to start pipeline: {e}')",
                "        raise HTTPException(status_code=500, detail=str(e))",
            ])
        
        return "\n".join(lines)
    
    def _generate_background_tasks(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate background task processing."""
        lines = [
            f"# Background tasks for pipeline execution",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "import asyncio",
            "import logging",
            "import traceback",
            "from typing import Dict, Any",
            "",
            "from .models import ExecutionStatus",
        ]
        
        if context.options.get('database', False):
            lines.extend([
                "from .database import get_db",
                "from .crud import update_execution_status",
            ])
        
        lines.extend([
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "async def execute_pipeline_task(",
            "    execution_id: int,",
            "    intent_name: str,",
            "    input_data: Dict[str, Any],",
            "    options: Dict[str, Any]",
            "):",
            '    """Execute a pipeline in the background."""',
            "    logger.info(f'Starting pipeline execution {execution_id}: {intent_name}')",
            "    ",
            "    try:",
        ])
        
        if context.options.get('database', False):
            lines.extend([
                "        # Update status to running",
                "        async with get_db() as db:",
                "            await update_execution_status(db, execution_id, ExecutionStatus.RUNNING)",
            ])
        
        lines.extend([
            "        ",
            "        # Execute the actual pipeline based on intent",
            "        result = await _execute_pipeline(intent_name, input_data, options)",
            "        ",
        ])
        
        if context.options.get('database', False):
            lines.extend([
                "        # Update status to completed",
                "        async with get_db() as db:",
                "            await update_execution_status(",
                "                db, execution_id, ExecutionStatus.COMPLETED,",
                "                records_processed=result.get('records_processed', 0)",
                "            )",
            ])
        
        lines.extend([
            "        ",
            "        logger.info(f'Pipeline execution {execution_id} completed successfully')",
            "        ",
            "    except Exception as e:",
            "        logger.error(f'Pipeline execution {execution_id} failed: {e}')",
            "        logger.error(traceback.format_exc())",
            "        ",
        ])
        
        if context.options.get('database', False):
            lines.extend([
                "        # Update status to failed",
                "        async with get_db() as db:",
                "            await update_execution_status(",
                "                db, execution_id, ExecutionStatus.FAILED,",
                "                error_message=str(e)",
                "            )",
            ])
        
        lines.extend([
            "",
            "async def _execute_pipeline(",
            "    intent_name: str,",
            "    input_data: Dict[str, Any],",
            "    options: Dict[str, Any]",
            ") -> Dict[str, Any]:",
            '    """Execute the actual pipeline logic."""',
            "    # This would contain the actual pipeline execution logic",
            "    # generated from AgentScript AST",
            "    ",
            "    await asyncio.sleep(1)  # Simulate work",
            "    ",
            "    return {",
            "        'records_processed': 100,",
            "        'output_file': options.get('output_file', 'output.json')",
            "    }",
        ])
        
        return "\n".join(lines)
    
    def _generate_database_config(self, context: GenerationContext) -> str:
        """Generate SQLAlchemy database configuration."""
        database_type = context.options.get('database_type', 'sqlite')
        
        lines = [
            f"# Database configuration for FastAPI application",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession",
            "from sqlalchemy.ext.declarative import declarative_base",
            "from sqlalchemy.orm import sessionmaker",
            "from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey",
            "from sqlalchemy.dialects.postgresql import JSONB",
            "from datetime import datetime",
            "",
            "from .config import settings",
            "",
            "# Create async engine",
            "engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)",
            "",
            "# Create async session factory",
            "AsyncSessionLocal = sessionmaker(",
            "    engine, class_=AsyncSession, expire_on_commit=False",
            ")",
            "",
            "# Base class for models",
            "Base = declarative_base()",
            "",
            "class PipelineExecutionDB(Base):",
            "    __tablename__ = 'pipeline_executions'",
            "    ",
            "    id = Column(Integer, primary_key=True, index=True)",
            "    intent_name = Column(String(100), nullable=False)",
            "    status = Column(String(20), nullable=False, default='pending')",
            "    input_file = Column(String(255))",
            "    output_file = Column(String(255))",
            "    records_processed = Column(Integer, default=0)",
            "    error_message = Column(Text)",
            "    created_at = Column(DateTime, default=datetime.utcnow)",
            "    updated_at = Column(DateTime, onupdate=datetime.utcnow)",
            "",
            "class DataRecordDB(Base):",
            "    __tablename__ = 'data_records'",
            "    ",
            "    id = Column(Integer, primary_key=True, index=True)",
            "    execution_id = Column(Integer, ForeignKey('pipeline_executions.id'))",
        ]
        
        if database_type == 'postgresql':
            lines.append("    data = Column(JSONB)")
        else:
            lines.append("    data = Column(Text)  # JSON as text for SQLite/MySQL")
        
        lines.extend([
            "    source_file = Column(String(255))",
            "    source_row = Column(Integer)",
            "    created_at = Column(DateTime, default=datetime.utcnow)",
            "",
            "async def get_db():",
            '    """Dependency to get database session."""',
            "    async with AsyncSessionLocal() as session:",
            "        try:",
            "            yield session",
            "        finally:",
            "            await session.close()",
        ])
        
        return "\n".join(lines)
    
    def _generate_crud_operations(self, intents: List[IntentDeclaration], context: GenerationContext) -> str:
        """Generate CRUD operations for database models."""
        lines = [
            f"# CRUD operations for database models",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from sqlalchemy.ext.asyncio import AsyncSession",
            "from sqlalchemy.future import select",
            "from sqlalchemy.orm import selectinload",
            "from typing import List, Optional",
            "",
            "from .database import PipelineExecutionDB, DataRecordDB",
            "from .models import PipelineExecutionCreate, ExecutionStatus",
            "",
            "async def create_execution(",
            "    db: AsyncSession,",
            "    execution: PipelineExecutionCreate",
            ") -> PipelineExecutionDB:",
            '    """Create a new pipeline execution."""',
            "    db_execution = PipelineExecutionDB(**execution.dict())",
            "    db.add(db_execution)",
            "    await db.commit()",
            "    await db.refresh(db_execution)",
            "    return db_execution",
            "",
            "async def get_execution_by_id(",
            "    db: AsyncSession,",
            "    execution_id: int",
            ") -> Optional[PipelineExecutionDB]:",
            '    """Get execution by ID."""',
            "    result = await db.execute(",
            "        select(PipelineExecutionDB).where(PipelineExecutionDB.id == execution_id)",
            "    )",
            "    return result.scalar_one_or_none()",
            "",
            "async def get_executions(",
            "    db: AsyncSession,",
            "    skip: int = 0,",
            "    limit: int = 100",
            ") -> List[PipelineExecutionDB]:",
            '    """Get paginated list of executions."""',
            "    result = await db.execute(",
            "        select(PipelineExecutionDB)",
            "        .offset(skip)",
            "        .limit(limit)",
            "        .order_by(PipelineExecutionDB.created_at.desc())",
            "    )",
            "    return result.scalars().all()",
            "",
            "async def update_execution_status(",
            "    db: AsyncSession,",
            "    execution_id: int,",
            "    status: ExecutionStatus,",
            "    records_processed: Optional[int] = None,",
            "    error_message: Optional[str] = None",
            "):",
            '    """Update execution status and metadata."""',
            "    result = await db.execute(",
            "        select(PipelineExecutionDB).where(PipelineExecutionDB.id == execution_id)",
            "    )",
            "    execution = result.scalar_one_or_none()",
            "    ",
            "    if execution:",
            "        execution.status = status",
            "        if records_processed is not None:",
            "            execution.records_processed = records_processed",
            "        if error_message is not None:",
            "            execution.error_message = error_message",
            "        ",
            "        await db.commit()",
            "        await db.refresh(execution)",
            "    ",
            "    return execution",
        ]
        
        return "\n".join(lines)
    
    def _generate_config_file(self, context: GenerationContext) -> str:
        """Generate configuration file."""
        lines = [
            f"# Configuration settings for FastAPI application",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from pydantic_settings import BaseSettings",
            "from typing import List",
            "",
            "class Settings(BaseSettings):",
            '    """Application settings."""',
            f'    APP_NAME: str = "{context.options.get("app_name", "AgentScript Pipelines")}"',
            "    DEBUG: bool = True",
            "    HOST: str = '0.0.0.0'",
            "    PORT: int = 8000",
            "    ",
            "    # CORS settings",
            "    CORS_ORIGINS: List[str] = [",
            "        'http://localhost:3000',",
            "        'http://localhost:3001',",
            "        'http://localhost:8080',",
            "    ]",
            "",
        ]
        
        if context.options.get('database', False):
            database_type = context.options.get('database_type', 'sqlite')
            if database_type == 'postgresql':
                lines.extend([
                    "    # Database settings",
                    "    DATABASE_URL: str = 'postgresql+asyncpg://user:password@localhost/dbname'",
                ])
            elif database_type == 'mysql':
                lines.extend([
                    "    # Database settings", 
                    "    DATABASE_URL: str = 'mysql+aiomysql://user:password@localhost/dbname'",
                ])
            else:
                lines.extend([
                    "    # Database settings",
                    "    DATABASE_URL: str = 'sqlite+aiosqlite:///./app.db'",
                ])
        
        lines.extend([
            "    ",
            "    class Config:",
            "        env_file = '.env'",
            "",
            "settings = Settings()",
        ])
        
        return "\n".join(lines)
    
    def _generate_dependencies(self, context: GenerationContext) -> str:
        """Generate FastAPI dependencies."""
        lines = [
            f"# FastAPI dependencies",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from fastapi import Depends, HTTPException, status",
            "from typing import AsyncGenerator",
        ]
        
        if context.options.get('database', False):
            lines.extend([
                "",
                "from .database import AsyncSessionLocal",
                "",
                "async def get_db() -> AsyncGenerator:",
                '    """Dependency to get database session."""',
                "    async with AsyncSessionLocal() as session:",
                "        try:",
                "            yield session",
                "        finally:",
                "            await session.close()",
            ])
        
        if context.options.get('auth', False):
            lines.extend([
                "",
                "# Authentication dependencies would go here",
                "async def get_current_user():",
                "    # Implement authentication logic",
                "    pass",
            ])
        
        return "\n".join(lines)
    
    def _generate_requirements(self, context: GenerationContext) -> str:
        """Generate requirements.txt file."""
        deps = self.get_dependencies(context)
        return "\n".join(deps) + "\n"
    
    def _generate_dockerfile(self, context: GenerationContext) -> str:
        """Generate Dockerfile for containerization."""
        return f"""# Dockerfile for FastAPI application
# Generated from AgentScript source: {context.source_file.name}

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _generate_docker_compose(self, context: GenerationContext) -> str:
        """Generate docker-compose.yml file."""
        lines = [
            f"# Docker Compose for FastAPI application",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "version: '3.8'",
            "",
            "services:",
            "  app:",
            "    build: .",
            "    ports:",
            "      - '8000:8000'",
            "    environment:",
            "      - DEBUG=false",
            "    volumes:",
            "      - .:/app",
        ]
        
        if context.options.get('database', False):
            database_type = context.options.get('database_type', 'sqlite')
            if database_type == 'postgresql':
                lines.extend([
                    "    depends_on:",
                    "      - db",
                    "    environment:",
                    "      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/agentscript",
                    "",
                    "  db:",
                    "    image: postgres:15",
                    "    environment:",
                    "      - POSTGRES_DB=agentscript", 
                    "      - POSTGRES_USER=postgres",
                    "      - POSTGRES_PASSWORD=password",
                    "    volumes:",
                    "      - postgres_data:/var/lib/postgresql/data",
                    "    ports:",
                    "      - '5432:5432'",
                ])
            elif database_type == 'mysql':
                lines.extend([
                    "    depends_on:",
                    "      - db",
                    "    environment:",
                    "      - DATABASE_URL=mysql+aiomysql://mysql:password@db:3306/agentscript",
                    "",
                    "  db:",
                    "    image: mysql:8.0",
                    "    environment:",
                    "      - MYSQL_DATABASE=agentscript",
                    "      - MYSQL_USER=mysql",
                    "      - MYSQL_PASSWORD=password",
                    "      - MYSQL_ROOT_PASSWORD=rootpassword",
                    "    volumes:",
                    "      - mysql_data:/var/lib/mysql",
                    "    ports:",
                    "      - '3306:3306'",
                ])
        
        if context.options.get('background_tasks', True):
            lines.extend([
                "",
                "  redis:",
                "    image: redis:7-alpine",
                "    ports:",
                "      - '6379:6379'",
            ])
        
        if context.options.get('database', False):
            database_type = context.options.get('database_type', 'sqlite')
            if database_type in ['postgresql', 'mysql']:
                lines.extend([
                    "",
                    "volumes:",
                    f"  {database_type}_data:",
                ])
        
        return "\n".join(lines)
    
    def _generate_startup_script(self, context: GenerationContext) -> str:
        """Generate startup script."""
        return f"""#!/bin/bash
# Startup script for FastAPI application
# Generated from AgentScript source: {context.source_file.name}

set -e

echo "Starting AgentScript FastAPI application..."

# Wait for database if configured
if [ "${{DATABASE_URL:-}}" ]; then
    echo "Waiting for database..."
    python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database import Base

async def wait_for_db():
    engine = create_async_engine('$DATABASE_URL')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

asyncio.run(wait_for_db())
"
fi

# Start the application
exec python -m uvicorn main:app --host 0.0.0.0 --port ${{PORT:-8000}} --workers ${{WORKERS:-1}}
"""
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        return "".join(word.capitalize() for word in name.replace("_", " ").split())
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()