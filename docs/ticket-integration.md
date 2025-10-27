# Framework-Aware Ticket Integration

The AgentScript ticket integration now supports framework-specific ticket generation, creating detailed implementation tasks tailored to your target framework (Django, FastAPI, Flask, or TUI).

## Overview

When creating tickets from AgentScript analysis, you can now specify a target framework to automatically generate framework-specific implementation tickets with:

- **Framework-specific tasks** (e.g., "Create Django models", "Implement Pydantic schemas")
- **Detailed implementation notes** for each task
- **Framework best practices** embedded in ticket descriptions
- **Appropriate labels** for filtering and organization

## Usage

### Basic Ticket Creation

Create tickets from an AgentScript file:

```bash
agentscript tickets create pipeline.ags
```

### Framework-Specific Tickets

Generate tickets with framework-specific implementation tasks:

```bash
# Django
agentscript tickets create pipeline.ags --target django

# FastAPI
agentscript tickets create pipeline.ags --target fastapi

# Flask
agentscript tickets create pipeline.ags --target flask

# TUI
agentscript tickets create pipeline.ags --target tui
```

### Complete Example

```bash
agentscript tickets create data_pipeline.ags \
  --target django \
  --epic-title "Data Pipeline Implementation" \
  --priority high \
  --assign-agent ai-dev
```

## Generated Tickets

### Standard Pipeline Tickets

For each pipeline stage, the system creates:

1. **Stage Implementation Tickets**
   - One ticket per pipeline stage
   - Includes stage type, operation, and parameters
   - Links to source file and line number

2. **Compilation and Testing Ticket**
   - Overall integration ticket
   - Framework-specific deliverables
   - Testing requirements

### Framework-Specific Tickets

When a target framework is specified, additional tickets are created:

#### Django Tickets

```
[DJANGO] Set up Django project structure
[DJANGO] Create database models
[DJANGO] Implement serializers
[DJANGO] Create API views
[DJANGO] Configure admin interface
[DJANGO] Add authentication
```

Each ticket includes:
- **Implementation notes**: "Use django-admin startproject and create apps..."
- **Framework context**: Django REST Framework, ModelSerializer, etc.
- **Best practices**: ViewSets, mixins, proper model inheritance

#### FastAPI Tickets

```
[FASTAPI] Set up FastAPI project
[FASTAPI] Create Pydantic models
[FASTAPI] Implement async endpoints
[FASTAPI] Configure database
[FASTAPI] Add authentication
[FASTAPI] Generate OpenAPI docs
```

Includes async/await patterns, Pydantic validation, and OpenAPI configuration.

#### Flask Tickets

```
[FLASK] Set up Flask application
[FLASK] Create database models
[FLASK] Design blueprints
[FLASK] Implement API routes
[FLASK] Configure Flask-Admin
[FLASK] Add database migrations
```

Covers application factory pattern, blueprints, and Flask extensions.

#### TUI Tickets

```
[TUI] Design TUI layout
[TUI] Implement data widgets
[TUI] Add interactive controls
[TUI] Implement pipeline executor
[TUI] Add configuration screen
[TUI] Implement logging view
```

Includes Rich/Textual widget implementation and async background tasks.

## Ticket Structure

### Epic

All tickets are organized under an epic:

```
Epic: Data Pipeline Implementation
├── Pipeline Stage Tickets
│   ├── Implement Load data from CSV file
│   ├── Implement Filter data based on conditions
│   └── Implement Save data to JSON file
├── Framework-Specific Tickets
│   ├── [DJANGO] Set up Django project structure
│   ├── [DJANGO] Create database models
│   ├── [DJANGO] Implement serializers
│   ├── [DJANGO] Create API views
│   ├── [DJANGO] Configure admin interface
│   └── [DJANGO] Add authentication
└── Integration Ticket
    └── Compile and Test for Django
```

### Ticket Details

Each framework ticket includes:

**Title**: `[FRAMEWORK] Task name`

**Description**:
```markdown
Task description

**Framework:** Django
**Source:** pipeline.ags

**Implementation Notes:**
Specific guidance on implementing this task using framework best practices

**Generated from AgentScript analysis for django target**
```

**Labels**: `agentscript`, `django`, `implementation`

**Epic**: Link to parent epic

**Priority**: Inherited from command

**Assignee**: Optional AI agent assignment

## Framework Deliverables

### Django Deliverables

