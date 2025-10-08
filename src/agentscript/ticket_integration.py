"""
AgentScript ↔ Repo-Tickets Integration Module

Provides bidirectional integration between AgentScript and the repo-tickets
project management system. Enables AI agents to generate tickets from AgentScript
analysis and create AgentScript programs from ticket requirements.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .parser import parse_agentscript, ParseError
from .lexer import LexerError
from .ast_nodes import *


class TicketIntegrationError(Exception):
    """Raised when ticket integration operations fail."""
    pass


class AgentScriptTicketIntegration:
    """Manages integration between AgentScript and repo-tickets."""
    
    def __init__(self, project_root: Path = None):
        """Initialize integration with project root directory."""
        self.project_root = project_root or Path.cwd()
        self.tickets_dir = self.project_root / ".tickets"
        self.agentscript_dir = self.project_root / "agentscript"
        self.generated_dir = self.project_root / "generated"
        
    def is_tickets_initialized(self) -> bool:
        """Check if repo-tickets is initialized in the project."""
        return self.tickets_dir.exists() and (self.tickets_dir / "tickets.json").exists()
    
    def is_tickets_available(self) -> bool:
        """Check if tickets command is available."""
        try:
            subprocess.run(['tickets', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        self.agentscript_dir.mkdir(exist_ok=True)
        self.generated_dir.mkdir(exist_ok=True)
    
    def analyze_agentscript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze an AgentScript file and extract project structure information."""
        try:
            source_code = file_path.read_text(encoding='utf-8')
            ast = parse_agentscript(source_code, str(file_path))
            
            analysis = {
                "file": str(file_path),
                "intents": [],
                "imports": [],
                "complexity": "low",
                "estimated_hours": 2,
                "pipeline_stages": [],
                "data_sources": [],
                "data_sinks": [],
                "transformations": []
            }
            
            # Analyze AST structure
            for stmt in ast.statements:
                if isinstance(stmt, ImportStatement):
                    analysis["imports"].extend(stmt.modules)
                    
                elif isinstance(stmt, IntentDeclaration):
                    intent_info = {
                        "name": stmt.name,
                        "description": stmt.description or "No description provided",
                        "line": stmt.position.line,
                        "stages": []
                    }
                    
                    if stmt.pipeline:
                        # Analyze pipeline stages
                        for i, stage in enumerate(stmt.pipeline.stages):
                            stage_info = self._analyze_pipeline_stage(stage, i)
                            intent_info["stages"].append(stage_info)
                            analysis["pipeline_stages"].append(stage_info)
                            
                            # Categorize stages
                            if stage_info["type"] == "source":
                                analysis["data_sources"].append(stage_info)
                            elif stage_info["type"] == "sink":
                                analysis["data_sinks"].append(stage_info)
                            elif stage_info["type"] in ["filter", "transform"]:
                                analysis["transformations"].append(stage_info)
                    
                    analysis["intents"].append(intent_info)
            
            # Estimate complexity based on pipeline stages and transformations
            total_stages = len(analysis["pipeline_stages"])
            transformations = len(analysis["transformations"])
            
            if total_stages <= 2 and transformations == 0:
                analysis["complexity"] = "low"
                analysis["estimated_hours"] = 2
            elif total_stages <= 5 and transformations <= 2:
                analysis["complexity"] = "medium"
                analysis["estimated_hours"] = 5
            else:
                analysis["complexity"] = "high"
                analysis["estimated_hours"] = 10
                
            return analysis
            
        except (LexerError, ParseError) as e:
            raise TicketIntegrationError(f"Failed to parse AgentScript file: {e}")
        except Exception as e:
            raise TicketIntegrationError(f"Analysis failed: {e}")
    
    def _analyze_pipeline_stage(self, stage: PipelineStage, index: int) -> Dict[str, Any]:
        """Analyze a single pipeline stage."""
        stage_info = {
            "index": index,
            "type": "unknown",
            "operation": "unknown",
            "description": "",
            "parameters": []
        }
        
        if isinstance(stage.operation, FunctionCall):
            if isinstance(stage.operation.function, AttributeAccess):
                obj_name = getattr(stage.operation.function.object, 'name', 'unknown')
                attr_name = stage.operation.function.attribute
                
                if obj_name == "source":
                    stage_info["type"] = "source"
                    stage_info["operation"] = f"load_{attr_name}"
                    stage_info["description"] = f"Load data from {attr_name.upper()} file"
                elif obj_name == "sink":
                    stage_info["type"] = "sink"
                    stage_info["operation"] = f"save_{attr_name}"
                    stage_info["description"] = f"Save data to {attr_name.upper()} file"
                
                # Extract file parameters
                if stage.operation.arguments:
                    for arg in stage.operation.arguments:
                        if isinstance(arg, Literal) and isinstance(arg.value, str):
                            stage_info["parameters"].append({
                                "type": "file",
                                "value": arg.value
                            })
            
            elif hasattr(stage.operation.function, 'name'):
                func_name = stage.operation.function.name
                if func_name == "filter":
                    stage_info["type"] = "filter"
                    stage_info["operation"] = "filter_data"
                    stage_info["description"] = "Filter data based on conditions"
                elif func_name == "transform":
                    stage_info["type"] = "transform"
                    stage_info["operation"] = "transform_data"
                    stage_info["description"] = "Transform data structure"
                else:
                    stage_info["operation"] = func_name
                    stage_info["description"] = f"Apply {func_name} operation"
        
        return stage_info
    
    def create_tickets_from_agentscript(
        self, 
        file_path: Path, 
        epic_title: str = None,
        priority: str = "medium",
        assign_agent: str = None
    ) -> Dict[str, Any]:
        """Create tickets and epic from AgentScript analysis."""
        if not self.is_tickets_available():
            raise TicketIntegrationError("tickets command not available")
        
        if not self.is_tickets_initialized():
            raise TicketIntegrationError("repo-tickets not initialized in project")
        
        analysis = self.analyze_agentscript_file(file_path)
        
        # Generate epic title if not provided
        if not epic_title:
            if analysis["intents"]:
                epic_title = f"{analysis['intents'][0]['name']} Pipeline"
            else:
                epic_title = f"{file_path.stem} Implementation"
        
        result = {
            "epic_id": None,
            "tickets": [],
            "analysis": analysis
        }
        
        try:
            # Create epic
            epic_cmd = [
                "tickets", "epic", "create", epic_title,
                "--description", f"Implementation of AgentScript pipeline from {file_path.name}",
                "--priority", priority,
                "--format", "json"
            ]
            
            epic_result = subprocess.run(epic_cmd, capture_output=True, text=True, check=True)
            epic_data = json.loads(epic_result.stdout)
            result["epic_id"] = epic_data["id"]
            
            # Create tickets for each pipeline stage
            for intent in analysis["intents"]:
                for stage in intent["stages"]:
                    ticket_title = f"Implement {stage['description']}"
                    ticket_desc = f"""
Implementation task for pipeline stage {stage['index'] + 1}.

**Stage Details:**
- Type: {stage['type']}
- Operation: {stage['operation']}
- Description: {stage['description']}
- Source File: {file_path.name}:{intent['line']}

**Parameters:**
{self._format_stage_parameters(stage['parameters'])}

**Generated from AgentScript analysis of {file_path.name}**
"""
                    
                    ticket_cmd = [
                        "tickets", "create", ticket_title,
                        "--description", ticket_desc.strip(),
                        "--priority", priority,
                        "--epic-id", result["epic_id"],
                        "--labels", f"agentscript,{stage['type']},{analysis['complexity']}",
                        "--format", "json"
                    ]
                    
                    if assign_agent:
                        ticket_cmd.extend(["--assignee", assign_agent])
                    
                    ticket_result = subprocess.run(ticket_cmd, capture_output=True, text=True, check=True)
                    ticket_data = json.loads(ticket_result.stdout)
                    
                    result["tickets"].append({
                        "id": ticket_data["id"],
                        "title": ticket_title,
                        "stage": stage
                    })
            
            # Create overall implementation ticket
            impl_title = f"Compile and Test {file_path.stem}"
            impl_desc = f"""
Overall compilation and testing task for the AgentScript pipeline.

**Deliverables:**
- Compile {file_path.name} to Python
- Generate test cases from pipeline stages
- Validate output format and data quality
- Update documentation

**Complexity:** {analysis['complexity']}
**Estimated Hours:** {analysis['estimated_hours']}

**Generated from AgentScript analysis of {file_path.name}**
"""
            
            impl_cmd = [
                "tickets", "create", impl_title,
                "--description", impl_desc.strip(),
                "--priority", priority,
                "--epic-id", result["epic_id"],
                "--labels", f"agentscript,compilation,{analysis['complexity']}",
                "--estimated-hours", str(analysis['estimated_hours']),
                "--format", "json"
            ]
            
            if assign_agent:
                impl_cmd.extend(["--assignee", assign_agent])
            
            impl_result = subprocess.run(impl_cmd, capture_output=True, text=True, check=True)
            impl_data = json.loads(impl_result.stdout)
            
            result["tickets"].append({
                "id": impl_data["id"],
                "title": impl_title,
                "stage": {"type": "compilation", "operation": "compile_and_test"}
            })
            
            return result
            
        except subprocess.CalledProcessError as e:
            raise TicketIntegrationError(f"Failed to create tickets: {e.stderr}")
        except json.JSONDecodeError as e:
            raise TicketIntegrationError(f"Failed to parse tickets response: {e}")
    
    def _format_stage_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format stage parameters for ticket description."""
        if not parameters:
            return "None"
        
        lines = []
        for param in parameters:
            if param["type"] == "file":
                lines.append(f"- File: {param['value']}")
            else:
                lines.append(f"- {param['type']}: {param['value']}")
        
        return "\n".join(lines)
    
    def generate_agentscript_from_ticket(
        self,
        ticket_id: str,
        output_file: Path = None,
        template: str = "basic-pipeline"
    ) -> Path:
        """Generate AgentScript file from ticket requirements."""
        if not self.is_tickets_available():
            raise TicketIntegrationError("tickets command not available")
        
        try:
            # Fetch ticket details
            ticket_cmd = ["tickets", "show", ticket_id, "--format", "json"]
            ticket_result = subprocess.run(ticket_cmd, capture_output=True, text=True, check=True)
            ticket_data = json.loads(ticket_result.stdout)
            
            # Generate output filename if not provided
            if not output_file:
                safe_title = "".join(c if c.isalnum() or c in "_-" else "_" for c in ticket_data["title"].lower())
                output_file = self.agentscript_dir / f"{safe_title}.ags"
            
            self.ensure_directories()
            
            # Generate AgentScript content based on ticket
            agentscript_content = self._generate_agentscript_content(ticket_data, template)
            
            # Write file
            output_file.write_text(agentscript_content, encoding='utf-8')
            
            return output_file
            
        except subprocess.CalledProcessError as e:
            raise TicketIntegrationError(f"Failed to fetch ticket {ticket_id}: {e.stderr}")
        except json.JSONDecodeError as e:
            raise TicketIntegrationError(f"Failed to parse ticket response: {e}")
    
    def _generate_agentscript_content(self, ticket_data: Dict[str, Any], template: str) -> str:
        """Generate AgentScript content from ticket data."""
        # Extract intent name from ticket title
        intent_name = "".join(word.capitalize() for word in ticket_data["title"].split() if word.isalnum())
        if not intent_name:
            intent_name = "GeneratedIntent"
        
        # Analyze description for data processing patterns
        description = ticket_data.get("description", "")
        
        # Determine imports based on description content
        imports = []
        if any(word in description.lower() for word in ["csv", "excel", "spreadsheet"]):
            imports.append("io.csv")
        if any(word in description.lower() for word in ["json", "api", "rest"]):
            imports.append("io.json")
        
        if not imports:
            imports = ["io.csv"]  # Default
        
        # Generate pipeline based on template and description analysis
        pipeline = self._generate_pipeline_from_description(description, template)
        
        # Build AgentScript content
        lines = [
            f"// Generated from ticket {ticket_data['id']}: {ticket_data['title']}",
            f"// Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"use {', '.join(imports)}",
            "",
            f"intent {intent_name} {{",
            f'    description: "{ticket_data.get("title", "Generated intent")}"',
            "",
            f"    pipeline: {pipeline}",
            "}"
        ]
        
        return "\n".join(lines)
    
    def _generate_pipeline_from_description(self, description: str, template: str) -> str:
        """Generate pipeline code from description and template."""
        desc_lower = description.lower()
        
        # Try to extract file names and operations from description
        source_file = "input.csv"
        output_file = "output.json"
        
        # Look for file references in description
        import re
        file_matches = re.findall(r'[\"\']([^\"\']*\.(csv|json|xlsx|txt))[\"\']', description)
        if file_matches:
            if len(file_matches) >= 1:
                source_file = file_matches[0][0]
            if len(file_matches) >= 2:
                output_file = file_matches[1][0]
        
        # Determine source and sink operations
        if source_file.endswith('.csv'):
            source_op = f'source.csv("{source_file}")'
        elif source_file.endswith('.json'):
            source_op = f'source.json("{source_file}")'
        else:
            source_op = f'source.csv("{source_file}")'
        
        if output_file.endswith('.csv'):
            sink_op = f'sink.csv("{output_file}")'
        elif output_file.endswith('.json'):
            sink_op = f'sink.json("{output_file}")'
        else:
            sink_op = f'sink.json("{output_file}")'
        
        # Add filtering if mentioned
        operations = [source_op]
        
        if any(word in desc_lower for word in ["filter", "where", "condition", "select"]):
            # Try to extract filter conditions
            if "age" in desc_lower and ("18" in desc_lower or "adult" in desc_lower):
                operations.append("filter(record => record.age >= 18)")
            elif "amount" in desc_lower and any(num in description for num in ["100", "1000"]):
                operations.append("filter(record => record.amount > 100)")
            else:
                operations.append("filter(record => record.active == true)")
        
        operations.append(sink_op)
        
        return " -> ".join(operations)


def create_tickets_from_agentscript_cli(
    file_path: str,
    epic_title: str = None,
    priority: str = "medium",
    assign_agent: str = None
) -> Dict[str, Any]:
    """CLI wrapper for creating tickets from AgentScript analysis."""
    integration = AgentScriptTicketIntegration()
    return integration.create_tickets_from_agentscript(
        Path(file_path), epic_title, priority, assign_agent
    )


def generate_agentscript_from_ticket_cli(
    ticket_id: str,
    output_file: str = None,
    template: str = "basic-pipeline"
) -> str:
    """CLI wrapper for generating AgentScript from ticket."""
    integration = AgentScriptTicketIntegration()
    output_path = integration.generate_agentscript_from_ticket(
        ticket_id, Path(output_file) if output_file else None, template
    )
    return str(output_path)