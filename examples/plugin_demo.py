#!/usr/bin/env python3
"""
AgentScript Plugin System Demonstration

This script demonstrates the pluggable framework capabilities of AgentScript,
showing how to generate different types of applications (Django, FastAPI, TUI)
from the same AgentScript source files.
"""

import sys
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentscript.plugins import get_registry
from agentscript.plugins.base import GenerationContext
from agentscript.parser import parse_agentscript


def demonstrate_plugin_system():
    """Demonstrate the plugin system capabilities."""
    print("🚀 AgentScript Plugin System Demonstration")
    print("=" * 60)
    
    # Get plugin registry
    try:
        registry = get_registry()
        plugin_names = registry.list_plugins()
        
        if not plugin_names:
            print("❌ No plugins found. Please ensure plugins are properly installed.")
            return
        
        print(f"📦 Found {len(plugin_names)} plugins: {', '.join(plugin_names)}")
        print()
        
        # Show plugin details
        for name in sorted(plugin_names):
            plugin_info = registry.get_plugin_info(name)
            if plugin_info:
                print(f"🔌 {plugin_info['name']}")
                print(f"   Description: {plugin_info['description']}")
                print(f"   Version: {plugin_info['version']}")
                
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
                
                print(f"   Dependencies: {', '.join(plugin_info['dependencies'][:3])}{'...' if len(plugin_info['dependencies']) > 3 else ''}")
                print()
        
    except Exception as e:
        print(f"❌ Error loading plugins: {e}")
        return


def demonstrate_code_generation():
    """Demonstrate code generation with different plugins."""
    print("\n🛠️  Code Generation Demonstration")
    print("=" * 60)
    
    # Create a sample AgentScript file
    sample_ags = Path(__file__).parent / "sample_pipeline.ags"
    sample_content = """
use io.csv, io.json

intent CustomerAnalysis {
    description: "Analyze customer data and generate insights"
    
    pipeline: source.csv("customers.csv") 
           -> filter(customer => customer.age >= 18)
           -> sink.json("customer_analysis.json")
}

intent SalesReport {
    description: "Generate monthly sales reports"
    
    pipeline: source.csv("sales.csv")
           -> filter(sale => sale.amount > 100)
           -> sink.csv("high_value_sales.csv")
}
"""
    
    # Write sample file
    sample_ags.write_text(sample_content.strip(), encoding='utf-8')
    print(f"📝 Created sample AgentScript: {sample_ags.name}")
    
    # Parse the sample
    try:
        ast = parse_agentscript(sample_content.strip(), str(sample_ags))
        print(f"✅ Successfully parsed {len(ast.statements)} statements")
        
        # Count intents
        intents = [stmt for stmt in ast.statements if hasattr(stmt, 'name') and hasattr(stmt, 'pipeline')]
        print(f"🎯 Found {len(intents)} intents: {', '.join(stmt.name for stmt in intents)}")
        
    except Exception as e:
        print(f"❌ Failed to parse sample: {e}")
        return
    
    print()


def demonstrate_framework_generation():
    """Demonstrate generating different framework applications."""
    print("🏗️  Framework Generation Examples")
    print("=" * 60)
    
    sample_ags = Path(__file__).parent / "sample_pipeline.ags"
    
    # Examples of what each plugin would generate
    examples = [
        {
            "target": "django",
            "description": "Django web application with admin interface",
            "command": f"agentscript compile {sample_ags} --target django --app-name CustomerApp --database postgresql --with-admin",
            "outputs": [
                "CustomerApp/models.py - Django models for pipeline data",
                "CustomerApp/admin.py - Admin interface configuration",
                "CustomerApp/views.py - REST API viewsets",
                "CustomerApp/urls.py - URL routing configuration",
                "CustomerApp/serializers.py - DRF serializers",
                "requirements.txt - Dependencies list"
            ]
        },
        {
            "target": "fastapi",
            "description": "Modern async FastAPI application",
            "command": f"agentscript compile {sample_ags} --target fastapi --with-auth --with-cors --database postgresql",
            "outputs": [
                "main.py - FastAPI application with CORS",
                "models.py - Pydantic data models",
                "routers/pipelines.py - API endpoints",
                "database.py - SQLAlchemy async config",
                "config.py - Application settings",
                "Dockerfile - Container configuration"
            ]
        },
        {
            "target": "tui",
            "description": "Interactive terminal user interface",
            "command": f"agentscript compile {sample_ags} --target tui --app-name 'Customer Dashboard'",
            "outputs": [
                "main.py - Textual TUI application",
                "screens/main_screen.py - Dashboard screen",
                "widgets/pipeline_widget.py - Pipeline controls",
                "executor.py - Pipeline execution engine",
                "models.py - Data models",
                "run.py - Startup script"
            ]
        }
    ]
    
    for example in examples:
        print(f"📱 {example['target'].upper()}: {example['description']}")
        print(f"   Command: {example['command']}")
        print("   Generated files:")
        for output in example['outputs']:
            print(f"     • {output}")
        print()


