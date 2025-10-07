"""
AgentScript Parser

Converts tokens into an Abstract Syntax Tree (AST).
Uses recursive descent parsing for clarity and maintainability.
"""

from typing import List, Optional, Dict, Any
from .lexer import Token, TokenType, Lexer
from .ast_nodes import *


class ParseError(Exception):
    """Raised when the parser encounters invalid syntax."""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{token.filename or '<unknown>'}:{token.line}:{token.column}: {message}")


class Parser:
    """Parses AgentScript tokens into an AST."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
    
    def parse(self) -> Program:
        """Parse tokens into a Program AST node."""
        statements = []
        
        while not self._is_at_end():
            # Skip newlines and comments at the top level
            if self._current_token().type in [TokenType.NEWLINE, TokenType.COMMENT]:
                self._advance()
                continue
                
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(
            statements=statements,
            position=Position(1, 1, self.tokens[0].filename if self.tokens else None)
        )
    
    def _current_token(self) -> Token:
        """Get the current token."""
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.position]
    
    def _peek_token(self, offset: int = 1) -> Token:
        """Peek at a token ahead."""
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[pos]
    
    def _advance(self) -> Token:
        """Advance to the next token."""
        if not self._is_at_end():
            self.position += 1
        return self.tokens[self.position - 1]
    
    def _is_at_end(self) -> bool:
        """Check if we're at the end of tokens."""
        return self._current_token().type == TokenType.EOF
    
    def _match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return self._current_token().type in types
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of the given type or raise an error."""
        if self._current_token().type == token_type:
            return self._advance()
        
        raise ParseError(message, self._current_token())
    
    def _skip_newlines(self):
        """Skip newline tokens."""
        while self._match(TokenType.NEWLINE):
            self._advance()
    
    def _parse_statement(self) -> Optional[Statement]:
        """Parse a statement."""
        self._skip_newlines()
        
        if self._match(TokenType.USE):
            return self._parse_import()
        elif self._match(TokenType.INTENT):
            return self._parse_intent_declaration()
        elif self._match(TokenType.BEHAVIOR):
            return self._parse_behavior_declaration()
        elif self._match(TokenType.RESOURCE):
            return self._parse_resource_declaration()
        else:
            raise ParseError(
                f"Unexpected token: {self._current_token().value}",
                self._current_token()
            )
    
    def _parse_import(self) -> ImportStatement:
        """Parse import statements like 'use io.csv, validation.email'."""
        use_token = self._consume(TokenType.USE, "Expected 'use'")
        
        modules = []
        modules.append(self._parse_module_name())
        
        while self._match(TokenType.COMMA):
            self._advance()  # consume comma
            modules.append(self._parse_module_name())
        
        return ImportStatement(
            modules=modules,
            position=Position(use_token.line, use_token.column, use_token.filename)
        )
    
    def _parse_module_name(self) -> str:
        """Parse a dotted module name like 'io.csv'."""
        parts = []
        parts.append(self._consume(TokenType.IDENTIFIER, "Expected module name").value)
        
        while self._match(TokenType.DOT):
            self._advance()  # consume dot
            parts.append(self._consume(TokenType.IDENTIFIER, "Expected module name part").value)
        
        return ".".join(parts)
    
    def _parse_intent_declaration(self) -> IntentDeclaration:
        """Parse intent declarations."""
        intent_token = self._consume(TokenType.INTENT, "Expected 'intent'")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected intent name")
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        self._skip_newlines()
        
        description = None
        pipeline = None
        error_handling = {}
        parameters = {}
        
        while not self._match(TokenType.RBRACE):
            self._skip_newlines()
            
            if self._match(TokenType.DESCRIPTION):
                description = self._parse_description()
            elif self._match(TokenType.PIPELINE):
                pipeline = self._parse_pipeline_declaration()
            elif self._match(TokenType.ON_ERROR):
                error_handling = self._parse_error_handling()
            else:
                # Skip unknown fields for now
                self._advance()
            
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}'")
        
        return IntentDeclaration(
            name=name_token.value,
            description=description,
            pipeline=pipeline,
            error_handling=error_handling if error_handling else None,
            parameters=parameters if parameters else None,
            position=Position(intent_token.line, intent_token.column, intent_token.filename)
        )
    
    def _parse_description(self) -> str:
        """Parse description field."""
        self._consume(TokenType.DESCRIPTION, "Expected 'description'")
        self._consume(TokenType.ASSIGN, "Expected ':'")
        desc_token = self._consume(TokenType.STRING, "Expected string description")
        return desc_token.value
    
    def _parse_pipeline_declaration(self) -> PipelineExpression:
        """Parse pipeline declaration."""
        pipeline_token = self._consume(TokenType.PIPELINE, "Expected 'pipeline'")
        self._consume(TokenType.ASSIGN, "Expected ':'")
        self._skip_newlines()
        
        return self._parse_pipeline_expression()
    
    def _parse_pipeline_expression(self) -> PipelineExpression:
        """Parse a pipeline expression with -> operators."""
        stages = []
        
        # Parse first stage
        first_stage = PipelineStage(
            operation=self._parse_primary_expression(),
            position=Position(self._current_token().line, self._current_token().column, self._current_token().filename)
        )
        stages.append(first_stage)
        
        # Parse remaining stages connected by ->
        while self._match(TokenType.ARROW):
            self._advance()  # consume ->
            self._skip_newlines()
            
            stage = PipelineStage(
                operation=self._parse_primary_expression(),
                position=Position(self._current_token().line, self._current_token().column, self._current_token().filename)
            )
            stages.append(stage)
        
        return PipelineExpression(
            stages=stages,
            position=Position(stages[0].position.line, stages[0].position.column, stages[0].position.filename)
        )
    
    def _parse_primary_expression(self) -> Expression:
        """Parse primary expressions."""
        if self._match(TokenType.IDENTIFIER):
            return self._parse_identifier_or_call()
        elif self._match(TokenType.STRING):
            token = self._advance()
            return Literal(
                value=token.value,
                type_hint="string",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.INTEGER):
            token = self._advance()
            return Literal(
                value=int(token.value),
                type_hint="int",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.FLOAT):
            token = self._advance()
            return Literal(
                value=float(token.value),
                type_hint="float",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.BOOLEAN):
            token = self._advance()
            return Literal(
                value=token.value == "true",
                type_hint="bool",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.LBRACE):
            return self._parse_object_literal()
        elif self._match(TokenType.LBRACKET):
            return self._parse_array_literal()
        else:
            raise ParseError(
                f"Unexpected token in expression: {self._current_token().value}",
                self._current_token()
            )
    
    def _parse_identifier_or_call(self) -> Expression:
        """Parse identifier or function call."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected identifier")
        
        # Check for attribute access (e.g., source.csv)
        expr = Identifier(
            name=name_token.value,
            position=Position(name_token.line, name_token.column, name_token.filename)
        )
        
        while self._match(TokenType.DOT):
            self._advance()  # consume dot
            attr_token = self._consume(TokenType.IDENTIFIER, "Expected attribute name")
            expr = AttributeAccess(
                object=expr,
                attribute=attr_token.value,
                position=Position(attr_token.line, attr_token.column, attr_token.filename)
            )
        
        # Check for function call
        if self._match(TokenType.LPAREN):
            return self._parse_function_call(expr)
        
        return expr
    
    def _parse_function_call(self, function: Expression) -> FunctionCall:
        """Parse function call arguments."""
        self._consume(TokenType.LPAREN, "Expected '('")
        
        arguments = []
        keyword_arguments = {}
        
        if not self._match(TokenType.RPAREN):
            # Parse first argument
            arguments.append(self._parse_argument())
            
            # Parse remaining arguments
            while self._match(TokenType.COMMA):
                self._advance()  # consume comma
                if self._match(TokenType.RPAREN):  # Trailing comma
                    break
                arguments.append(self._parse_argument())
        
        self._consume(TokenType.RPAREN, "Expected ')'")
        
        return FunctionCall(
            function=function,
            arguments=arguments,
            keyword_arguments=keyword_arguments,
            position=function.position
        )
    
    def _parse_expression(self) -> Expression:
        """Parse expressions with operator precedence."""
        return self._parse_logical_or()
    
    def _parse_logical_or(self) -> Expression:
        """Parse logical OR expressions."""
        expr = self._parse_logical_and()
        
        while self._match(TokenType.OR):
            op_token = self._advance()
            right = self._parse_logical_and()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_logical_and(self) -> Expression:
        """Parse logical AND expressions."""
        expr = self._parse_equality()
        
        while self._match(TokenType.AND):
            op_token = self._advance()
            right = self._parse_equality()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_equality(self) -> Expression:
        """Parse equality expressions."""
        expr = self._parse_comparison()
        
        while self._match(TokenType.EQ, TokenType.NE):
            op_token = self._advance()
            right = self._parse_comparison()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_argument(self) -> Expression:
        """Parse a function argument, which might be a lambda expression."""
        # Check if this is a lambda expression
        if (self._match(TokenType.IDENTIFIER) and 
            self._peek_token().type == TokenType.LAMBDA_ARROW):
            param_token = self._advance()
            self._consume(TokenType.LAMBDA_ARROW, "Expected '=>'")
            body = self._parse_expression()
            return LambdaExpression(
                parameter=param_token.value,
                body=body,
                position=Position(param_token.line, param_token.column, param_token.filename)
            )
        else:
            return self._parse_expression()
    
    def _parse_primary_expression(self) -> Expression:
        """Parse primary expressions."""
        if self._match(TokenType.IDENTIFIER):
            return self._parse_identifier_or_call()
        elif self._match(TokenType.STRING):
            token = self._advance()
            return Literal(
                value=token.value,
                type_hint="string",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.INTEGER):
            token = self._advance()
            return Literal(
                value=int(token.value),
                type_hint="int",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.FLOAT):
            token = self._advance()
            return Literal(
                value=float(token.value),
                type_hint="float",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.BOOLEAN):
            token = self._advance()
            return Literal(
                value=token.value == "true",
                type_hint="bool",
                position=Position(token.line, token.column, token.filename)
            )
        elif self._match(TokenType.LBRACE):
            return self._parse_object_literal()
        elif self._match(TokenType.LBRACKET):
            return self._parse_array_literal()
        else:
            raise ParseError(
                f"Unexpected token in expression: {self._current_token().value}",
                self._current_token()
            )
    
    def _parse_identifier_or_call(self) -> Expression:
        """Parse identifier or function call."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected identifier")
        
        # Check for attribute access (e.g., source.csv)
        expr = Identifier(
            name=name_token.value,
            position=Position(name_token.line, name_token.column, name_token.filename)
        )
        
        while self._match(TokenType.DOT):
            self._advance()  # consume dot
            attr_token = self._consume(TokenType.IDENTIFIER, "Expected attribute name")
            expr = AttributeAccess(
                object=expr,
                attribute=attr_token.value,
                position=Position(attr_token.line, attr_token.column, attr_token.filename)
            )
        
        # Check for function call
        if self._match(TokenType.LPAREN):
            return self._parse_function_call(expr)
        
        return expr
    
    def _parse_comparison(self) -> Expression:
        """Parse comparison expressions."""
        expr = self._parse_term()
        
        while self._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op_token = self._advance()
            right = self._parse_term()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_term(self) -> Expression:
        """Parse arithmetic term expressions."""
        expr = self._parse_factor()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op_token = self._advance()
            right = self._parse_factor()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_factor(self) -> Expression:
        """Parse arithmetic factor expressions."""
        expr = self._parse_unary()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self._advance()
            right = self._parse_unary()
            expr = BinaryOperation(
                left=expr,
                operator=op_token.value,
                right=right,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return expr
    
    def _parse_unary(self) -> Expression:
        """Parse unary expressions."""
        if self._match(TokenType.NOT, TokenType.MINUS):
            op_token = self._advance()
            expr = self._parse_unary()
            return UnaryOperation(
                operator=op_token.value,
                operand=expr,
                position=Position(op_token.line, op_token.column, op_token.filename)
            )
        
        return self._parse_primary_expression()
    
    def _parse_object_literal(self) -> ObjectLiteral:
        """Parse object literals like { name: "John", age: 30 }."""
        brace_token = self._consume(TokenType.LBRACE, "Expected '{'")
        self._skip_newlines()
        
        fields = {}
        
        if not self._match(TokenType.RBRACE):
            # Parse first field
            key_token = self._consume(TokenType.IDENTIFIER, "Expected field name")
            self._consume(TokenType.ASSIGN, "Expected ':'")
            value = self._parse_expression()
            fields[key_token.value] = value
            
            # Parse remaining fields
            while self._match(TokenType.COMMA):
                self._advance()  # consume comma
                self._skip_newlines()
                
                if self._match(TokenType.RBRACE):  # Trailing comma
                    break
                
                key_token = self._consume(TokenType.IDENTIFIER, "Expected field name")
                self._consume(TokenType.ASSIGN, "Expected ':'")
                value = self._parse_expression()
                fields[key_token.value] = value
            
            self._skip_newlines()
        
        self._consume(TokenType.RBRACE, "Expected '}'")
        
        return ObjectLiteral(
            fields=fields,
            position=Position(brace_token.line, brace_token.column, brace_token.filename)
        )
    
    def _parse_array_literal(self) -> ArrayLiteral:
        """Parse array literals like [1, 2, 3]."""
        bracket_token = self._consume(TokenType.LBRACKET, "Expected '['")
        
        elements = []
        
        if not self._match(TokenType.RBRACKET):
            elements.append(self._parse_expression())
            
            while self._match(TokenType.COMMA):
                self._advance()  # consume comma
                if self._match(TokenType.RBRACKET):  # Trailing comma
                    break
                elements.append(self._parse_expression())
        
        self._consume(TokenType.RBRACKET, "Expected ']'")
        
        return ArrayLiteral(
            elements=elements,
            position=Position(bracket_token.line, bracket_token.column, bracket_token.filename)
        )
    
    def _parse_behavior_declaration(self) -> BehaviorDeclaration:
        """Parse behavior declarations."""
        behavior_token = self._consume(TokenType.BEHAVIOR, "Expected 'behavior'")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected behavior name")
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        # For now, return a simple behavior declaration
        # TODO: Parse the full behavior body
        self._skip_until_closing_brace()
        
        return BehaviorDeclaration(
            name=name_token.value,
            expects=None,
            returns=None,
            description=None,
            rules=[],
            position=Position(behavior_token.line, behavior_token.column, behavior_token.filename)
        )
    
    def _parse_resource_declaration(self) -> ResourceDeclaration:
        """Parse resource declarations."""
        resource_token = self._consume(TokenType.RESOURCE, "Expected 'resource'")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected resource name")
        self._consume(TokenType.LBRACE, "Expected '{'")
        
        # For now, return a simple resource declaration
        # TODO: Parse the full resource configuration
        self._skip_until_closing_brace()
        
        return ResourceDeclaration(
            name=name_token.value,
            resource_type="unknown",
            configuration={},
            position=Position(resource_token.line, resource_token.column, resource_token.filename)
        )
    
    def _parse_error_handling(self) -> Dict[str, Any]:
        """Parse error handling configuration."""
        self._consume(TokenType.ON_ERROR, "Expected 'on_error'")
        self._consume(TokenType.ASSIGN, "Expected ':'")
        
        # Simple error handling for now
        error_value = self._consume(TokenType.IDENTIFIER, "Expected error handling strategy")
        return {"strategy": error_value.value}
    
    def _skip_until_closing_brace(self):
        """Skip tokens until we find the closing brace."""
        brace_count = 1
        
        while brace_count > 0 and not self._is_at_end():
            if self._match(TokenType.LBRACE):
                brace_count += 1
            elif self._match(TokenType.RBRACE):
                brace_count -= 1
            
            self._advance()


def parse_agentscript(source: str, filename: Optional[str] = None) -> Program:
    """Convenience function to parse AgentScript source code."""
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()