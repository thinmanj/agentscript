"""
AgentScript Lexer (Tokenizer)

Converts AgentScript source code into tokens for parsing.
Supports both symbolic operators and natural language constructs.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    # Literals
    STRING = "STRING"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    
    # Identifiers and Keywords
    IDENTIFIER = "IDENTIFIER"
    INTENT = "intent"
    BEHAVIOR = "behavior"
    USE = "use"
    RESOURCE = "resource"
    PIPELINE = "pipeline"
    DESCRIPTION = "description"
    EXPECTS = "expects"
    RETURNS = "returns"
    VALIDATE = "validate"
    TRANSFORM = "transform"
    FILTER = "filter"
    SOURCE = "source"
    SINK = "sink"
    ON_ERROR = "on_error"
    
    # Operators
    ARROW = "->"
    LAMBDA_ARROW = "=>"
    ASSIGN = ":"
    COMMA = ","
    DOT = "."
    
    # Comparison operators
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    
    # Logical operators
    AND = "and"
    OR = "or"
    NOT = "not"
    IN = "in"
    MATCHES = "matches"
    CONTAINS = "contains"
    BETWEEN = "between"
    IS = "is"
    
    # Arithmetic operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    
    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    COMMENT = "COMMENT"


@dataclass
class Token:
    """Represents a single token in the source code."""
    type: TokenType
    value: str
    line: int
    column: int
    filename: Optional[str] = None


class LexerError(Exception):
    """Raised when the lexer encounters invalid syntax."""
    def __init__(self, message: str, line: int, column: int, filename: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(f"{filename or '<unknown>'}:{line}:{column}: {message}")


class Lexer:
    """Tokenizes AgentScript source code."""
    
    # Keywords that should be recognized as special tokens
    KEYWORDS = {
        'intent': TokenType.INTENT,
        'behavior': TokenType.BEHAVIOR,
        'use': TokenType.USE,
        'resource': TokenType.RESOURCE,
        'pipeline': TokenType.PIPELINE,
        'description': TokenType.DESCRIPTION,
        'expects': TokenType.EXPECTS,
        'returns': TokenType.RETURNS,
        'validate': TokenType.VALIDATE,
        'transform': TokenType.TRANSFORM,
        'on_error': TokenType.ON_ERROR,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'in': TokenType.IN,
        'matches': TokenType.MATCHES,
        'contains': TokenType.CONTAINS,
        'between': TokenType.BETWEEN,
        'is': TokenType.IS,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
    }
    
    def __init__(self, source: str, filename: Optional[str] = None):
        self.source = source
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.position < len(self.source):
            self._skip_whitespace()
            
            if self.position >= len(self.source):
                break
                
            if self._match_comment():
                continue
            elif self._match_string():
                continue
            elif self._match_number():
                continue
            elif self._match_arrow():
                continue
            elif self._match_comparison_operators():
                continue
            elif self._match_single_char_tokens():
                continue
            elif self._match_identifier_or_keyword():
                continue
            else:
                raise LexerError(
                    f"Unexpected character: '{self._current_char()}'",
                    self.line, self.column, self.filename
                )
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column, self.filename))
        return self.tokens
    
    def _current_char(self) -> str:
        """Get the current character."""
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]
    
    def _peek_char(self, offset: int = 1) -> str:
        """Peek at a character ahead."""
        pos = self.position + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def _advance(self) -> str:
        """Advance to the next character."""
        if self.position < len(self.source):
            char = self.source[self.position]
            self.position += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return '\0'
    
    def _skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self._current_char() in ' \t\r':
            self._advance()
    
    def _match_comment(self) -> bool:
        """Match and skip comments."""
        if self._current_char() == '/' and self._peek_char() == '/':
            start_column = self.column
            comment_text = ""
            self._advance()  # Skip first /
            self._advance()  # Skip second /
            
            while self._current_char() != '\n' and self._current_char() != '\0':
                comment_text += self._advance()
            
            self.tokens.append(Token(
                TokenType.COMMENT, comment_text.strip(),
                self.line, start_column, self.filename
            ))
            return True
        return False
    
    def _match_string(self) -> bool:
        """Match string literals."""
        if self._current_char() in ['"', "'"]:
            quote_char = self._current_char()
            start_column = self.column
            self._advance()  # Skip opening quote
            
            value = ""
            while self._current_char() != quote_char and self._current_char() != '\0':
                if self._current_char() == '\\':
                    self._advance()  # Skip backslash
                    escaped = self._advance()
                    # Handle common escape sequences
                    if escaped == 'n':
                        value += '\n'
                    elif escaped == 't':
                        value += '\t'
                    elif escaped == 'r':
                        value += '\r'
                    elif escaped == '\\':
                        value += '\\'
                    elif escaped in ['"', "'"]:
                        value += escaped
                    else:
                        value += escaped
                else:
                    value += self._advance()
            
            if self._current_char() == '\0':
                raise LexerError(
                    "Unterminated string literal",
                    self.line, start_column, self.filename
                )
            
            self._advance()  # Skip closing quote
            self.tokens.append(Token(
                TokenType.STRING, value,
                self.line, start_column, self.filename
            ))
            return True
        return False
    
    def _match_number(self) -> bool:
        """Match integer and float literals."""
        if self._current_char().isdigit():
            start_column = self.column
            value = ""
            is_float = False
            
            while self._current_char().isdigit():
                value += self._advance()
            
            if self._current_char() == '.' and self._peek_char().isdigit():
                is_float = True
                value += self._advance()  # Add the dot
                while self._current_char().isdigit():
                    value += self._advance()
            
            token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
            self.tokens.append(Token(
                token_type, value,
                self.line, start_column, self.filename
            ))
            return True
        return False
    
    def _match_arrow(self) -> bool:
        """Match arrow operators."""
        if self._current_char() == '-' and self._peek_char() == '>':
            start_column = self.column
            self._advance()
            self._advance()
            self.tokens.append(Token(
                TokenType.ARROW, "->",
                self.line, start_column, self.filename
            ))
            return True
        elif self._current_char() == '=' and self._peek_char() == '>':
            start_column = self.column
            self._advance()
            self._advance()
            self.tokens.append(Token(
                TokenType.LAMBDA_ARROW, "=>",
                self.line, start_column, self.filename
            ))
            return True
        return False
    
    def _match_comparison_operators(self) -> bool:
        """Match comparison and other multi-character operators."""
        current = self._current_char()
        next_char = self._peek_char()
        start_column = self.column
        
        if current == '=' and next_char == '=':
            self._advance()
            self._advance()
            self.tokens.append(Token(TokenType.EQ, "==", self.line, start_column, self.filename))
            return True
        elif current == '!' and next_char == '=':
            self._advance()
            self._advance()
            self.tokens.append(Token(TokenType.NE, "!=", self.line, start_column, self.filename))
            return True
        elif current == '<' and next_char == '=':
            self._advance()
            self._advance()
            self.tokens.append(Token(TokenType.LE, "<=", self.line, start_column, self.filename))
            return True
        elif current == '>' and next_char == '=':
            self._advance()
            self._advance()
            self.tokens.append(Token(TokenType.GE, ">=", self.line, start_column, self.filename))
            return True
        
        return False
    
    def _match_single_char_tokens(self) -> bool:
        """Match single character tokens."""
        char = self._current_char()
        start_column = self.column
        
        single_char_map = {
            ':': TokenType.ASSIGN,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '\n': TokenType.NEWLINE,
        }
        
        if char in single_char_map:
            self._advance()
            self.tokens.append(Token(
                single_char_map[char], char,
                self.line, start_column, self.filename
            ))
            return True
        
        return False
    
    def _match_identifier_or_keyword(self) -> bool:
        """Match identifiers and keywords."""
        if self._current_char().isalpha() or self._current_char() == '_':
            start_column = self.column
            value = ""
            
            while (self._current_char().isalnum() or 
                   self._current_char() == '_'):
                value += self._advance()
            
            # Check if it's a keyword
            token_type = self.KEYWORDS.get(value, TokenType.IDENTIFIER)
            
            # Special handling for boolean literals
            if value in ['true', 'false']:
                self.tokens.append(Token(
                    TokenType.BOOLEAN, value,
                    self.line, start_column, self.filename
                ))
            else:
                self.tokens.append(Token(
                    token_type, value,
                    self.line, start_column, self.filename
                ))
            return True
        return False