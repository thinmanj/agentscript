#!/usr/bin/env python3
"""
Comprehensive Plugin System Demonstration for AgentScript

This script demonstrates the full capabilities of the AgentScript plugin system by:
1. Listing all available plugins
2. Generating actual application files for each plugin
3. Creating working directory structures
4. Showing the generated code structure

Usage:
    python comprehensive_demo.py [--clean] [--plugin PLUGIN_NAME]
    
    --clean: Remove existing demo directories before generating
    --plugin: Generate only for specific plugin (django, fastapi, tui)
"""

import sys
import argparse
import shutil
from pathlib import Path

# Add AgentScript to path
sys.path.insert(0, '../src')

from agentscript.plugins import get_registry
from agentscript.plugins.base import GenerationContext
from agentscript.parser import parse_agentscript


def clean_demo_directories():
    """Remove existing demo directories."""
    demo_dirs = ['django_demo', 'fastapi_demo', 'tui_demo']
    for demo_dir in demo_dirs:
        dir_path = Path(demo_dir)
        if dir_path.exists():
            print(f"🧹 Removing existing directory: {demo_dir}")
            shutil.rmtree(dir_path)


def generate_plugin_demo(plugin_name: str, registry, ast):
    """Generate demo files for a specific plugin."""
    plugin = registry.get_plugin(plugin_name)
    
    # Plugin-specific configurations
    configs = {
        'django': {
            'output_dir': Path('django_demo'),
            'options': {'app_name': 'CustomerApp'}
        },
        'fastapi': {
            'output_dir': Path('fastapi_demo'),
            'options': {'app_name': 'customer_service'}
        },
        'tui': {
            'output_dir': Path('tui_demo'),
            'options': {'app_name': 'CustomerTUI'}
        }
    }
    
    config = configs[plugin_name]
    
    # Create context
    context = GenerationContext(
        source_file=Path('sample_pipeline.ags'),
        output_dir=config['output_dir'],
        target_framework=plugin_name,
        options=config['options']
    )
    
    print(f"\n🚀 Generating {plugin_name.upper()} application...")
    
    # Generate files
    files = plugin.generate_code(ast, context)
    
    # Create output directory
    config['output_dir'].mkdir(exist_ok=True)
    
    # Write files to disk
    written_files = []
    for file_path, content in files.items():
        full_path = config['output_dir'] / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        written_files.append(full_path)
    
    print(f"📁 Created {len(written_files)} files in {config['output_dir']}/")
    
    # Show directory structure
    show_directory_tree(config['output_dir'])
    
    return written_files


def show_directory_tree(directory: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0):
    """Show directory structure in tree format."""
    if current_depth >= max_depth:
        return
        
    items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")
        
        if item.is_dir() and current_depth < max_depth - 1:
            extension = "    " if is_last else "│   "
            show_directory_tree(item, prefix + extension, max_depth, current_depth + 1)


def show_sample_code(directory: Path, plugin_name: str):
    """Show sample generated code for each plugin."""
    sample_files = {
        'django': 'CustomerApp/models.py',
        'fastapi': 'main.py',
        'tui': 'main.py'
    }
    
    sample_file = sample_files.get(plugin_name)
    if sample_file:
        file_path = directory / sample_file
        if file_path.exists():
            print(f"\n📝 Sample code from {sample_file}:")
            print("=" * 60)
            with open(file_path) as f:
                content = f.read()
                # Show first 15 lines
                lines = content.split('\n')[:15]
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line}")
                if len(content.split('\n')) > 15:
                    print("    ... (truncated)")


def main():
    parser = argparse.ArgumentParser(description='AgentScript Plugin System Demo')
    parser.add_argument('--clean', action='store_true', help='Clean existing demo directories')
    parser.add_argument('--plugin', choices=['django', 'fastapi', 'tui'], help='Generate only specific plugin')
    args = parser.parse_args()
    
    print("🎯 AgentScript Plugin System - Comprehensive Demo")
    print("=" * 50)
    
    # Clean directories if requested
    if args.clean:
        clean_demo_directories()
    
    # Load registry and sample
    registry = get_registry()
    
    print(f"\n📦 Available plugins: {len(registry.list_plugins())}")
    for name in registry.list_plugins():
        plugin = registry.get_plugin(name)
        capabilities = []
        if plugin.config.supports_async:
            capabilities.append('async')
        if plugin.config.supports_web:
            capabilities.append('web')
        if plugin.config.supports_database:
            capabilities.append('database')
        if plugin.config.supports_auth:
            capabilities.append('auth')
        
        capabilities_str = ', '.join(capabilities) if capabilities else 'basic'
        print(f"  • {name}: {plugin.config.description} ({capabilities_str})")
    
    # Parse sample AgentScript
    sample_content = Path('sample_pipeline.ags').read_text()
    ast = parse_agentscript(sample_content, 'sample_pipeline.ags')
    
    print(f"\n📄 Parsed AgentScript with {len(ast.statements)} statements")
    
    # Generate for specific plugin or all plugins
    if args.plugin:
        plugins_to_generate = [args.plugin]
    else:
        plugins_to_generate = registry.list_plugins()
    
    total_files = 0
    
    for plugin_name in plugins_to_generate:
        try:
            written_files = generate_plugin_demo(plugin_name, registry, ast)
            total_files += len(written_files)
            
            # Show sample code
            config_output_dir = {
                'django': Path('django_demo'),
                'fastapi': Path('fastapi_demo'), 
                'tui': Path('tui_demo')
            }[plugin_name]
            
            show_sample_code(config_output_dir, plugin_name)
            
        except Exception as e:
            print(f"❌ Error generating {plugin_name}: {e}")
    
    print(f"\n✅ Demo completed! Generated {total_files} files total.")
    print("\n💡 Next steps:")
    print("  • Navigate to each demo directory")
    print("  • Install requirements: pip install -r requirements.txt") 
    print("  • Follow framework-specific setup instructions")
    print("  • Customize the generated code for your needs")
    
    print("\n🔧 CLI Usage Examples:")
    print("  agentscript compile sample_pipeline.ags --target django --app-name MyApp")
    print("  agentscript compile sample_pipeline.ags --target fastapi --app-name api_service")
    print("  agentscript compile sample_pipeline.ags --target tui --app-name DataProcessorTUI")


if __name__ == '__main__':
    main()