def demonstrate_cli_usage():
    """Show CLI usage examples."""
    print("💻 CLI Usage Examples")
    print("=" * 60)
    
    examples = [
        "# List available plugins",
        "agentscript plugins",
        "agentscript plugins --verbose",
        "",
        "# Generate pandas Python (default)",
        "agentscript compile pipeline.ags",
        "",
        "# Generate Django web app",
        "agentscript compile pipeline.ags --target django --app-name MyApp --database postgresql",
        "",
        "# Generate FastAPI with authentication",
        "agentscript compile pipeline.ags --target fastapi --with-auth --with-cors",
        "",
        "# Generate TUI dashboard", 
        "agentscript compile pipeline.ags --target tui --app-name 'Data Dashboard'",
        "",
        "# Multiple targets for the same source",
        "agentscript compile pipeline.ags --target django -o django_app/",
        "agentscript compile pipeline.ags --target fastapi -o fastapi_app/",
        "agentscript compile pipeline.ags --target tui -o tui_app/",
    ]
    
    for example in examples:
        if example.startswith("#"):
            print(f"\n{example}")
        elif example == "":
            pass
        else:
            print(f"  {example}")
    print()


def demonstrate_extensibility():
    """Show how the plugin system can be extended."""
    print("🔧 Plugin System Extensibility")
    print("=" * 60)
    
    print("The AgentScript plugin system is designed for easy extension:")
    print()
    
    print("📝 Creating a New Plugin:")
    print("  1. Inherit from BasePlugin")
    print("  2. Implement generate_code() method")
    print("  3. Define plugin metadata (dependencies, capabilities)")
    print("  4. Place in src/agentscript/plugins/<name>_plugin.py")
    print("  5. Plugin is auto-discovered and registered")
    print()
    
    print("🎯 Plugin Capabilities:")
    print("  • supports_async: Async/await support")
    print("  • supports_web: Web framework features")
    print("  • supports_database: Database integration")
    print("  • supports_auth: Authentication systems")
    print()
    
    print("📦 Potential Future Plugins:")
    print("  • flask - Flask web framework")
    print("  • streamlit - Streamlit data apps") 
    print("  • notebook - Jupyter notebook generation")
    print("  • airflow - Apache Airflow DAGs")
    print("  • spark - Apache Spark jobs")
    print("  • kubernetes - K8s deployment configs")
    print()


def main():
    """Run the complete demonstration."""
    print("🎪 Welcome to the AgentScript Plugin System Demo!")
    print("This demonstration shows how AgentScript can generate code for")
    print("multiple frameworks from the same pipeline definitions.\n")
    
    try:
        demonstrate_plugin_system()
        demonstrate_code_generation()
        demonstrate_framework_generation()
        demonstrate_cli_usage()
        demonstrate_extensibility()
        
        print("✨ Demonstration Complete!")
        print("=" * 60)
        print("🚀 Try it yourself:")
        print(f"  cd {Path(__file__).parent}")
        print("  agentscript plugins")
        print("  agentscript compile sample_pipeline.ags --target django")
        print("  agentscript compile sample_pipeline.ags --target fastapi")
        print("  agentscript compile sample_pipeline.ags --target tui")
        print("\n💡 Each target generates a complete, runnable application!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()