- Create Django models from pipeline data structures
- Implement serializers for API endpoints
- Configure Django admin interface
- Set up database migrations
- Create API views and URL routing

### FastAPI Deliverables

- Create Pydantic models for request/response validation
- Implement async API endpoints
- Configure OpenAPI documentation
- Set up dependency injection for database
- Create background tasks for pipeline execution

### Flask Deliverables

- Create Flask blueprints for API routes
- Implement SQLAlchemy models
- Configure Flask-Admin interface
- Set up database migrations with Flask-Migrate
- Create API endpoints with error handling

### TUI Deliverables

- Design terminal user interface layout
- Implement Rich/Textual widgets for data display
- Create interactive pipeline controls
- Add progress indicators and status displays
- Configure keyboard shortcuts and navigation

## Implementation Notes by Framework

### Django Implementation Notes

| Task | Notes |
|------|-------|
| Set up project | Use `django-admin startproject` and create apps |
| Create models | Inherit from `models.Model` with proper field types |
| Implement serializers | Use `ModelSerializer` for automatic mapping |
| Create API views | Use ViewSets with appropriate mixins |
| Configure admin | Register models with custom `ModelAdmin` |
| Add authentication | Use DRF's `TokenAuthentication` or JWT |

### FastAPI Implementation Notes

| Task | Notes |
|------|-------|
| Set up project | Create `main.py` with `FastAPI()` instance |
| Create models | Use `BaseModel` with type hints and validators |
| Implement endpoints | Use `async def` with `await` for DB operations |
| Configure database | Use SQLAlchemy 2.0 async engine with asyncpg |
| Add authentication | Implement OAuth2 with JWT tokens |
| Generate docs | Customize metadata, tags, and examples |

### Flask Implementation Notes

| Task | Notes |
|------|-------|
| Set up app | Use application factory pattern with `create_app()` |
| Create models | Use Flask-SQLAlchemy's `db.Model` base class |
| Design blueprints | Organize routes by functionality (api, admin, main) |
| Implement routes | Use `@blueprint.route()` decorators properly |
| Configure admin | Create `ModelView` classes for each model |
| Add migrations | Initialize Alembic and create initial migration |

### TUI Implementation Notes

| Task | Notes |
|------|-------|
| Design layout | Use Textual's `Screen` and `Container` widgets |
| Implement widgets | Create custom widgets inheriting from `Widget` |
| Add controls | Use `Button`, `Input`, and `DataTable` widgets |
| Implement executor | Use `asyncio.create_task()` for background execution |
| Add config screen | Create modal dialog with form inputs |
| Implement logging | Use `RichLog` widget for scrollable log display |

## Examples

### Example 1: Django Web Application

```bash
agentscript tickets create sales_pipeline.ags \
  --target django \
  --epic-title "Sales Analytics Dashboard" \
  --priority high
```

**Generated Tickets**:
1. Pipeline stages (3 tickets for load, transform, save)
2. Django setup and configuration (6 tickets)
3. Integration and testing (1 ticket)

**Total**: 10 tickets organized under "Sales Analytics Dashboard" epic

### Example 2: FastAPI Microservice

```bash
agentscript tickets create api_pipeline.ags \
  --target fastapi \
  --priority medium \
  --assign-agent backend-team
```

**Generated Tickets**:
1. Pipeline stages (2 tickets)
2. FastAPI implementation (6 tickets)
3. Integration and testing (1 ticket)
4. All assigned to "backend-team"

### Example 3: TUI Data Dashboard

```bash
agentscript tickets create monitor_pipeline.ags \
  --target tui \
  --epic-title "Real-time Data Monitor"
```

**Generated Tickets**:
1. Pipeline stages (4 tickets)
2. TUI implementation (6 tickets)
3. Integration and testing (1 ticket)

### Example 4: Multi-Framework Comparison

Create tickets for different frameworks to compare:

```bash
# Django version
agentscript tickets create pipeline.ags --target django \
  --epic-title "Django Implementation"

# FastAPI version
agentscript tickets create pipeline.ags --target fastapi \
  --epic-title "FastAPI Implementation"

# Compare ticket counts and estimates
tickets list --epic "Django Implementation"
tickets list --epic "FastAPI Implementation"
```

## Integration with AgentScript Workflow

### Typical Workflow

