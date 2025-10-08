# Data models for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    IDLE = 'idle'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    STOPPED = 'stopped'

@dataclass
class ExecutionResult:
    """Result of a pipeline execution."""
    execution_id: str
    intent_name: str
    status: PipelineStatus
    records_processed: int
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PipelineConfig:
    """Configuration for a pipeline."""
    name: str
    description: str
    input_formats: List[str]
    output_formats: List[str]
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

@dataclass
class CustomeranalysisConfig(PipelineConfig):
    """Configuration for CustomerAnalysis pipeline."""
    name: str = "CustomerAnalysis"
    description: str = "Analyze customer data and generate insights"
    input_formats: List[str] = None
    output_formats: List[str] = None

    def __post_init__(self):
        if self.input_formats is None:
            self.input_formats = ['csv', 'json']
        if self.output_formats is None:
            self.output_formats = ['csv', 'json']
        super().__post_init__()

@dataclass
class SalesreportConfig(PipelineConfig):
    """Configuration for SalesReport pipeline."""
    name: str = "SalesReport"
    description: str = "Generate monthly sales reports"
    input_formats: List[str] = None
    output_formats: List[str] = None

    def __post_init__(self):
        if self.input_formats is None:
            self.input_formats = ['csv', 'json']
        if self.output_formats is None:
            self.output_formats = ['csv', 'json']
        super().__post_init__()