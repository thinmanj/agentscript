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
        python_code = generate_python_code(ast, str(input_file))
        
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


def handle_ticket_commands(args):
    """Handle ticket integration commands."""
    try:
        from .ticket_integration import (
            create_tickets_from_agentscript_cli,
            generate_agentscript_from_ticket_cli,
            TicketIntegrationError
        )
    except ImportError as e:
        print(f"Error: Ticket integration not available: {e}", file=sys.stderr)
        return 1
    
    try:
        if args.tickets_command == 'create':
            if not args.input_file.exists():
                print(f"Error: File not found: {args.input_file}", file=sys.stderr)
                return 1
                
            result = create_tickets_from_agentscript_cli(
                str(args.input_file),
                args.epic_title,
                args.priority,
                args.assign_agent
            )
            
            print(f"✅ Created epic: {result['epic_id']}")
            print(f"✅ Created {len(result['tickets'])} tickets:")
            for ticket in result['tickets']:
                print(f"   - {ticket['id']}: {ticket['title']}")
            
            print(f"\n📊 Analysis Summary:")
            analysis = result['analysis']
            print(f"   - Complexity: {analysis['complexity']}")
            print(f"   - Estimated hours: {analysis['estimated_hours']}")
            print(f"   - Pipeline stages: {len(analysis['pipeline_stages'])}")
            print(f"   - Data sources: {len(analysis['data_sources'])}")
            print(f"   - Transformations: {len(analysis['transformations'])}")
            
            return 0
            
        elif args.tickets_command == 'generate':
            output_path = generate_agentscript_from_ticket_cli(
                args.ticket_id,
                str(args.output) if args.output else None,
                args.template
            )
            
            print(f"✅ Generated AgentScript file: {output_path}")
            return 0
            
        else:
            print("Available ticket commands: create, generate")
            return 1
            
    except TicketIntegrationError as e:
        print(f"❌ Ticket integration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AgentScript Compiler - Convert AgentScript to Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile AgentScript to Python
  agentscript compile data_processor.ags
  agentscript compile input.ags -o output.py
  agentscript compile *.ags
  
  # Ticket integration
  agentscript tickets create pipeline.ags --priority high
  agentscript tickets create pipeline.ags --epic-title "Data Pipeline" --assign-agent ai-dev
  agentscript tickets generate TICKET-123 -o generated_pipeline.ags
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
    
    # Ticket integration commands
    tickets_parser = subparsers.add_parser('tickets', help='Integrate with repo-tickets')
    tickets_subparsers = tickets_parser.add_subparsers(dest='tickets_command', help='Ticket operations')
    
    # Create tickets from AgentScript
    create_tickets_parser = tickets_subparsers.add_parser('create', help='Create tickets from AgentScript analysis')
    create_tickets_parser.add_argument('input_file', type=Path, help='AgentScript file to analyze')
    create_tickets_parser.add_argument('--epic-title', help='Title for the epic (optional)')
    create_tickets_parser.add_argument('--priority', default='medium', choices=['low', 'medium', 'high'], help='Ticket priority')
    create_tickets_parser.add_argument('--assign-agent', help='Assign tickets to AI agent')
    
    # Generate AgentScript from ticket
    generate_parser = tickets_subparsers.add_parser('generate', help='Generate AgentScript from ticket requirements')
    generate_parser.add_argument('ticket_id', help='Ticket ID to generate from')
    generate_parser.add_argument('-o', '--output', type=Path, help='Output AgentScript file path')
    generate_parser.add_argument('--template', default='basic-pipeline', help='Template to use for generation')
    
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
    
    elif args.command == 'tickets':
        return handle_ticket_commands(args)
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())