# Pydantic models for AgentScript pipelines
# Generated from AgentScript source: sample_pipeline.ags

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Execution status enum
class ExecutionStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'

# Base models
class PipelineExecutionBase(BaseModel):
    """Base model for pipeline execution."""
    intent_name: str = Field(..., description='Name of the intent to execute')
    input_file: Optional[str] = Field(None, description='Input file path')
    output_file: Optional[str] = Field(None, description='Output file path')

class PipelineExecutionCreate(PipelineExecutionBase):
    """Model for creating a new pipeline execution."""
    pass

class PipelineExecution(PipelineExecutionBase):
    """Complete pipeline execution model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: ExecutionStatus = ExecutionStatus.PENDING
    records_processed: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class CustomeranalysisRequest(BaseModel):
    """Request model for CustomerAnalysis pipeline."""
    input_data: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

class CustomeranalysisResponse(BaseModel):
    """Response model for CustomerAnalysis pipeline."""
    execution_id: int
    status: ExecutionStatus
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    records_processed: int = 0

class SalesreportRequest(BaseModel):
    """Request model for SalesReport pipeline."""
    input_data: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None

class SalesreportResponse(BaseModel):
    """Response model for SalesReport pipeline."""
    execution_id: int
    status: ExecutionStatus
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    records_processed: int = 0

class DataRecord(BaseModel):
    """Generic data record model."""
    id: Optional[int] = None
    data: Dict[str, Any]
    source_file: Optional[str] = None
    source_row: Optional[int] = None
    execution_id: int
    created_at: datetime

class PaginatedResponse(BaseModel):
    """Paginated response model."""
    items: List[Dict[str, Any]]
    total: int
    page: int = 1
    size: int = 50
    pages: int