1. **Write AgentScript**: Create data pipeline in AgentScript
2. **Choose Framework**: Decide on target framework (Django, FastAPI, Flask, TUI)
3. **Generate Tickets**: Create framework-specific tickets
4. **Assign to Agent**: AI agent or team member picks up tickets
5. **Implement**: Follow implementation notes in each ticket
6. **Compile**: Use AgentScript to generate code
7. **Test**: Validate generated application
8. **Deploy**: Deploy framework-specific application

### Complete Example

```bash
# Step 1: Write AgentScript
cat > data_pipeline.ags << 'EOF'
intent ProcessSalesData {
    description: "Process sales data and generate reports"
    
    pipeline: 
        source.csv("sales.csv") ->
        filter(record => record.amount > 100) ->
        sink.json("filtered_sales.json")
}
EOF

# Step 2: Generate framework-specific tickets
agentscript tickets create data_pipeline.ags \
  --target django \
  --epic-title "Sales Processing API" \
  --priority high \
  --assign-agent ai-dev

# Step 3: Agent implements tickets (automated or manual)

# Step 4: Generate Django application
agentscript compile data_pipeline.ags \
  --target django \
  --app-name sales_api \
  --database postgresql \
  --with-admin \
  --with-auth

# Step 5: Review and test generated code
cd sales_api_django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Benefits

### For Teams

- **Clear Task Breakdown**: Framework-specific tickets provide clear implementation steps
- **Consistent Practices**: Embedded best practices ensure quality
- **Easy Assignment**: Label-based filtering for framework expertise
- **Progress Tracking**: Track implementation by framework component

### For AI Agents

- **Detailed Context**: Each ticket has comprehensive implementation notes
- **Framework Guidance**: Best practices prevent common mistakes
- **Structured Work**: Clear deliverables and acceptance criteria
- **Iterative Development**: Tickets can be tackled incrementally

### For Project Management

- **Accurate Estimates**: Framework-specific tickets improve time estimates
- **Resource Planning**: Assign tasks based on framework expertise
- **Risk Management**: Identify framework-specific complexities early
- **Milestone Tracking**: Track progress by framework component

## Advanced Usage

### Custom Ticket Templates

Extend the ticket integration with custom templates:

```python
from agentscript.ticket_integration import AgentScriptTicketIntegration

class CustomTicketIntegration(AgentScriptTicketIntegration):
    def _create_framework_tickets(self, file_path, framework, epic_id, priority, assign_agent):
        # Add custom framework tasks
        tickets = super()._create_framework_tickets(
            file_path, framework, epic_id, priority, assign_agent
        )
        
        # Add custom tasks
        custom_tasks = [
            ("Custom Security Audit", "Review security implications"),
            ("Performance Optimization", "Optimize critical paths"),
        ]
        
        # Create additional tickets
        # ... implementation ...
        
        return tickets
```

### Filtering and Queries

Use repo-tickets to filter framework-specific tickets:

```bash
# Show all Django tickets
tickets list --labels django

# Show high-priority FastAPI tickets
tickets list --labels fastapi --priority high

# Show tickets assigned to AI agent
tickets list --assignee ai-dev --labels agentscript
```

### Analytics

Generate reports on framework-specific implementation:

```bash
# Ticket count by framework
tickets list --labels agentscript --format json | \
  jq '[.[] | select(.labels | contains(["django","fastapi","flask","tui"]))] | group_by(.labels[1]) | map({framework: .[0].labels[1], count: length})'

# Estimated hours by framework
tickets list --labels agentscript --format json | \
  jq '[.[] | {framework: .labels[1], hours: .estimated_hours}] | group_by(.framework) | map({framework: .[0].framework, total_hours: map(.hours) | add})'
```

## Troubleshooting

### Tickets Not Created

```bash
# Check if repo-tickets is initialized
tickets init

# Verify tickets command is available
tickets --version

# Check for error messages
agentscript tickets create pipeline.ags --target django 2>&1 | tee tickets.log
```

### Missing Framework Tickets

Ensure you're using the `--target` parameter:

```bash
# Without target: Only pipeline stage tickets
agentscript tickets create pipeline.ags

# With target: Pipeline + framework tickets
agentscript tickets create pipeline.ags --target django
```

### Duplicate Tickets

If tickets are created multiple times:

```bash
# Delete epic and all related tickets
tickets epic delete <epic-id>

# Start fresh
agentscript tickets create pipeline.ags --target django
```

## See Also

- [AgentScript Plugin System](plugins.md)
- [Configuration System](configuration.md)
- [CLI Reference](cli.md)
- [repo-tickets Documentation](https://github.com/yourusername/repo-tickets)
