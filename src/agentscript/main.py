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


def compile_file(input_file: Path, output_path: Path = None, target: str = 'pandas', **options):
    """Compile a single AgentScript file using the specified plugin."""
    try:
        # Read input file
        source_code = input_file.read_text(encoding='utf-8')
        
        # Parse AgentScript to AST
        print(f"Parsing {input_file}...")
        ast = parse_agentscript(source_code, str(input_file))
        
        if target == 'pandas':
            # Original pandas compilation
            print("Generating Python code...")
            python_code = generate_python_code(ast, str(input_file))
            
            # Determine output file
            if output_path is None:
                output_file = input_file.with_suffix('.py')
            elif output_path.is_dir():
                output_file = output_path / input_file.with_suffix('.py').name
            else:
                output_file = output_path
            
            # Write output file
            output_file.write_text(python_code, encoding='utf-8')
            print(f"✓ Compiled to {output_file}")
            
        else:
            # Use plugin system
            from .plugins import get_registry
            from .plugins.base import GenerationContext
            
            registry = get_registry()
            plugin = registry.get_plugin(target)
            
            if not plugin:
                raise ValueError(f"Unknown target framework: {target}")
            
            # Create generation context
            output_dir = output_path or input_file.parent / f"{input_file.stem}_{target}"
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            
            context = GenerationContext(
                source_file=input_file,
                output_dir=output_dir,
                target_framework=target,
                options=options
            )
            
            # Validate context
            errors = plugin.validate_context(context)
            if errors:
                for error in errors:
                    print(f"Error: {error}", file=sys.stderr)
                return 1
            
            # Generate code files
            print(f"Generating {target} application...")
            generated_files = plugin.generate_code(ast, context)
            
            if not generated_files:
                print("No files generated", file=sys.stderr)
                return 1
            
            # Write generated files
            for file_path, content in generated_files.items():
                full_path = output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
                print(f"✓ Generated {full_path}")
            
            # Show next steps
            dependencies = plugin.get_dependencies(context)
            if dependencies:
                print(f"\n📦 Install dependencies: pip install {' '.join(dependencies)}")
            
            print(f"\n🎉 Generated {target} application in {output_dir}")
        
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


