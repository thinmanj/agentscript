# AgentScript ↔ Repo-Tickets Integration

This document describes the bidirectional integration between AgentScript and the [repo-tickets](https://github.com/thinmanj/repo-tickets) project management system.

## Overview

The integration enables:
- **Analysis to Tickets**: Analyze AgentScript files to automatically create project tickets and epics
- **Requirements to Code**: Generate AgentScript files from ticket requirements and descriptions
- **Automated Workflows**: AI agents can manage the entire development lifecycle from requirements to code

## Features

### 📊 AgentScript Analysis
- Extracts pipeline structure, complexity, and data flow patterns
- Estimates development effort based on pipeline stages
- Categorizes operations (sources, sinks, transformations)
- Maps requirements to implementation tasks

### 🎫 Ticket Generation
- Creates epics for AgentScript pipeline projects
- Generates individual tickets for each pipeline stage
- Includes detailed task descriptions with source code references
- Supports priority assignment and AI agent delegation

### 📝 Code Generation
- Generates valid AgentScript code from ticket descriptions
- Automatically detects data formats and processing patterns
- Creates appropriate imports and pipeline structures
- Maintains traceability back to original requirements

## Installation & Setup

1. **Install AgentScript** (if not already installed):
   ```bash
   cd /path/to/agentscript
   pip install -e .
   ```

2. **Install repo-tickets** (optional, for full integration):
   ```bash
   git clone https://github.com/thinmanj/repo-tickets
   cd repo-tickets
   # Follow repo-tickets installation instructions
   # Add tickets command to your PATH
   ```

3. **Initialize tickets in your project** (if using repo-tickets):
   ```bash
   cd /path/to/your/project
   tickets init
   ```

## Usage

### Command Line Interface

#### Create Tickets from AgentScript
```bash
# Basic ticket creation
agentscript tickets create pipeline.ags

# With custom epic title and priority
agentscript tickets create data_processor.ags --epic-title "Customer Data Pipeline" --priority high

# Assign to AI agent
agentscript tickets create pipeline.ags --assign-agent ai-developer
```

#### Generate AgentScript from Tickets
```bash
# Generate from ticket ID
agentscript tickets generate TICKET-123

# Specify output file
agentscript tickets generate TICKET-456 -o custom_pipeline.ags

# Use specific template
agentscript tickets generate TICKET-789 --template advanced-pipeline
```

### Python API

#### Direct Analysis
```python
from agentscript.ticket_integration import AgentScriptTicketIntegration

integration = AgentScriptTicketIntegration()

# Analyze an AgentScript file
analysis = integration.analyze_agentscript_file(Path("pipeline.ags"))
print(f"Complexity: {analysis['complexity']}")
print(f"Estimated hours: {analysis['estimated_hours']}")
print(f"Pipeline stages: {len(analysis['pipeline_stages'])}")
```

#### Create Tickets
```python
# Create tickets from analysis
result = integration.create_tickets_from_agentscript(
    Path("pipeline.ags"),
    epic_title="Data Processing Epic",
    priority="medium",
    assign_agent="ai-dev"
)

print(f"Created epic: {result['epic_id']}")
for ticket in result['tickets']:
    print(f"- {ticket['id']}: {ticket['title']}")
```

#### Generate Code
```python
# Generate AgentScript from ticket
output_file = integration.generate_agentscript_from_ticket(
    "TICKET-123",
    output_file=Path("generated.ags"),
    template="basic-pipeline"
)

print(f"Generated: {output_file}")
```

## Demo & Examples

Run the interactive demo to see all features in action:

```bash
cd /path/to/agentscript
python3 examples/ticket_integration_demo.py
```

The demo includes:
- File analysis with complexity estimation
- Mock ticket creation (works without repo-tickets)
- Code generation from requirements
- Complete workflow demonstration

## Integration Workflow

### 1. Epic-Driven Development
```bash
# Start with requirements in tickets
tickets epic create "Customer Analytics Pipeline"

# Generate AgentScript from requirements
agentscript tickets generate EPIC-123 -o analytics.ags

# Refine and implement pipeline
# ... edit analytics.ags ...

# Create implementation tickets
agentscript tickets create analytics.ags --epic-title "Analytics Implementation"
```

### 2. Code-First Analysis
```bash
# Start with existing AgentScript
agentscript compile existing_pipeline.ags

# Analyze for project management
agentscript tickets create existing_pipeline.ags --priority high

# AI agents can now manage the tickets
tickets agent assign TICKET-456 --agent code-reviewer
```

## Ticket Templates

The integration generates tickets with rich metadata:

### Epic Template
```
Title: [Pipeline Name] Implementation
Description: Implementation of AgentScript pipeline from [filename]
Priority: [specified priority]
Labels: agentscript, pipeline, [complexity]
```

### Stage Tickets
```
Title: Implement [Stage Description]
Description: 
  Implementation task for pipeline stage N.
  
  Stage Details:
  - Type: source/sink/transform/filter
  - Operation: load_csv/save_json/etc
  - Source File: filename.ags:line
  
  Parameters:
  - File: input.csv
  
  Generated from AgentScript analysis
Labels: agentscript, [stage-type], [complexity]
```

### Compilation Tickets
```
Title: Compile and Test [Filename]
Description:
  Overall compilation and testing task.
  
  Deliverables:
  - Compile [filename] to Python
  - Generate test cases from pipeline stages  
  - Validate output format and data quality
  - Update documentation
  
  Complexity: [low/medium/high]
  Estimated Hours: [2/5/10]
Labels: agentscript, compilation, [complexity]
Estimated Hours: [based on analysis]
```

## AI Agent Integration

The integration works seamlessly with repo-tickets AI agents:

### Automated Workflows
```bash
# Set up agents for different tasks
tickets agent create code-generator --type agentscript-compiler
tickets agent create test-runner --type validation
tickets agent create docs-updater --type documentation

# Agents can automatically:
# - Generate AgentScript from requirements
# - Compile and test generated code  
# - Update documentation
# - Validate data quality
# - Report completion status
```

### Agent Configuration
```yaml
# .tickets/agents/agentscript-dev.yaml
name: agentscript-dev
type: development
capabilities:
  - agentscript-generation
  - code-compilation
  - testing
  - documentation

workflows:
  - on: ticket.created[labels.contains('agentscript')]
    do: 
      - generate_agentscript_if_needed
      - compile_to_python
      - run_basic_tests
      - update_ticket_status
```

## Configuration

### Directory Structure
```
project/
├── .tickets/                    # repo-tickets data
│   ├── tickets.json
│   ├── epics.json
│   └── agents/
├── agentscript/                 # AgentScript source files
│   ├── pipeline1.ags
│   └── pipeline2.ags
├── generated/                   # Generated Python code
│   ├── pipeline1.py
│   └── pipeline2.py
└── INTEGRATION_PLAN.md         # Integration documentation
```

### Integration Settings
```python
# Configure integration behavior
integration = AgentScriptTicketIntegration(
    project_root=Path("/path/to/project"),
)

# Custom directory structure
integration.agentscript_dir = project_root / "src" / "ags"
integration.generated_dir = project_root / "build" / "python"
```

## Troubleshooting

### Common Issues

#### "tickets command not available"
- Install repo-tickets and add to PATH
- Or use the demo mode which works without repo-tickets

#### "repo-tickets not initialized"
```bash
cd /path/to/project
tickets init
```

#### Module import errors
```bash
# Install in development mode
pip install -e /path/to/agentscript

# Or add to Python path
export PYTHONPATH="/path/to/agentscript/src:$PYTHONPATH"
```

#### Parsing errors in generated AgentScript
- Check the original ticket description for format issues
- Verify file path references are quoted properly
- Use simpler descriptions for initial testing

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run integration with detailed output
integration = AgentScriptTicketIntegration()
result = integration.analyze_agentscript_file(Path("debug.ags"))
```

## Contributing

To extend the integration:

1. **Add new templates**: Extend `_generate_pipeline_from_description()` in `ticket_integration.py`
2. **Custom analysis**: Add methods to `_analyze_pipeline_stage()`
3. **New CLI commands**: Add subparsers in `main.py`
4. **Agent workflows**: Create YAML configs in `.tickets/agents/`

## See Also

- [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) - Complete integration specification
- [repo-tickets documentation](https://github.com/thinmanj/repo-tickets)
- [AgentScript language reference](README.md)
- [Examples directory](examples/) - Sample AgentScript files

## License

This integration inherits the licenses of both AgentScript and repo-tickets projects.