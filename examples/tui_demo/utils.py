# Utility functions for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

import pandas as pd
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from rich.table import Table
from rich.console import Console

def load_data_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load data from various file formats."""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix.lower() == '.json':
        return pd.read_json(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

def save_data_file(data: pd.DataFrame, file_path: Union[str, Path]) -> None:
    """Save data to various file formats."""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.csv':
        data.to_csv(file_path, index=False)
    elif file_path.suffix.lower() == '.json':
        data.to_json(file_path, orient='records', indent=2)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        data.to_excel(file_path, index=False)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_data_summary(data: pd.DataFrame) -> Dict[str, Any]:
    """Create a summary of the DataFrame."""
    return {
        'rows': len(data),
        'columns': len(data.columns),
        'memory_usage': data.memory_usage(deep=True).sum(),
        'column_types': data.dtypes.to_dict(),
        'null_counts': data.isnull().sum().to_dict(),
        'numeric_summary': data.describe().to_dict() if len(data.select_dtypes(include='number').columns) > 0 else {}
    }
