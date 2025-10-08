"""
Django Plugin for AgentScript

This plugin generates Django web applications from AgentScript pipeline definitions.
It creates Django models, serializers, views, and URLs for data processing pipelines
with built-in admin interface and REST API endpoints.
"""

from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .base import BasePlugin, GenerationContext, PluginConfig
from ..ast_nodes import Program, IntentDeclaration, PipelineStage, FunctionCall, AttributeAccess, Literal


class DjangoPlugin(BasePlugin):
    """Django web framework code generator."""
    
    plugin_name = "django"
    plugin_description = "Generate Django web applications with models, views, and APIs"
    plugin_version = "1.0.0"
    plugin_dependencies = ["django>=4.0", "djangorestframework>=3.14"]
    plugin_optional_dependencies = ["django-cors-headers", "django-filter", "celery"]
    plugin_output_extension = ".py"
    plugin_supports_async = True
    plugin_supports_web = True
    plugin_supports_database = True
    plugin_supports_auth = True
    
    @property
    def name(self) -> str:
        return "django"
    
    @property
    def description(self) -> str:
        return "Generate Django web applications with models, views, and REST APIs"
    
    def generate_code(self, ast: Program, context: GenerationContext) -> Dict[str, str]:
        """Generate Django application code from AgentScript AST."""
        files = {}
        
        # Extract intents from AST
        intents = [stmt for stmt in ast.statements if isinstance(stmt, IntentDeclaration)]
        
        if not intents:
            return files
        
        # Generate Django app structure
        app_name = context.options.get('app_name', 'data_pipeline')
        
        # Generate models.py
        files[f"{app_name}/models.py"] = self._generate_models_file(intents, context, app_name)
        
        # Generate serializers.py
        files[f"{app_name}/serializers.py"] = self._generate_serializers_file(intents, context, app_name)
        
        # Generate views.py
        files[f"{app_name}/views.py"] = self._generate_views_file(intents, context, app_name)
        
        # Generate urls.py
        files[f"{app_name}/urls.py"] = self._generate_urls_file(intents, context, app_name)
        
        # Generate admin.py
        files[f"{app_name}/admin.py"] = self._generate_admin_file(intents, context, app_name)
        
        # Generate apps.py
        files[f"{app_name}/apps.py"] = self._generate_apps_file(context, app_name)
        
        # Generate __init__.py
        files[f"{app_name}/__init__.py"] = ""
        
        # Generate management commands
        files[f"{app_name}/management/__init__.py"] = ""
        files[f"{app_name}/management/commands/__init__.py"] = ""
        files[f"{app_name}/management/commands/run_pipeline.py"] = self._generate_management_command(intents, context, app_name)
        
        # Generate settings additions
        files["settings_additions.py"] = self._generate_settings_additions(context, app_name)
        
        # Generate requirements.txt
        files["requirements.txt"] = self._generate_requirements(context)
        
        return files
    
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """Get required dependencies for Django project."""
        deps = self.plugin_dependencies.copy()
        
        # Add database dependencies based on options
        database = context.options.get('database', 'sqlite')
        if database == 'postgresql':
            deps.append('psycopg2-binary>=2.9')
        elif database == 'mysql':
            deps.append('mysqlclient>=2.1')
        
        # Add optional dependencies if enabled
        if context.options.get('cors', False):
            deps.append('django-cors-headers>=3.13')
        
        if context.options.get('celery', False):
            deps.extend(['celery>=5.2', 'redis>=4.3'])
        
        if context.options.get('admin_theme', False):
            deps.append('django-admin-interface>=0.19')
        
        return deps
    
    def _generate_models_file(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django models.py file."""
        lines = [
            f"# Django models for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "from django.db import models",
            "from django.contrib.auth.models import User",
            "from django.utils import timezone",
            "import json",
            "",
        ]
        
        # Generate base pipeline execution model
        lines.extend([
            "class PipelineExecution(models.Model):",
            '    """Track pipeline execution runs."""',
            "    intent_name = models.CharField(max_length=100)",
            "    status = models.CharField(max_length=20, choices=[",
            "        ('pending', 'Pending'),",
            "        ('running', 'Running'),",
            "        ('completed', 'Completed'),",
            "        ('failed', 'Failed'),",
            "    ], default='pending')",
            "    input_file = models.CharField(max_length=255, blank=True)",
            "    output_file = models.CharField(max_length=255, blank=True)",
            "    records_processed = models.IntegerField(default=0)",
            "    error_message = models.TextField(blank=True)",
            "    created_at = models.DateTimeField(auto_now_add=True)",
            "    updated_at = models.DateTimeField(auto_now=True)",
            "    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)",
            "",
            "    class Meta:",
            "        ordering = ['-created_at']",
            "",
            "    def __str__(self):",
            "        return f'{self.intent_name} - {self.status} ({self.created_at})'",
            "",
        ])
        
        # Generate data models based on pipeline analysis
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"class {model_name}Data(models.Model):",
                f'    """Data model for {intent.name} pipeline."""',
                "    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='data')",
            ])
            
            # Analyze pipeline to determine fields
            if intent.pipeline:
                fields = self._extract_data_fields(intent.pipeline.stages)
                for field_name, field_type in fields.items():
                    django_field = self._get_django_field(field_type)
                    lines.append(f"    {field_name} = {django_field}")
            
            lines.extend([
                "    created_at = models.DateTimeField(auto_now_add=True)",
                "",
                "    class Meta:",
                f"        db_table = '{app_name}_{model_name.lower()}_data'",
                "",
                "    def __str__(self):",
                "        return f'{self.execution.intent_name} - Record {self.id}'",
                "",
            ])
        
        return "\n".join(lines)
    
    def _generate_serializers_file(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django REST serializers."""
        lines = [
            f"# Django REST serializers for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from rest_framework import serializers",
            f"from .models import PipelineExecution",
            "",
        ]
        
        # Import data models
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.append(f"from .models import {model_name}Data")
        
        lines.append("")
        
        # Generate base serializers
        lines.extend([
            "class PipelineExecutionSerializer(serializers.ModelSerializer):",
            '    """Serializer for pipeline execution tracking."""',
            "    ",
            "    class Meta:",
            "        model = PipelineExecution",
            "        fields = '__all__'",
            "        read_only_fields = ('created_at', 'updated_at')",
            "",
        ])
        
        # Generate data serializers
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"class {model_name}DataSerializer(serializers.ModelSerializer):",
                f'    """Serializer for {intent.name} pipeline data."""',
                "    ",
                "    class Meta:",
                f"        model = {model_name}Data",
                "        fields = '__all__'",
                "",
            ])
        
        return "\n".join(lines)
    
    def _generate_views_file(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django views with REST API endpoints."""
        lines = [
            f"# Django views for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from django.shortcuts import render, get_object_or_404",
            "from django.http import JsonResponse",
            "from django.views.decorators.csrf import csrf_exempt",
            "from django.utils.decorators import method_decorator",
            "from rest_framework import viewsets, status",
            "from rest_framework.decorators import action",
            "from rest_framework.response import Response",
            "import pandas as pd",
            "import json",
            "import traceback",
            "",
            f"from .models import PipelineExecution",
            f"from .serializers import PipelineExecutionSerializer",
        ]
        
        # Import data models and serializers
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"from .models import {model_name}Data",
                f"from .serializers import {model_name}DataSerializer",
            ])
        
        lines.extend([
            "",
            "# Import generated pipeline processors",
            "import sys",
            "from pathlib import Path",
            "",
        ])
        
        # Generate ViewSets
        lines.extend([
            "class PipelineExecutionViewSet(viewsets.ModelViewSet):",
            '    """API ViewSet for pipeline execution management."""',
            "    queryset = PipelineExecution.objects.all()",
            "    serializer_class = PipelineExecutionSerializer",
            "",
            "    @action(detail=True, methods=['post'])",
            "    def run_pipeline(self, request, pk=None):",
            '        """Execute a specific pipeline."""',
            "        execution = self.get_object()",
            "        ",
            "        try:",
            "            # Update status to running",
            "            execution.status = 'running'",
            "            execution.save()",
            "            ",
            "            # Execute the pipeline based on intent",
            f"            result = self._execute_pipeline(execution)",
            "            ",
            "            # Update status to completed",
            "            execution.status = 'completed'",
            "            execution.records_processed = result.get('records_processed', 0)",
            "            execution.save()",
            "            ",
            "            return Response({",
            "                'status': 'completed',",
            "                'records_processed': execution.records_processed",
            "            })",
            "            ",
            "        except Exception as e:",
            "            execution.status = 'failed'",
            "            execution.error_message = str(e)",
            "            execution.save()",
            "            ",
            "            return Response({",
            "                'status': 'failed',",
            "                'error': str(e)",
            "            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)",
            "",
            "    def _execute_pipeline(self, execution):",
            '        """Execute pipeline based on intent name."""',
            "        # This would import and run the generated pipeline code",
            "        # Implementation depends on how pipelines are structured",
            "        return {'records_processed': 0}",
            "",
        ])
        
        # Generate data ViewSets
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"class {model_name}DataViewSet(viewsets.ReadOnlyModelViewSet):",
                f'    """API ViewSet for {intent.name} pipeline data."""',
                f"    queryset = {model_name}Data.objects.all()",
                f"    serializer_class = {model_name}DataSerializer",
                "",
            ])
        
        return "\n".join(lines)
    
    def _generate_urls_file(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django URLs configuration."""
        lines = [
            f"# URL configuration for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from django.urls import path, include",
            "from rest_framework.routers import DefaultRouter",
            "from . import views",
            "",
            "# Create REST API router",
            "router = DefaultRouter()",
            "router.register(r'executions', views.PipelineExecutionViewSet)",
        ]
        
        # Register data ViewSets
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            endpoint = self._to_snake_case(intent.name)
            lines.append(f"router.register(r'{endpoint}-data', views.{model_name}DataViewSet)")
        
        lines.extend([
            "",
            "app_name = 'data_pipeline'",
            "",
            "urlpatterns = [",
            "    path('api/', include(router.urls)),",
            "]",
        ])
        
        return "\n".join(lines)
    
    def _generate_admin_file(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django admin configuration."""
        lines = [
            f"# Django admin configuration for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from django.contrib import admin",
            f"from .models import PipelineExecution",
        ]
        
        # Import data models
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.append(f"from .models import {model_name}Data")
        
        lines.extend([
            "",
            "@admin.register(PipelineExecution)",
            "class PipelineExecutionAdmin(admin.ModelAdmin):",
            "    list_display = ('intent_name', 'status', 'records_processed', 'created_at', 'created_by')",
            "    list_filter = ('status', 'intent_name', 'created_at')",
            "    search_fields = ('intent_name', 'input_file', 'output_file')",
            "    readonly_fields = ('created_at', 'updated_at')",
            "    ",
            "    def get_queryset(self, request):",
            "        return super().get_queryset(request).select_related('created_by')",
            "",
        ])
        
        # Register data models
        for intent in intents:
            model_name = self._to_class_name(intent.name)
            lines.extend([
                f"@admin.register({model_name}Data)",
                f"class {model_name}DataAdmin(admin.ModelAdmin):",
                "    list_display = ('id', 'execution', 'created_at')",
                "    list_filter = ('execution__intent_name', 'created_at')",
                "    search_fields = ('execution__intent_name',)",
                "",
            ])
        
        return "\n".join(lines)
    
    def _generate_apps_file(self, context: GenerationContext, app_name: str) -> str:
        """Generate Django apps.py configuration."""
        return f"""# Django app configuration for {app_name}
# Generated from AgentScript source: {context.source_file.name}

from django.apps import AppConfig


class {self._to_class_name(app_name)}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_name.replace("_", " ").title()}'
"""
    
    def _generate_management_command(self, intents: List[IntentDeclaration], context: GenerationContext, app_name: str) -> str:
        """Generate Django management command for running pipelines."""
        lines = [
            f"# Django management command for {app_name}",
            f"# Generated from AgentScript source: {context.source_file.name}",
            "",
            "from django.core.management.base import BaseCommand, CommandError",
            "from django.contrib.auth.models import User",
            f"from {app_name}.models import PipelineExecution",
            "",
            "class Command(BaseCommand):",
            "    help = 'Run AgentScript data pipeline'",
            "",
            "    def add_arguments(self, parser):",
            "        parser.add_argument('intent', type=str, help='Intent name to execute')",
            "        parser.add_argument('--input', type=str, help='Input file path')",
            "        parser.add_argument('--output', type=str, help='Output file path')",
            "        parser.add_argument('--user', type=str, help='Username for tracking')",
            "",
            "    def handle(self, *args, **options):",
            "        intent_name = options['intent']",
            "        input_file = options.get('input', '')",
            "        output_file = options.get('output', '')",
            "        username = options.get('user')",
            "",
            "        # Get user for tracking",
            "        user = None",
            "        if username:",
            "            try:",
            "                user = User.objects.get(username=username)",
            "            except User.DoesNotExist:",
            "                self.stdout.write(self.style.WARNING(f'User {username} not found'))",
            "",
            "        # Create execution record",
            "        execution = PipelineExecution.objects.create(",
            "            intent_name=intent_name,",
            "            input_file=input_file,",
            "            output_file=output_file,",
            "            created_by=user",
            "        )",
            "",
            "        try:",
            "            # Execute pipeline (implementation would go here)",
            "            self.stdout.write(self.style.SUCCESS(f'Pipeline {intent_name} started with execution ID {execution.id}'))",
            "",
            "        except Exception as e:",
            "            execution.status = 'failed'",
            "            execution.error_message = str(e)",
            "            execution.save()",
            "            raise CommandError(f'Pipeline execution failed: {e}')",
        ]
        
        return "\n".join(lines)
    
    def _generate_settings_additions(self, context: GenerationContext, app_name: str) -> str:
        """Generate Django settings additions."""
        lines = [
            f"# Django settings additions for {app_name}",
            f"# Add these to your main Django settings.py file",
            "",
            "# Add to INSTALLED_APPS:",
            "INSTALLED_APPS = [",
            "    # ... existing apps ...",
            f"    '{app_name}',",
            "    'rest_framework',",
        ]
        
        if context.options.get('cors', False):
            lines.append("    'corsheaders',")
        
        lines.extend([
            "]",
            "",
            "# REST Framework configuration",
            "REST_FRAMEWORK = {",
            "    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',",
            "    'PAGE_SIZE': 50,",
            "    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],",
            "}",
            "",
        ])
        
        if context.options.get('cors', False):
            lines.extend([
                "# CORS configuration",
                "CORS_ALLOWED_ORIGINS = [",
                "    'http://localhost:3000',  # React development server",
                "    'http://127.0.0.1:3000',",
                "]",
                "",
            ])
        
        # Database configuration
        database = context.options.get('database', 'sqlite')
        if database == 'postgresql':
            lines.extend([
                "# PostgreSQL database configuration",
                "DATABASES = {",
                "    'default': {",
                "        'ENGINE': 'django.db.backends.postgresql',",
                "        'NAME': 'your_database_name',",
                "        'USER': 'your_database_user',",
                "        'PASSWORD': 'your_database_password',",
                "        'HOST': 'localhost',",
                "        'PORT': '5432',",
                "    }",
                "}",
                "",
            ])
        elif database == 'mysql':
            lines.extend([
                "# MySQL database configuration",
                "DATABASES = {",
                "    'default': {",
                "        'ENGINE': 'django.db.backends.mysql',",
                "        'NAME': 'your_database_name',",
                "        'USER': 'your_database_user',",
                "        'PASSWORD': 'your_database_password',",
                "        'HOST': 'localhost',",
                "        'PORT': '3306',",
                "    }",
                "}",
                "",
            ])
        
        return "\n".join(lines)
    
    def _generate_requirements(self, context: GenerationContext) -> str:
        """Generate requirements.txt file."""
        deps = self.get_dependencies(context)
        return "\n".join(deps) + "\n"
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        return "".join(word.capitalize() for word in name.replace("_", " ").split())
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _extract_data_fields(self, stages: List[PipelineStage]) -> Dict[str, str]:
        """Extract data fields from pipeline stages."""
        fields = {}
        
        # Default fields that most data will have
        fields['data'] = 'text'  # JSON field for actual data
        fields['source_row'] = 'integer'  # Original row number
        
        # Analyze stages to infer additional fields
        for stage in stages:
            if isinstance(stage.operation, FunctionCall):
                if isinstance(stage.operation.function, AttributeAccess):
                    if stage.operation.function.attribute in ['csv', 'json']:
                        # File-based source, add filename tracking
                        fields['source_file'] = 'text'
        
        return fields
    
    def _get_django_field(self, field_type: str) -> str:
        """Convert field type to Django field specification."""
        field_map = {
            'text': 'models.TextField(blank=True)',
            'integer': 'models.IntegerField(null=True, blank=True)',
            'float': 'models.FloatField(null=True, blank=True)',
            'boolean': 'models.BooleanField(default=False)',
            'datetime': 'models.DateTimeField(null=True, blank=True)',
            'json': 'models.JSONField(default=dict)',
        }
        return field_map.get(field_type, 'models.TextField(blank=True)')