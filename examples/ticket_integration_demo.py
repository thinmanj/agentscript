#!/usr/bin/env python3
"""
AgentScript Ticket Integration Demo

This script demonstrates how to use the AgentScript ticket integration
features to create a bidirectional workflow between AgentScript and
the repo-tickets project management system.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentscript.ticket_integration import (
    AgentScriptTicketIntegration,
    TicketIntegrationError
)


def demo_analyze_agentscript():
    """Demo analyzing an AgentScript file for project management insights."""
    print("=" * 60)
    print("DEMO: Analyzing AgentScript File")
    print("=" * 60)
    
    integration = AgentScriptTicketIntegration()
    
    # Use the simple.ags example file
    ags_file = Path(__file__).parent / "simple.ags"
    if not ags_file.exists():
        print(f"⚠️  Example file {ags_file} not found. Creating a sample...")
        ags_file.write_text("""
use io.csv, io.json

intent DataProcessing {
    description: "Process customer data from CSV to JSON"
    
    pipeline: source.csv("customers.csv") 
           -> filter(record => record.age >= 18)
           -> sink.json("adults.json")
}
""".strip(), encoding='utf-8')
    
    try:
        analysis = integration.analyze_agentscript_file(ags_file)
        
        print(f"📁 File: {analysis['file']}")
        print(f"📊 Complexity: {analysis['complexity']}")
        print(f"⏱️  Estimated hours: {analysis['estimated_hours']}")
        print(f"🔧 Pipeline stages: {len(analysis['pipeline_stages'])}")
        print(f"📥 Data sources: {len(analysis['data_sources'])}")
        print(f"📤 Data sinks: {len(analysis['data_sinks'])}")
        print(f"🔄 Transformations: {len(analysis['transformations'])}")
        
        print(f"\n🎯 Intents found:")
        for intent in analysis['intents']:
            print(f"   - {intent['name']}: {intent['description']}")
            print(f"     Line: {intent['line']}, Stages: {len(intent['stages'])}")
            
        print(f"\n⚙️  Pipeline stages detail:")
        for stage in analysis['pipeline_stages']:
            print(f"   {stage['index']+1}. {stage['description']}")
            print(f"      Type: {stage['type']}, Operation: {stage['operation']}")
            if stage['parameters']:
                for param in stage['parameters']:
                    print(f"      - {param['type']}: {param['value']}")
        
    except TicketIntegrationError as e:
        print(f"❌ Analysis failed: {e}")


def demo_create_tickets():
    """Demo creating tickets from AgentScript analysis (requires repo-tickets)."""
    print("\n" + "=" * 60)
    print("DEMO: Creating Tickets from AgentScript")
    print("=" * 60)
    
    integration = AgentScriptTicketIntegration()
    
    if not integration.is_tickets_available():
        print("⚠️  repo-tickets CLI not available. To test this feature:")
        print("   1. Install repo-tickets: git clone https://github.com/thinmanj/repo-tickets")
        print("   2. Add tickets command to PATH")
        print("   3. Initialize tickets in project: tickets init")
        return
    
    if not integration.is_tickets_initialized():
        print("⚠️  repo-tickets not initialized in current project.")
        print("   Run: tickets init")
        return
    
    ags_file = Path(__file__).parent / "simple.ags"
    if not ags_file.exists():
        print(f"⚠️  Example file {ags_file} not found.")
        return
    
    try:
        result = integration.create_tickets_from_agentscript(
            ags_file,
            epic_title="Customer Data Processing Pipeline",
            priority="high",
            assign_agent="ai-dev"
        )
        
        print(f"✅ Created epic: {result['epic_id']}")
        print(f"✅ Created {len(result['tickets'])} tickets:")
        for ticket in result['tickets']:
            print(f"   - {ticket['id']}: {ticket['title']}")
            
    except TicketIntegrationError as e:
        print(f"❌ Ticket creation failed: {e}")


def demo_generate_agentscript():
    """Demo generating AgentScript from ticket (mock implementation)."""
    print("\n" + "=" * 60)
    print("DEMO: Generating AgentScript from Ticket")
    print("=" * 60)
    
    integration = AgentScriptTicketIntegration()
    
    # Mock ticket data for demo
    mock_ticket = {
        "id": "DEMO-123",
        "title": "Process Sales Data Pipeline",
        "description": """
        Create a data processing pipeline that:
        1. Loads sales data from "sales.csv"
        2. Filters records where amount > 100
        3. Saves results to "filtered_sales.json"
        
        Requirements:
        - Handle CSV input format
        - Apply amount filtering
        - Output as JSON format
        """
    }
    
    print(f"📝 Mock ticket: {mock_ticket['id']} - {mock_ticket['title']}")
    print(f"📋 Description preview: {mock_ticket['description'][:100]}...")
    
    # Generate AgentScript content
    agentscript_content = integration._generate_agentscript_content(
        mock_ticket, "basic-pipeline"
    )
    
    output_file = Path(__file__).parent / "generated_from_ticket.ags"
    output_file.write_text(agentscript_content, encoding='utf-8')
    
    print(f"\n✅ Generated AgentScript file: {output_file}")
    print(f"📄 Content preview:")
    print("-" * 40)
    print(agentscript_content)
    print("-" * 40)


def demo_integration_workflow():
    """Demo complete integration workflow."""
    print("\n" + "=" * 60)
    print("DEMO: Complete Integration Workflow")
    print("=" * 60)
    
    print("🔄 This demonstrates a complete workflow:")
    print("   1. Analyze existing AgentScript file")
    print("   2. Generate tickets for project management")
    print("   3. Create new AgentScript from ticket requirements")
    print("   4. Compile both files to Python")
    
    integration = AgentScriptTicketIntegration()
    
    # Step 1: Analyze existing file
    print(f"\n📊 Step 1: Analyzing existing AgentScript files...")
    ags_files = list(Path(__file__).parent.glob("*.ags"))
    
    if not ags_files:
        print("   No .ags files found in examples directory")
        return
    
    for ags_file in ags_files:
        try:
            analysis = integration.analyze_agentscript_file(ags_file)
            print(f"   - {ags_file.name}: {analysis['complexity']} complexity, "
                  f"{analysis['estimated_hours']}h estimated")
        except Exception as e:
            print(f"   - {ags_file.name}: Analysis failed - {e}")
    
    # Step 2: Mock ticket creation (real version would need repo-tickets)
    print(f"\n🎫 Step 2: Ticket creation (would create real tickets with repo-tickets)")
    print(f"   Epic: Customer Data Processing")
    print(f"   Tickets: Load CSV, Filter Data, Save JSON, Compile & Test")
    
    # Step 3: Generate new AgentScript from mock ticket
    print(f"\n📝 Step 3: Generating AgentScript from requirements...")
    mock_ticket = {
        "id": "REQ-456",
        "title": "Financial Report Generator",
        "description": 'Process "transactions.csv" and generate "monthly_report.json"'
    }
    
    output_file = Path(__file__).parent / "financial_report.ags"
    content = integration._generate_agentscript_content(mock_ticket, "basic-pipeline")
    output_file.write_text(content, encoding='utf-8')
    print(f"   Generated: {output_file.name}")
    
    # Step 4: Would compile files
    print(f"\n🔧 Step 4: Compilation (use 'agentscript compile *.ags')")
    print(f"   This would generate Python pandas pipeline code")
    
    print(f"\n✅ Integration workflow complete!")
    print(f"💡 Next steps:")
    print(f"   - Use 'agentscript tickets create <file>' with real repo-tickets")
    print(f"   - Set up AI agents to automate ticket workflows")
    print(f"   - Integrate with CI/CD for automatic compilation")


def main():
    """Run all demos."""
    print("🚀 AgentScript ↔ Repo-Tickets Integration Demo")
    print("=" * 60)
    
    # Ensure examples directory exists
    examples_dir = Path(__file__).parent
    examples_dir.mkdir(exist_ok=True)
    
    try:
        demo_analyze_agentscript()
        demo_create_tickets()
        demo_generate_agentscript()
        demo_integration_workflow()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully!")
        print("=" * 60)
        
        print(f"\n📚 To explore further:")
        print(f"   - Check generated files in {examples_dir}")
        print(f"   - Try: python -m agentscript.main tickets create simple.ags")
        print(f"   - Install repo-tickets for full functionality")
        print(f"   - Read INTEGRATION_PLAN.md for complete documentation")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()