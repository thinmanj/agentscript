"""
AgentScript Abstract Syntax Tree (AST) Node Definitions

This module defines all the AST node types used by the AgentScript parser.
Each node represents a different construct in the AgentScript language.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod


@dataclass
class Position:
    """Source code position information for error reporting."""
    line: int
    column: int
    filename: Optional[str] = None


@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes."""
    position: Position
    
    @abstractmethod
    def accept(self, visitor):
        """Accept a visitor for the visitor pattern."""
        pass


@dataclass
class Expression(ASTNode):
    """Base class for all expressions."""
    pass


@dataclass
class Statement(ASTNode):
    """Base class for all statements."""
    pass


@dataclass
class Identifier(Expression):
    """Represents an identifier (variable name, function name, etc.)."""
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)


@dataclass
class Literal(Expression):
    """Represents literal values (strings, numbers, booleans)."""
    value: Union[str, int, float, bool]
    type_hint: Optional[str] = None
    
    def accept(self, visitor):
        return visitor.visit_literal(self)


@dataclass
class ImportStatement(Statement):
    """Represents import statements like 'use io.csv, validation.email'."""
    modules: List[str]
    
    def accept(self, visitor):
        return visitor.visit_import(self)


@dataclass
class IntentDeclaration(Statement):
    """Represents an intent block - the main construct of AgentScript."""
    name: str
    description: Optional[str]
    pipeline: Optional['PipelineExpression']
    error_handling: Optional[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]
    
    def accept(self, visitor):
        return visitor.visit_intent_declaration(self)


@dataclass
class BehaviorDeclaration(Statement):
    """Represents a custom behavior definition."""
    name: str
    expects: Optional[str]  # Input type
    returns: Optional[str]  # Return type
    description: Optional[str]
    rules: List['ValidationRule']
    
    def accept(self, visitor):
        return visitor.visit_behavior_declaration(self)


@dataclass
class ValidationRule(ASTNode):
    """Represents a validation rule within a behavior."""
    condition: Expression
    message: Optional[str]
    
    def accept(self, visitor):
        return visitor.visit_validation_rule(self)


@dataclass
class PipelineExpression(Expression):
    """Represents a data processing pipeline with -> operators."""
    stages: List['PipelineStage']
    
    def accept(self, visitor):
        return visitor.visit_pipeline_expression(self)


@dataclass
class PipelineStage(ASTNode):
    """Represents a single stage in a pipeline."""
    operation: Expression
    
    def accept(self, visitor):
        return visitor.visit_pipeline_stage(self)


@dataclass
class FunctionCall(Expression):
    """Represents a function call with arguments."""
    function: Expression
    arguments: List[Expression]
    keyword_arguments: Dict[str, Expression]
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)


@dataclass
class LambdaExpression(Expression):
    """Represents a lambda expression like 'user => user.age > 18'."""
    parameter: str
    body: Expression
    
    def accept(self, visitor):
        return visitor.visit_lambda_expression(self)


@dataclass
class BinaryOperation(Expression):
    """Represents binary operations like comparisons and arithmetic."""
    left: Expression
    operator: str
    right: Expression
    
    def accept(self, visitor):
        return visitor.visit_binary_operation(self)


@dataclass
class UnaryOperation(Expression):
    """Represents unary operations like 'not', '-', etc."""
    operator: str
    operand: Expression
    
    def accept(self, visitor):
        return visitor.visit_unary_operation(self)


@dataclass
class AttributeAccess(Expression):
    """Represents attribute access like 'user.age'."""
    object: Expression
    attribute: str
    
    def accept(self, visitor):
        return visitor.visit_attribute_access(self)


@dataclass
class ObjectLiteral(Expression):
    """Represents object literals like '{ name: "John", age: 30 }'."""
    fields: Dict[str, Expression]
    
    def accept(self, visitor):
        return visitor.visit_object_literal(self)


@dataclass
class ArrayLiteral(Expression):
    """Represents array literals like '[1, 2, 3]'."""
    elements: List[Expression]
    
    def accept(self, visitor):
        return visitor.visit_array_literal(self)


@dataclass
class ResourceDeclaration(Statement):
    """Represents a resource declaration for databases, APIs, etc."""
    name: str
    resource_type: str
    configuration: Dict[str, Any]
    
    def accept(self, visitor):
        return visitor.visit_resource_declaration(self)


@dataclass
class Program(ASTNode):
    """Represents the root of the AST - the entire program."""
    statements: List[Statement]
    
    def accept(self, visitor):
        return visitor.visit_program(self)


class ASTVisitor(ABC):
    """Abstract base class for AST visitors."""
    
    @abstractmethod
    def visit_program(self, node: Program): pass
    
    @abstractmethod
    def visit_import(self, node: ImportStatement): pass
    
    @abstractmethod
    def visit_intent_declaration(self, node: IntentDeclaration): pass
    
    @abstractmethod
    def visit_behavior_declaration(self, node: BehaviorDeclaration): pass
    
    @abstractmethod
    def visit_validation_rule(self, node: ValidationRule): pass
    
    @abstractmethod
    def visit_pipeline_expression(self, node: PipelineExpression): pass
    
    @abstractmethod
    def visit_pipeline_stage(self, node: PipelineStage): pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall): pass
    
    @abstractmethod
    def visit_lambda_expression(self, node: LambdaExpression): pass
    
    @abstractmethod
    def visit_binary_operation(self, node: BinaryOperation): pass
    
    @abstractmethod
    def visit_unary_operation(self, node: UnaryOperation): pass
    
    @abstractmethod
    def visit_attribute_access(self, node: AttributeAccess): pass
    
    @abstractmethod
    def visit_object_literal(self, node: ObjectLiteral): pass
    
    @abstractmethod
    def visit_array_literal(self, node: ArrayLiteral): pass
    
    @abstractmethod
    def visit_resource_declaration(self, node: ResourceDeclaration): pass
    
    @abstractmethod
    def visit_identifier(self, node: Identifier): pass
    
    @abstractmethod
    def visit_literal(self, node: Literal): pass