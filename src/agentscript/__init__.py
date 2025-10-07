"""
AgentScript - A declarative language for agentic program creation

AgentScript is designed to be an intuitive language for AI agents to generate
and understand, while transpiling to clean, readable Python code.
"""

__version__ = "0.1.0"

from .lexer import Lexer, Token, TokenType, LexerError
from .parser import Parser, ParseError, parse_agentscript
from .codegen import PythonCodeGenerator, generate_python_code
from .ast_nodes import *

__all__ = [
    'Lexer', 'Token', 'TokenType', 'LexerError',
    'Parser', 'ParseError', 'parse_agentscript',
    'PythonCodeGenerator', 'generate_python_code',
    'Program', 'IntentDeclaration', 'BehaviorDeclaration',
    'PipelineExpression', 'FunctionCall', 'LambdaExpression'
]