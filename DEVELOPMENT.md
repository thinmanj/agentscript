# AgentScript Development Guide

This guide covers the development tooling and setup for AgentScript.

## Project Structure

```
agentscript/
├── src/agentscript/          # Core language implementation
│   ├── __init__.py          # Package initialization
│   ├── lexer.py             # Tokenizer
│   ├── parser.py            # AST parser
│   ├── ast_nodes.py         # AST node definitions
│   ├── codegen.py           # Python code generator
│   ├── error_reporter.py    # Enhanced error reporting
│   └── main.py              # CLI interface
├── examples/                 # Example AgentScript programs
├── tools/vscode/            # VSCode extension for syntax highlighting
├── tests/                   # Test suite
└── README.md                # Main documentation
```

## Development Setup

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd agentscript
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

2. **Run tests:**
```bash
pytest tests/
```

3. **Code formatting:**
```bash
black src/ tests/
isort src/ tests/
```

4. **Type checking:**
```bash
mypy src/agentscript/
```

## Development Tooling

### VSCode Extension

The `tools/vscode/` directory contains a complete VSCode extension for AgentScript:

- **Syntax highlighting** for `.ags` files
- **Code snippets** for common patterns
- **Language configuration** for proper indentation and bracket matching

To install the extension:
1. Copy `tools/vscode/` to `~/.vscode/extensions/agentscript-0.1.0/`
2. Restart VSCode
3. Open any `.ags` file to see syntax highlighting

### Enhanced Error Reporting

The error reporting system provides:

- **Context-aware messages** with source code highlighting
- **Intelligent suggestions** based on common mistakes
- **Agent-friendly explanations** for AI systems
- **Fix recommendations** with specific replacements

Example error output:
```
🚨 Lexer Error at example.ags:5:23
   Unterminated string literal

📍 Source Context:
      4 |     description: "This is missing
  →   5 |     pipeline: source.csv("data.csv")
      |                        ^

💡 Suggestions:
  1. Add a closing quote to complete the string literal
     Fix: Add closing quote (")

🤖 For AI Agents:
   This error indicates a syntax issue in the AgentScript code.
   Review the language syntax documentation and apply the suggested fixes.
   Common patterns: intent { pipeline: source -> filter -> sink }
```

### CLI Usage

Basic compilation:
```bash
# Compile single file
agentscript compile example.ags

# Compile with specific output
agentscript compile input.ags -o output.py

# Compile multiple files
agentscript compile *.ags

# Check syntax without output
agentscript compile --check example.ags
```

### Testing Framework

The test suite includes:
- **Lexer tests** for tokenization
- **Parser tests** for AST generation
- **Code generation tests** for Python output
- **Integration tests** for end-to-end compilation
- **Error reporting tests** for error handling

Run specific test categories:
```bash
pytest tests/test_lexer.py      # Lexer tests
pytest tests/test_parser.py     # Parser tests
pytest tests/test_codegen.py    # Code generation tests
pytest tests/integration/       # Integration tests
```

## Contributing

1. **Language Features:**
   - Add new AST node types in `ast_nodes.py`
   - Update lexer for new keywords/operators in `lexer.py`
   - Extend parser grammar in `parser.py`
   - Implement code generation in `codegen.py`

2. **Error Handling:**
   - Add new error types and suggestions in `error_reporter.py`
   - Update error messages with helpful context

3. **Development Tools:**
   - Update VSCode syntax highlighting in `tools/vscode/syntaxes/`
   - Add new code snippets in `tools/vscode/snippets/`

4. **Testing:**
   - Add test cases for new features
   - Include both positive and negative test cases
   - Test error conditions and edge cases

## Architecture Notes

### Compilation Pipeline

1. **Lexer** (`lexer.py`): Converts source code into tokens
2. **Parser** (`parser.py`): Builds AST from tokens using recursive descent
3. **Code Generator** (`codegen.py`): Traverses AST to generate Python code
4. **Error Reporter** (`error_reporter.py`): Provides enhanced error messages

### Design Principles

- **Agent-Friendly**: Syntax designed for AI agents to generate and understand
- **Declarative**: Focus on *what* to accomplish rather than *how*
- **Transparent**: Clean transpilation to readable Python
- **Extensible**: Easy to add new language features
- **Error-Resilient**: Helpful error messages with suggestions

### Future Enhancements

- **Multi-line pipeline support** with proper indentation handling
- **Object literal support** in lambda expressions
- **Behavior system implementation** for reusable components  
- **Resource management** for databases and APIs
- **Type inference** and static analysis
- **Debugging support** with source maps