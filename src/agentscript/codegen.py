"""
AgentScript Code Generator

Converts AgentScript AST to clean, readable Python code.
Maintains good coding practices and generates well-documented output.
"""

import textwrap
from typing import Dict, List, Set
from .ast_nodes import *


class PythonCodeGenerator(ASTVisitor):
    """Generates Python code from AgentScript AST."""
    
    def __init__(self, source_filename: str = None):
        self.imports: Set[str] = set()
        self.classes: List[str] = []
        self.current_indent = 0
        self.indent_size = 4
        self.source_filename = source_filename
        self.line_mappings: Dict[int, int] = {}  # Python line -> AgentScript line
    
    def generate(self, program: Program) -> str:
        """Generate complete Python code from the program AST."""
        self.imports.clear()
        self.classes.clear()
        self.current_indent = 0
        
        # Visit the program to collect imports and generate classes
        program.accept(self)
        
        # Build the final Python code
        result = []
        
        # Add file header with generation info
        result.extend(self._generate_file_header(program))
        result.append("")
        
        # Add imports with documentation
        if self.imports:
            result.append("# Required imports for data processing")
            result.extend(sorted(self.imports))
            result.append("")  # Empty line after imports
        
        # Add generated classes
        result.extend(self.classes)
        
        return "\n".join(result)
    
    def _indent(self, text: str) -> str:
        """Apply current indentation to text."""
        if not text.strip():
            return text
        
        indent = " " * (self.current_indent * self.indent_size)
        lines = text.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    
    def _increase_indent(self):
        """Increase indentation level."""
        self.current_indent += 1
    
    def _decrease_indent(self):
        """Decrease indentation level."""
        self.current_indent = max(0, self.current_indent - 1)
    
    def _generate_file_header(self, program: Program) -> List[str]:
        """Generate header comment with generation and debugging info."""
        lines = [
            "# This file was automatically generated from AgentScript",
            f"# Source: {self.source_filename or 'unknown'}",
            f"# Generated at: {self._get_timestamp()}",
            "#",
            "# AgentScript is a declarative language for agentic program creation.",
            "# The generated code follows a specific structure to maintain clarity:",
            "#",
            "# - Each AgentScript 'intent' becomes a Python class",
            "# - Pipeline operations are converted to sequential pandas operations",
            "# - Error handling is built-in with validation_errors tracking",
            "# - Methods are well-documented with their original intent descriptions",
            "#",
            "# For debugging: Line numbers in comments refer to the original .ags file"
        ]
        return lines
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for file header."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _add_source_comment(self, ags_line: int) -> str:
        """Add source line reference for debugging."""
        if ags_line and self.source_filename:
            return f"  # Source: {self.source_filename}:{ags_line}"
        return ""
    
    def visit_program(self, node: Program) -> str:
        """Visit the root program node."""
        for stmt in node.statements:
            stmt.accept(self)
        return ""
    
    def visit_import(self, node: ImportStatement) -> str:
        """Convert import statements to Python imports."""
        for module in node.modules:
            if module.startswith("io."):
                if "csv" in module:
                    self.imports.add("import pandas as pd")
                    self.imports.add("import csv")
                if "json" in module:
                    self.imports.add("import json")
            elif module.startswith("validation."):
                self.imports.add("import re")
            elif module.startswith("transformation."):
                pass  # Built-in transformations
        return ""
    
    def visit_intent_declaration(self, node: IntentDeclaration) -> str:
        """Convert intent declarations to Python classes."""
        class_name = self._to_camel_case(node.name)
        
        class_lines = []
        
        # Add class header with source location
        source_comment = self._add_source_comment(node.position.line)
        class_lines.append(f"class {class_name}:{source_comment}")
        
        # Add comprehensive docstring
        self._increase_indent()
        docstring_lines = []
        docstring_lines.append('"""')
        if node.description:
            docstring_lines.append(f"    {node.description}")
            docstring_lines.append("")
        
        docstring_lines.extend([
            "    This class was generated from an AgentScript 'intent' declaration.",
            "    An intent represents a high-level data processing goal that gets",
            "    transpiled into a sequence of pandas operations.",
            "",
            "    Structure:",
            "    - __init__: Initializes error tracking and validation patterns",
            f"    - {self._to_snake_case(node.name)}: Main processing method implementing the pipeline",
            "    - Helper methods: Utility functions for validation and transformation",
            "",
            "    The validation_errors list collects any data validation issues",
            "    encountered during processing for debugging and quality assurance.",
            '    """'
        ])
        
        class_lines.extend([self._indent(line) for line in docstring_lines])
        class_lines.append("")
        
        # Generate __init__ method with documentation
        class_lines.append(self._indent("def __init__(self):"))
        self._increase_indent()
        class_lines.append(self._indent('"""Initialize the data processor with error tracking and validation patterns."""'))
        class_lines.append(self._indent("# Track validation errors during processing for debugging"))
        class_lines.append(self._indent("self.validation_errors = []"))
        
        if "re" in str(self.imports):
            class_lines.append(self._indent("# Email validation pattern for data quality checks"))
            class_lines.append(self._indent("self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')"))
        
        self._decrease_indent()
        class_lines.append("")
        
        # Generate main method from pipeline
        if node.pipeline:
            method_name = self._to_snake_case(node.name)
            method_code = self._generate_pipeline_method(node.pipeline, method_name, node.description, node.position.line)
            class_lines.append(self._indent(method_code))
        
        # Generate helper methods
        helper_methods = self._generate_helper_methods()
        if helper_methods:
            class_lines.append("")
            class_lines.extend([self._indent(method) for method in helper_methods])
        
        self._decrease_indent()
        
        self.classes.extend(class_lines)
        self.classes.append("")  # Empty line between classes
        
        return ""
    
    def visit_behavior_declaration(self, node: BehaviorDeclaration) -> str:
        """Convert behavior declarations to Python classes."""
        # TODO: Implement behavior generation
        return ""
    
    def visit_resource_declaration(self, node: ResourceDeclaration) -> str:
        """Convert resource declarations to Python connection managers."""
        # TODO: Implement resource generation
        return ""
    
    def visit_pipeline_expression(self, node: PipelineExpression) -> str:
        """Convert pipeline expressions to Python method chains."""
        stages = []
        
        for i, stage in enumerate(node.stages):
            stage_code = stage.accept(self)
            if i == 0:
                stages.append(stage_code)
            else:
                # Add proper method chaining
                stages.append(f".pipe({stage_code})")
        
        return "\n".join(stages)
    
    def visit_pipeline_stage(self, node: PipelineStage) -> str:
        """Convert individual pipeline stages."""
        return node.operation.accept(self)
    
    def visit_function_call(self, node: FunctionCall) -> str:
        """Convert function calls to Python."""
        # Handle special pipeline functions first
        if isinstance(node.function, AttributeAccess):
            if node.function.attribute == "csv" and isinstance(node.function.object, Identifier):
                if node.function.object.name == "source":
                    # source.csv("file.csv") -> pd.read_csv("file.csv")
                    filename = node.arguments[0].accept(self) if node.arguments else '""'
                    return f"pd.read_csv({filename})"
                elif node.function.object.name == "sink":
                    # sink.csv("file.csv") -> to_csv("file.csv")
                    filename = node.arguments[0].accept(self) if node.arguments else '""'
                    return f"to_csv({filename}, index=False)"
            
            elif node.function.attribute == "json" and isinstance(node.function.object, Identifier):
                if node.function.object.name == "source":
                    # source.json("file.json") -> pd.read_json("file.json")
                    filename = node.arguments[0].accept(self) if node.arguments else '""'
                    return f"pd.read_json({filename})"
                elif node.function.object.name == "sink":
                    # sink.json("file.json") -> to_json("file.json")
                    filename = node.arguments[0].accept(self) if node.arguments else '""'
                    return f"to_json({filename}, orient='records', indent=2)"
        
        # Handle regular function calls
        func_code = node.function.accept(self)
        args = []
        for arg in node.arguments:
            args.append(arg.accept(self))
        
        args_str = ", ".join(args)
        return f"{func_code}({args_str})"
    
    def visit_lambda_expression(self, node: LambdaExpression) -> str:
        """Convert lambda expressions to Python lambdas."""
        param = node.parameter
        body = node.body.accept(self)
        return f"lambda {param}: {body}"
    
    def visit_binary_operation(self, node: BinaryOperation) -> str:
        """Convert binary operations."""
        left = node.left.accept(self)
        right = node.right.accept(self)
        
        # Map AgentScript operators to Python
        op_map = {
            "and": "and",
            "or": "or",
            "==": "==",
            "!=": "!=",
            "<": "<",
            "<=": "<=",
            ">": ">",
            ">=": ">=",
            "+": "+",
            "-": "-",
            "*": "*",
            "/": "/",
            "%": "%"
        }
        
        op = op_map.get(node.operator, node.operator)
        return f"{left} {op} {right}"
    
    def visit_unary_operation(self, node: UnaryOperation) -> str:
        """Convert unary operations."""
        operand = node.operand.accept(self)
        
        op_map = {
            "not": "not",
            "-": "-"
        }
        
        op = op_map.get(node.operator, node.operator)
        return f"{op} {operand}"
    
    def visit_attribute_access(self, node: AttributeAccess) -> str:
        """Convert attribute access."""
        obj = node.object.accept(self)
        return f"{obj}.{node.attribute}"
    
    def visit_object_literal(self, node: ObjectLiteral) -> str:
        """Convert object literals to Python dictionaries."""
        fields = []
        for key, value in node.fields.items():
            value_code = value.accept(self)
            fields.append(f"'{key}': {value_code}")
        
        return "{" + ", ".join(fields) + "}"
    
    def visit_array_literal(self, node: ArrayLiteral) -> str:
        """Convert array literals to Python lists."""
        elements = [elem.accept(self) for elem in node.elements]
        return "[" + ", ".join(elements) + "]"
    
    def visit_identifier(self, node: Identifier) -> str:
        """Convert identifiers."""
        # Handle special AgentScript identifiers
        if node.name == "filter":
            return "query"  # Pandas filter equivalent
        elif node.name == "transform":
            return "apply"  # Pandas transform equivalent
        
        return node.name
    
    def visit_literal(self, node: Literal) -> str:
        """Convert literals to Python."""
        if isinstance(node.value, str):
            # Escape quotes in strings
            escaped = node.value.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(node.value, bool):
            return "True" if node.value else "False"
        else:
            return str(node.value)
    
    def visit_validation_rule(self, node: ValidationRule) -> str:
        """Convert validation rules."""
        # TODO: Implement validation rule generation
        return ""
    
    def _generate_pipeline_method(self, pipeline: PipelineExpression, method_name: str, description: Optional[str], source_line: int = None) -> str:
        """Generate a method from a pipeline expression."""
        lines = []
        
        # Method signature with source reference
        source_comment = self._add_source_comment(source_line)
        lines.append(f"def {method_name}(self, input_file: str = None, output_file: str = None):{source_comment}")
        
        # Enhanced method docstring
        docstring_lines = []
        docstring_lines.append('    """')
        if description:
            docstring_lines.append(f"    {description}")
            docstring_lines.append("")
        
        docstring_lines.extend([
            f"    This method implements the AgentScript pipeline from {self.source_filename or 'source'}.",
            "    The pipeline is executed as a series of pandas operations in sequence:",
            ""
        ])
        
        # Document each pipeline stage
        for i, stage in enumerate(pipeline.stages):
            stage_desc = self._describe_pipeline_stage(stage, i)
            docstring_lines.append(f"    {i + 1}. {stage_desc}")
        
        docstring_lines.extend([
            "",
            "    Args:",
            "        input_file (str, optional): Override default input file",
            "        output_file (str, optional): Override default output file",
            "",
            "    Returns:",
            "        pd.DataFrame: The processed dataset",
            "",
            "    Raises:",
            "        Exception: Re-raises any processing errors after logging to validation_errors",
            '    """'
        ])
        
        lines.extend(docstring_lines)
        lines.append("")
        
        # Method body - convert pipeline to sequential operations
        lines.append("    # Execute AgentScript pipeline as sequential pandas operations")
        lines.append("    try:")
        
        # Generate code for each pipeline stage with documentation
        for i, stage in enumerate(pipeline.stages):
            stage_code = stage.accept(self)
            stage_source_line = getattr(stage, 'position', None)
            stage_line_comment = self._add_source_comment(stage_source_line.line if stage_source_line else None)
            
            if i == 0:
                # First stage - usually data loading
                lines.append(f"        # Stage {i + 1}: Data input{stage_line_comment}")
                lines.append(f"        df = {stage_code}")
            else:
                # Subsequent stages - transformations
                if "filter" in stage_code or "query" in stage_code:
                    # Handle filtering
                    lines.append(f"        # Stage {i + 1}: Data filtering{stage_line_comment}")
                    if isinstance(stage.operation, FunctionCall) and stage.operation.arguments:
                        if isinstance(stage.operation.arguments[0], LambdaExpression):
                            lambda_expr = stage.operation.arguments[0]
                            condition = lambda_expr.body.accept(self)
                            # Convert lambda condition to pandas query
                            condition = condition.replace(f"{lambda_expr.parameter}.", "")
                            lines.append(f"        df = df.query('{condition}')  # Filter: {lambda_expr.parameter} => {condition}")
                elif "apply" in stage_code or "transform" in stage_code:
                    # Handle transformations
                    lines.append(f"        # Stage {i + 1}: Data transformation{stage_line_comment}")
                    lines.append(f"        df = df.{stage_code}")
                elif "to_csv" in stage_code or "to_json" in stage_code:
                    # Handle output - these are terminal operations
                    lines.append(f"        # Stage {i + 1}: Data output{stage_line_comment}")
                    lines.append(f"        df.{stage_code}")
                else:
                    # Generic pipeline stage
                    lines.append(f"        # Stage {i + 1}: Custom operation{stage_line_comment}")
                    lines.append(f"        df = df.pipe(lambda x: {stage_code})")
            
            if i < len(pipeline.stages) - 1:
                lines.append("")  # Empty line between stages for readability
        
        lines.append("")
        lines.append("        # Pipeline execution completed successfully")
        lines.append("        return df")
        lines.append("")  
        lines.append("    except Exception as e:")
        lines.append("        # Log error for debugging while preserving original exception")
        lines.append("        error_info = {")
        lines.append("            'error': str(e),")
        lines.append("            'error_type': type(e).__name__,")
        lines.append(f"            'method': '{method_name}',")
        lines.append(f"            'source_file': '{self.source_filename or 'unknown'}'")
        lines.append("        }")
        lines.append("        self.validation_errors.append(error_info)")
        lines.append("        raise  # Re-raise for proper error handling")
        
        return "\n".join(lines)
    
    def _describe_pipeline_stage(self, stage: 'PipelineStage', index: int) -> str:
        """Generate human-readable description of a pipeline stage."""
        if isinstance(stage.operation, FunctionCall):
            if isinstance(stage.operation.function, AttributeAccess):
                obj_name = stage.operation.function.object.name if hasattr(stage.operation.function.object, 'name') else 'source'
                attr_name = stage.operation.function.attribute
                
                if obj_name == 'source':
                    return f"Load data from {attr_name.upper()} file"
                elif obj_name == 'sink':
                    return f"Save data to {attr_name.upper()} file"
            elif hasattr(stage.operation.function, 'name'):
                func_name = stage.operation.function.name
                if func_name == 'filter':
                    return "Filter data based on conditions"
                elif func_name == 'transform':
                    return "Transform data structure"
                else:
                    return f"Apply {func_name} operation"
        
        return "Custom data processing step"
    
    def _generate_helper_methods(self) -> List[str]:
        """Generate common helper methods with comprehensive documentation."""
        methods = []
        
        # Email validation method with enhanced documentation
        methods.append("""def is_valid_email(self, email: str) -> bool:
    \"\"\"Validate email format using regex pattern.
    
    This method provides email validation for data quality assurance.
    It uses a standard regex pattern that covers most common email formats.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
        
    Note:
        This validation is for format checking only and doesn't verify
        if the email address actually exists or is deliverable.
    \"\"\"
    if not email:
        return False
    return bool(self.email_pattern.match(email))""")
        
        return methods
    
    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to CamelCase."""
        components = name.split('_')
        return ''.join(word.capitalize() for word in components)
    
    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def generate_python_code(program: Program, source_filename: str = None) -> str:
    """Convenience function to generate Python code from an AST."""
    generator = PythonCodeGenerator(source_filename)
    return generator.generate(program)