def list_plugins(verbose: bool = False):
    """List available plugins and their capabilities."""
    try:
        from .plugins import get_registry
        
        registry = get_registry()
        plugin_names = registry.list_plugins()
        
        if not plugin_names:
            print("No plugins available.")
            return 0
        
        print("Available AgentScript plugins:")
        print("=" * 40)
        
        for name in sorted(plugin_names):
            plugin_info = registry.get_plugin_info(name)
            if not plugin_info:
                continue
                
            print(f"\n📦 {plugin_info['name']}")
            print(f"   {plugin_info['description']}")
            print(f"   Version: {plugin_info['version']}")
            
            # Show capabilities
            capabilities = []
            if plugin_info['supports_async']:
                capabilities.append('async')
            if plugin_info['supports_web']:
                capabilities.append('web')
            if plugin_info['supports_database']:
                capabilities.append('database')
            if plugin_info['supports_auth']:
                capabilities.append('auth')
            
            if capabilities:
                print(f"   Capabilities: {', '.join(capabilities)}")
            
            if verbose:
                print(f"   Output: {plugin_info['output_extension']} files")
                if plugin_info['dependencies']:
                    print(f"   Dependencies: {', '.join(plugin_info['dependencies'])}")
                if plugin_info['optional_dependencies']:
                    print(f"   Optional: {', '.join(plugin_info['optional_dependencies'])}")
        
        print(f"\n💡 Usage: agentscript compile <file.ags> --target <plugin>")
        return 0
        
    except ImportError as e:
        print(f"Error: Plugin system not available: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error listing plugins: {e}", file=sys.stderr)
        return 1


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
                args.assign_agent,
                args.target if hasattr(args, 'target') else None
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
  # Interactive configuration wizard
  agentscript init
  agentscript init pipeline.ags
  
  # Compile AgentScript to Python (default pandas)
  agentscript compile data_processor.ags
  agentscript compile input.ags -o output.py
  
  # Generate web applications
  agentscript compile pipeline.ags --target django --app-name "DataApp" --database postgresql
  agentscript compile pipeline.ags --target fastapi --with-auth --with-cors
  agentscript compile pipeline.ags --target flask --database mysql
  
  # Generate TUI applications
  agentscript compile pipeline.ags --target tui --app-name "Data Dashboard"
  
  # List available plugins
  agentscript plugins
  agentscript plugins --verbose
  
  # Ticket integration
  agentscript tickets create pipeline.ags --priority high
  agentscript tickets create pipeline.ags --epic-title "Data Pipeline" --assign-agent ai-dev
  agentscript tickets generate TICKET-123 -o generated_pipeline.ags
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Compile command (now supports plugins)
    compile_parser = subparsers.add_parser('compile', help='Compile AgentScript files')
    compile_parser.add_argument('files', nargs='+', type=Path,
                               help='AgentScript files to compile')
    compile_parser.add_argument('-o', '--output', type=Path,
                               help='Output directory or file')
    compile_parser.add_argument('--target', choices=['pandas', 'django', 'fastapi', 'flask', 'tui'],
                               default='pandas', help='Target framework for code generation')
    compile_parser.add_argument('--check', action='store_true',
                               help='Check syntax without generating output')
    
    # Framework-specific options
    compile_parser.add_argument('--app-name', help='Application name for web frameworks')
    compile_parser.add_argument('--database', choices=['sqlite', 'postgresql', 'mysql'], 
                               help='Database backend for web frameworks')
    compile_parser.add_argument('--with-admin', action='store_true',
                               help='Include admin interface (Django)')
    compile_parser.add_argument('--with-auth', action='store_true',
                               help='Include authentication support')
    compile_parser.add_argument('--with-cors', action='store_true',
                               help='Include CORS support for web APIs')
    compile_parser.add_argument('--async-mode', action='store_true',
                               help='Use async/await patterns where supported')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    # Plugin list command
    plugins_parser = subparsers.add_parser('plugins', help='List available plugins and their capabilities')
    plugins_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed plugin information')
    
    # Interactive wizard command
    wizard_parser = subparsers.add_parser('init', help='Interactive wizard for project configuration')
    wizard_parser.add_argument('source_file', nargs='?', type=Path, help='Optional AgentScript source file')
    
    # Ticket integration commands
    tickets_parser = subparsers.add_parser('tickets', help='Integrate with repo-tickets')
    tickets_subparsers = tickets_parser.add_subparsers(dest='tickets_command', help='Ticket operations')
    
    # Create tickets from AgentScript
    create_tickets_parser = tickets_subparsers.add_parser('create', help='Create tickets from AgentScript analysis')
    create_tickets_parser.add_argument('input_file', type=Path, help='AgentScript file to analyze')
    create_tickets_parser.add_argument('--epic-title', help='Title for the epic (optional)')
    create_tickets_parser.add_argument('--priority', default='medium', choices=['low', 'medium', 'high'], help='Ticket priority')
    create_tickets_parser.add_argument('--assign-agent', help='Assign tickets to AI agent')
    create_tickets_parser.add_argument('--target', choices=['django', 'fastapi', 'flask', 'tui'], 
                                      help='Target framework for framework-specific tickets')
    
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
        # Prepare compilation options
        compile_options = {}
        if hasattr(args, 'app_name') and args.app_name:
            compile_options['app_name'] = args.app_name
        if hasattr(args, 'database') and args.database:
            compile_options['database'] = True
            compile_options['database_type'] = args.database
        if hasattr(args, 'with_admin') and args.with_admin:
            compile_options['admin'] = True
        if hasattr(args, 'with_auth') and args.with_auth:
            compile_options['auth'] = True
        if hasattr(args, 'with_cors') and args.with_cors:
            compile_options['cors'] = True
        if hasattr(args, 'async_mode') and args.async_mode:
            compile_options['async_mode'] = True
        
        exit_code = 0
        for file_path in args.files:
            if not file_path.exists():
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                exit_code = 1
                continue
            
            if not file_path.suffix == '.ags':
                print(f"Warning: {file_path} doesn't have .ags extension", file=sys.stderr)
            
            # For multiple files, create individual output directories
            output_path = args.output
            if len(args.files) > 1 and args.target != 'pandas':
                output_path = args.output / file_path.stem if args.output else None
            
            result = compile_file(
                file_path, 
                output_path, 
                target=args.target,
                **compile_options
            )
            if result != 0:
                exit_code = result
        
        return exit_code
    
    elif args.command == 'plugins':
        return list_plugins(args.verbose)
    
    elif args.command == 'init':
        # Run interactive wizard
        try:
            from .interactive import run_interactive_wizard
            config = run_interactive_wizard(args.source_file if hasattr(args, 'source_file') else None)
            if config:
                print("\n✅ Configuration complete! Use 'agentscript compile' to generate code.")
                return 0
            else:
                print("\n❌ Configuration cancelled")
                return 1
        except ImportError:
            print("Error: Interactive mode requires 'rich' library", file=sys.stderr)
            print("Install with: pip install rich", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    
    elif args.command == 'tickets':
        return handle_ticket_commands(args)
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())