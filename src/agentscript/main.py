#!/usr/bin/env python3
"""
AgentScript Compiler

Command-line interface for compiling AgentScript to Python.
"""

import argparse
import sys
from pathlib import Path

from .parser import parse_agentscript
from .codegen import generate_python_code
from .lexer import LexerError
from .parser import ParseError
from .error_reporter import create_error_report


def compile_file(input_file: Path, output_file: Path = None):
    """Compile a single AgentScript file to Python."""
    try:
        # Read input file
        source_code = input_file.read_text(encoding='utf-8')
        
        # Parse AgentScript to AST
        print(f"Parsing {input_file}...")
        ast = parse_agentscript(source_code, str(input_file))
        
        # Generate Python code
        print("Generating Python code...")
        python_code = generate_python_code(ast)
        
        # Determine output file
        if output_file is None:
            output_file = input_file.with_suffix('.py')
        
        # Write output file
        output_file.write_text(python_code, encoding='utf-8')
        print(f"✓ Compiled to {output_file}")
        
    except LexerError as e:
        error_report = create_error_report(e, source_code, str(input_file))
        print(error_report, file=sys.stderr)
        return 1
    except ParseError as e:
        error_report = create_error_report(e, source_code, str(input_file))
        print(error_report, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AgentScript Compiler - Convert AgentScript to Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agentscript compile data_processor.ags
  agentscript compile input.ags -o output.py
  agentscript compile *.ags
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile AgentScript files')
    compile_parser.add_argument('files', nargs='+', type=Path,
                               help='AgentScript files to compile')
    compile_parser.add_argument('-o', '--output', type=Path,
                               help='Output file (only for single input file)')
    compile_parser.add_argument('--check', action='store_true',
                               help='Check syntax without generating output')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if args.command == 'version':
        print("AgentScript Compiler v0.1.0")
        return 0
    
    elif args.command == 'compile':
        if len(args.files) > 1 and args.output:
            print("Error: Cannot specify output file for multiple inputs", file=sys.stderr)
            return 1
        
        exit_code = 0
        for file_path in args.files:
            if not file_path.exists():
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                exit_code = 1
                continue
            
            if not file_path.suffix == '.ags':
                print(f"Warning: {file_path} doesn't have .ags extension", file=sys.stderr)
            
            result = compile_file(file_path, args.output)
            if result != 0:
                exit_code = result
        
        return exit_code
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())