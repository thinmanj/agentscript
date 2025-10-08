# Pipeline executor for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

import asyncio
import logging
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from .models import ExecutionResult, PipelineStatus

logger = logging.getLogger(__name__)

class PipelineExecutor:
    """Executes AgentScript pipelines with real-time updates."""
    
    def __init__(self):
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_history: List[ExecutionResult] = []
        self.progress_callbacks: Dict[str, List[Callable]] = {}

    async def execute_customer_analysis(
        self,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> ExecutionResult:
        """Execute CustomerAnalysis pipeline."""
        return await self._execute_pipeline_impl(
            'CustomerAnalysis',
            input_file,
            output_file,
            progress_callback
        )

    async def execute_sales_report(
        self,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> ExecutionResult:
        """Execute SalesReport pipeline."""
        return await self._execute_pipeline_impl(
            'SalesReport',
            input_file,
            output_file,
            progress_callback
        )

    async def execute_pipeline(
        self,
        intent_name: str,
        input_file: Optional[str] = None,
        output_file: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> ExecutionResult:
        """Execute a pipeline by intent name."""
        
        # Route to specific pipeline method
        if intent_name == 'CustomerAnalysis':
            return await self.execute_customer_analysis(input_file, output_file, progress_callback)
        elif intent_name == 'SalesReport':
            return await self.execute_sales_report(input_file, output_file, progress_callback)
        else:
            raise ValueError(f'Unknown intent: {intent_name}')

    async def _execute_pipeline_impl(
        self,
        intent_name: str,
        input_file: Optional[str],
        output_file: Optional[str],
        progress_callback: Optional[Callable]
    ) -> ExecutionResult:
        """Core pipeline execution implementation."""
        
        execution_id = f'{intent_name}_{datetime.now().isoformat()}'
        
        try:
            logger.info(f'Starting pipeline execution: {execution_id}')
            
            # Update progress
            if progress_callback:
                await progress_callback(0, 'Starting pipeline...')
            
            # Simulate pipeline execution (replace with actual AgentScript execution)
            records_processed = 0
            total_records = 1000  # Would be determined from actual data
            
            for i in range(total_records):
                # Simulate processing
                await asyncio.sleep(0.001)  # Simulate work
                records_processed += 1
                
                # Update progress every 100 records
                if records_processed % 100 == 0 and progress_callback:
                    progress = (records_processed / total_records) * 100
                    await progress_callback(progress, f'Processed {records_processed} records')
            
            # Final progress update
            if progress_callback:
                await progress_callback(100, 'Pipeline completed')
            
            result = ExecutionResult(
                execution_id=execution_id,
                intent_name=intent_name,
                status=PipelineStatus.COMPLETED,
                records_processed=records_processed,
                input_file=input_file,
                output_file=output_file,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=None
            )
            
            self.execution_history.append(result)
            logger.info(f'Pipeline execution completed: {execution_id}')
            
            return result
            
        except Exception as e:
            logger.error(f'Pipeline execution failed: {execution_id} - {e}')
            
            error_result = ExecutionResult(
                execution_id=execution_id,
                intent_name=intent_name,
                status=PipelineStatus.FAILED,
                records_processed=records_processed,
                input_file=input_file,
                output_file=output_file,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=str(e)
            )
            
            self.execution_history.append(error_result)
            raise

    def get_execution_history(self) -> List[ExecutionResult]:
        """Get execution history."""
        return self.execution_history.copy()

    def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        return list(self.active_executions.keys())

    async def stop_execution(self, execution_id: str) -> bool:
        """Stop an active execution."""
        if execution_id in self.active_executions:
            task = self.active_executions[execution_id]
            task.cancel()
            del self.active_executions[execution_id]
            return True
        return False