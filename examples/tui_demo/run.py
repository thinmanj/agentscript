#!/usr/bin/env python3
# Run script for AgentScript TUI
# Generated from AgentScript source: sample_pipeline.ags

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import main

if __name__ == "__main__":
    main()
