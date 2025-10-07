"""
AgentScript Error Reporter

Provides enhanced error reporting with context, suggestions, and agent-friendly messages.
"""

from typing import List, Optional
from dataclasses import dataclass
from .lexer import LexerError, Token
from .parser import ParseError


@dataclass
class ErrorContext:
    """Context information for an error."""
    line: int
    column: int
    filename: Optional[str]
    source_line: Optional[str] = None
    surrounding_lines: Optional[List[str]] = None


@dataclass 
class ErrorSuggestion:
    """A suggestion for fixing an error."""
    message: str
    fix: Optional[str] = None  # Suggested replacement text
    position: Optional[int] = None  # Character position for fix


class AgentScriptErrorReporter:
    """Enhanced error reporting for AgentScript compilation errors."""
    
    def __init__(self, source_code: str = None, filename: str = None):
        self.source_code = source_code
        self.filename = filename
        self.source_lines = source_code.splitlines() if source_code else []
    
    def report_lexer_error(self, error: LexerError) -> str:
        """Generate a comprehensive lexer error report."""
        context = self._get_error_context(error.line, error.column)
        suggestions = self._get_lexer_suggestions(error)
        
        return self._format_error_report(
            error_type="Lexer Error",
            message=error.message,
            context=context,
            suggestions=suggestions
        )
    
    def report_parser_error(self, error: ParseError) -> str:
        """Generate a comprehensive parser error report."""
        context = self._get_error_context(error.token.line, error.token.column)
        suggestions = self._get_parser_suggestions(error)
        
        return self._format_error_report(
            error_type="Parse Error",
            message=error.message,
            context=context,
            suggestions=suggestions
        )
    
    def _get_error_context(self, line: int, column: int) -> ErrorContext:
        """Extract context around the error location."""
        source_line = None
        surrounding_lines = []
        
        if self.source_lines and 1 <= line <= len(self.source_lines):
            source_line = self.source_lines[line - 1]
            
            # Get surrounding lines for context
            start = max(0, line - 3)
            end = min(len(self.source_lines), line + 2)
            surrounding_lines = self.source_lines[start:end]
        
        return ErrorContext(
            line=line,
            column=column,
            filename=self.filename,
            source_line=source_line,
            surrounding_lines=surrounding_lines
        )
    
    def _get_lexer_suggestions(self, error: LexerError) -> List[ErrorSuggestion]:
        """Generate suggestions for lexer errors."""
        suggestions = []
        
        if "Unexpected character" in error.message:
            char = error.message.split("'")[-2] if "'" in error.message else ""
            if char == "{":
                suggestions.append(ErrorSuggestion(
                    "Did you forget to close a string with quotes before this brace?",
                    fix='Add missing quote (") before {'
                ))
            elif char in "!@#$%^&":
                suggestions.append(ErrorSuggestion(
                    f"Character '{char}' is not valid in AgentScript. Use alphanumeric characters and underscores for identifiers."
                ))
        
        elif "Unterminated string" in error.message:
            suggestions.append(ErrorSuggestion(
                "Add a closing quote to complete the string literal",
                fix='Add closing quote (")'
            ))
        
        return suggestions
    
    def _get_parser_suggestions(self, error: ParseError) -> List[ErrorSuggestion]:
        """Generate suggestions for parser errors."""
        suggestions = []
        
        if "Expected" in error.message:
            expected = error.message.split("Expected ")[-1]
            if "identifier" in expected.lower():
                suggestions.append(ErrorSuggestion(
                    "Use a valid identifier (letters, numbers, underscores, starting with letter or underscore)"
                ))
            elif "'{'" in expected:
                suggestions.append(ErrorSuggestion(
                    "Add an opening brace '{' to start the block"
                ))
            elif "'}'" in expected:
                suggestions.append(ErrorSuggestion(
                    "Add a closing brace '}' to end the block"
                ))
        
        elif "Unexpected token" in error.message:
            token_value = error.token.value
            
            # Common AgentScript mistakes
            if token_value == "def":
                suggestions.append(ErrorSuggestion(
                    "AgentScript uses 'intent' instead of 'def' to define processing logic",
                    fix="intent"
                ))
            elif token_value == "import":
                suggestions.append(ErrorSuggestion(
                    "AgentScript uses 'use' instead of 'import'",
                    fix="use"
                ))
            elif token_value == "class":
                suggestions.append(ErrorSuggestion(
                    "AgentScript uses 'behavior' to define reusable components",
                    fix="behavior"
                ))
            elif token_value == "function":
                suggestions.append(ErrorSuggestion(
                    "AgentScript uses 'intent' for processing logic",
                    fix="intent"
                ))
            elif token_value == "=":
                suggestions.append(ErrorSuggestion(
                    "AgentScript uses ':' for assignment, not '='",
                    fix=":"
                ))
        
        return suggestions
    
    def _format_error_report(
        self, 
        error_type: str, 
        message: str, 
        context: ErrorContext,
        suggestions: List[ErrorSuggestion]
    ) -> str:
        """Format a comprehensive error report."""
        lines = []
        
        # Header
        location = f"{context.filename or '<unknown>'}:{context.line}:{context.column}"
        lines.append(f"🚨 {error_type} at {location}")
        lines.append(f"   {message}")
        lines.append("")
        
        # Source context
        if context.source_line is not None:
            lines.append("📍 Source Context:")
            
            if context.surrounding_lines:
                start_line = max(1, context.line - 2)
                for i, line in enumerate(context.surrounding_lines):
                    line_num = start_line + i
                    if line_num == context.line:
                        lines.append(f"  → {line_num:3d} | {line}")
                        # Add pointer to error location
                        pointer = " " * (8 + context.column) + "^"
                        lines.append(f"      | {pointer}")
                    else:
                        lines.append(f"    {line_num:3d} | {line}")
            else:
                lines.append(f"  → {context.line:3d} | {context.source_line}")
                pointer = " " * (8 + context.column) + "^"
                lines.append(f"      | {pointer}")
            
            lines.append("")
        
        # Suggestions
        if suggestions:
            lines.append("💡 Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"  {i}. {suggestion.message}")
                if suggestion.fix:
                    lines.append(f"     Fix: {suggestion.fix}")
            lines.append("")
        
        # Agent-friendly explanation
        lines.append("🤖 For AI Agents:")
        lines.append("   This error indicates a syntax issue in the AgentScript code.")
        lines.append("   Review the language syntax documentation and apply the suggested fixes.")
        lines.append("   Common patterns: intent { pipeline: source -> filter -> sink }")
        
        return "\n".join(lines)


def create_error_report(error: Exception, source_code: str = None, filename: str = None) -> str:
    """Convenience function to create error reports."""
    reporter = AgentScriptErrorReporter(source_code, filename)
    
    if isinstance(error, LexerError):
        return reporter.report_lexer_error(error)
    elif isinstance(error, ParseError):
        return reporter.report_parser_error(error)
    else:
        return f"❌ Unknown Error: {str(error)}"