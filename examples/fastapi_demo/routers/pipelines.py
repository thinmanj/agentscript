# FastAPI routes for pipeline operations
# Generated from AgentScript source: sample_pipeline.ags

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
import logging

from ..models import *
from ..tasks import execute_pipeline_task

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get('/executions', response_model=List[PipelineExecution])
async def list_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List pipeline executions with pagination."""
    # In-memory storage (replace with database in production)
    return []

@router.get('/executions/{execution_id}', response_model=PipelineExecution)
async def get_execution(
    execution_id: int,
):
    """Get details of a specific execution."""
    # Mock response for demonstration
    raise HTTPException(status_code=404, detail='Execution not found')

@router.post('/customer_analysis', response_model=CustomeranalysisResponse)
async def execute_customer_analysis(
    request: CustomeranalysisRequest,
    background_tasks: BackgroundTasks,
):
    """Execute CustomerAnalysis pipeline asynchronously."""
    try:
        # Create execution record
        # Mock execution ID for demonstration
        execution_id = 1
        
        # Start background task
        background_tasks.add_task(
            execute_pipeline_task,
            execution_id,
            'CustomerAnalysis',
            request.input_data or {},
            request.options or {}
        )
        
        return CustomeranalysisResponse(
            execution_id=execution_id,
            status=ExecutionStatus.PENDING,
            message='Pipeline CustomerAnalysis started successfully'
        )
        
    except Exception as e:
        logger.error(f'Failed to start pipeline: {e}')
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/sales_report', response_model=SalesreportResponse)
async def execute_sales_report(
    request: SalesreportRequest,
    background_tasks: BackgroundTasks,
):
    """Execute SalesReport pipeline asynchronously."""
    try:
        # Create execution record
        # Mock execution ID for demonstration
        execution_id = 1
        
        # Start background task
        background_tasks.add_task(
            execute_pipeline_task,
            execution_id,
            'SalesReport',
            request.input_data or {},
            request.options or {}
        )
        
        return SalesreportResponse(
            execution_id=execution_id,
            status=ExecutionStatus.PENDING,
            message='Pipeline SalesReport started successfully'
        )
        
    except Exception as e:
        logger.error(f'Failed to start pipeline: {e}')
        raise HTTPException(status_code=500, detail=str(e))