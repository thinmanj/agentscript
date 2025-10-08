# Django admin configuration for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags

from django.contrib import admin
from .models import PipelineExecution
from .models import CustomeranalysisData
from .models import SalesreportData

@admin.register(PipelineExecution)
class PipelineExecutionAdmin(admin.ModelAdmin):
    list_display = ('intent_name', 'status', 'records_processed', 'created_at', 'created_by')
    list_filter = ('status', 'intent_name', 'created_at')
    search_fields = ('intent_name', 'input_file', 'output_file')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(CustomeranalysisData)
class CustomeranalysisDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'execution', 'created_at')
    list_filter = ('execution__intent_name', 'created_at')
    search_fields = ('execution__intent_name',)

@admin.register(SalesreportData)
class SalesreportDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'execution', 'created_at')
    list_filter = ('execution__intent_name', 'created_at')
    search_fields = ('execution__intent_name',)
