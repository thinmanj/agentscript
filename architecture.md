# AgentScript Transpiler Architecture

## Overview

The AgentScript transpiler follows a traditional compiler pipeline with agent-specific optimizations:

```
AgentScript (.ags) → Lexer → Parser → AST → Semantic Analysis → Code Generator → Python (.py)
```

## Architecture Components

### 1. Lexer (Tokenizer)
- Converts raw AgentScript text into tokens
- Handles keywords, operators, literals, identifiers
- Supports both symbolic (`->`) and natural language operators (`then`, `where`)

### 2. Parser
- Builds Abstract Syntax Tree (AST) from tokens
- Uses recursive descent parsing for readability
- Handles operator precedence and associativity
- Supports error recovery for IDE integration

### 3. AST Nodes
Core AST node types:
- `IntentDeclaration`: Top-level intent blocks
- `BehaviorDeclaration`: Custom behavior definitions
- `PipelineExpression`: Data flow pipelines
- `FilterExpression`: Data filtering operations
- `TransformExpression`: Data transformations
- `ValidationExpression`: Data validation rules

### 4. Semantic Analyzer
- Type inference and checking
- Dependency resolution
- Resource validation
- Intent-to-implementation mapping

### 5. Code Generator
- Converts AST to Python code
- Maintains code quality and readability
- Generates appropriate imports and class structures
- Preserves comments and documentation

## Key Design Decisions

### 1. Intent-First Design
```agentscript
intent ProcessData {
    description: "High-level description of what this does"
    pipeline: /* implementation */
}
```
Transpiles to well-documented Python classes with clear method names and docstrings.

### 2. Pipeline Abstraction
```agentscript
source.csv("data.csv") -> filter(age > 18) -> sink.json("output.json")
```
Becomes a readable method chain in Python with proper error handling.

### 3. Behavior Reusability
```agentscript
behavior EmailValidator {
    validate email matches email_pattern
}
```
Generates reusable Python classes that can be imported and composed.

### 4. Resource Management
```agentscript
resource database {
    type: postgresql
    connection: env.DATABASE_URL
}
```
Creates proper connection management with context managers and connection pooling.

## Error Handling Strategy

1. **Parse Errors**: Clear error messages with line numbers and suggestions
2. **Semantic Errors**: Type mismatches, undefined behaviors, resource issues
3. **Runtime Errors**: Generate Python code with proper exception handling
4. **Agent-Friendly Errors**: Errors formatted for AI agents to understand and fix

## Extensibility

The architecture supports:
- Custom behavior plugins
- New data source/sink types
- Agent-specific optimizations
- IDE integration hooks
- Debug information preservation