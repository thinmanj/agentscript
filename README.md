# AgentScript

> A declarative language designed for agentic program creation that transpiles to clean, readable Python.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/status-alpha-orange.svg)

## Overview

AgentScript is a domain-specific language (DSL) specifically designed to be intuitive for AI agents to generate and understand, while producing clean, maintainable Python code. It focuses on declarative data processing pipelines using natural language concepts that align with how agents think about problems.

## Key Features

- 🤖 **Agent-Friendly**: Syntax designed for AI agents to naturally generate and understand
- 📊 **Pipeline-Oriented**: Declarative data flow using `->` operators
- 🔄 **Transparent Transpilation**: Generates clean, readable Python with pandas integration
- 🛠️ **Rich Tooling**: VSCode extension with syntax highlighting and intelligent error reporting
- 📝 **Intent-Based**: Focus on *what* to accomplish rather than *how*

## Quick Start

### Installation

```bash
pip install agentscript
```

### Basic Example

Create a file `process_users.ags`:

```agentscript
// AgentScript Example
use io.csv, io.json

intent ProcessUsers {
    description: "Process user data with age filtering"
    
    pipeline: 
        source.csv("users.csv") 
        -> filter(user => user.age >= 18) 
        -> sink.json("adults.json")
    
    on_error: log_and_continue
}
```

Compile to Python:

```bash
agentscript compile process_users.ags
```

Generated Python output:

```python
import csv, json, pandas as pd

class ProcessUsers:
    """Process user data with age filtering"""
    
    def process_users(self, input_file: str = None, output_file: str = None):
        """Process user data with age filtering"""
        
        try:
            # Load data
            df = pd.read_csv("users.csv")
            df = df.query('age >= 18')
            df.to_json("adults.json", orient='records', indent=2)
            
            return df
        except Exception as e:
            self.validation_errors.append({'error': str(e)})
            raise
```

## Language Syntax

### Core Constructs

#### Intent Declarations
```agentscript
intent DataProcessor {
    description: "High-level description of what this does"
    pipeline: source -> transform -> sink
    on_error: log_and_continue
}
```

#### Pipeline Operations
```agentscript
// Data sources
source.csv("data.csv")
source.json("data.json")

// Transformations
filter(record => record.value > 100)
transform(record => { name: record.name, processed: true })

// Data sinks
sink.csv("output.csv")
sink.json("output.json")
```

#### Lambda Expressions
```agentscript
filter(user => user.age >= 21 and user.active == true)
```

### Data Processing Examples

**CSV Processing:**
```agentscript
use io.csv

intent ProcessSales {
    description: "Filter high-value sales"
    pipeline: source.csv("sales.csv") -> filter(sale => sale.amount > 1000) -> sink.csv("high_value_sales.csv")
}
```

**JSON Transformation:**
```agentscript
use io.csv, io.json

intent ConvertData {
    description: "Convert CSV to JSON with filtering"
    pipeline: source.csv("input.csv") -> filter(row => row.active == true) -> sink.json("output.json")
}
```
}
```

## Development Tools

### VSCode Extension

AgentScript includes a complete VSCode extension with:
- Syntax highlighting for `.ags` files
- Code snippets for common patterns
- Intelligent auto-completion
- Error highlighting

Install by copying `tools/vscode/` to your VSCode extensions directory.

### Enhanced Error Reporting

AgentScript provides comprehensive error messages with context and suggestions:

```
🚨 Parse Error at example.ags:5:23
   Unexpected token: 'import'

📍 Source Context:
      4 |     description: "Process data"
  →   5 |     import pandas as pd
      |            ^

💡 Suggestions:
  1. AgentScript uses 'use' instead of 'import'
     Fix: use

🤖 For AI Agents:
   This error indicates a syntax issue in the AgentScript code.
   Review the language syntax documentation and apply the suggested fixes.
   Common patterns: intent { pipeline: source -> filter -> sink }
```

## CLI Usage

```bash
# Compile single file
agentscript compile example.ags

# Compile with specific output
agentscript compile input.ags -o output.py

# Compile multiple files
agentscript compile *.ags

# Check syntax without generating output
agentscript compile --check example.ags

# Show version
agentscript version
```

## Architecture

AgentScript follows a traditional compiler pipeline optimized for agent-friendliness:

1. **Lexer**: Tokenizes AgentScript source with agent-friendly keywords
2. **Parser**: Builds AST using recursive descent parsing
3. **Code Generator**: Produces clean Python with proper imports and structure
4. **Error Reporter**: Provides contextual, actionable error messages

## Design Philosophy

### Agent-First Design
- Syntax that aligns with how AI agents naturally think about data processing
- Natural language keywords (`intent`, `pipeline`, `filter`)
- Declarative approach focusing on outcomes rather than implementation

### Human-Readable Output
- Generated Python code is clean and well-documented
- Proper type hints and error handling
- Maintainable structure that humans can easily modify

### Extensible Architecture
- Easy to add new data sources and transformations
- Plugin system for custom behaviors
- Clear separation of concerns in the compiler pipeline

## Contributing

We welcome contributions! Please see [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development setup and guidelines.

### Quick Development Setup

```bash
git clone https://github.com/julio/agentscript.git
cd agentscript
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
pytest tests/
```

## Roadmap

- [ ] **Multi-line Pipeline Support**: Better handling of complex, indented pipelines
- [ ] **Object Literal Support**: Full support for object transformations in lambda expressions
- [ ] **Behavior System**: Reusable component definitions
- [ ] **Resource Management**: Built-in support for databases and APIs
- [ ] **Type System**: Static type checking and inference
- [ ] **Debugging Tools**: Source maps and debugging support

## Examples

See the `examples/` directory for more comprehensive examples:

- [`examples/simple.ags`](examples/simple.ags) - Basic CSV processing
- [`examples/data_pipeline.ags`](examples/data_pipeline.ags) - Advanced filtering and transformations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Julio Merino**
- GitHub: [@julio](https://github.com/julio)

## Acknowledgments

- Inspired by the need for agent-friendly programming languages
- Built with modern compiler design principles
- Designed for the age of AI-assisted programming

---

*AgentScript: Making agentic program creation intuitive and transparent.*
4. Create IDE tooling for syntax highlighting and error checking