# Django models for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags
# Generated at: 2025-10-07 22:18:35

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class PipelineExecution(models.Model):
    """Track pipeline execution runs."""
    intent_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    input_file = models.CharField(max_length=255, blank=True)
    output_file = models.CharField(max_length=255, blank=True)
    records_processed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.intent_name} - {self.status} ({self.created_at})'

class CustomeranalysisData(models.Model):
    """Data model for CustomerAnalysis pipeline."""
    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='data')
    data = models.TextField(blank=True)
    source_row = models.IntegerField(null=True, blank=True)
    source_file = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CustomerApp_customeranalysis_data'

    def __str__(self):
        return f'{self.execution.intent_name} - Record {self.id}'

class SalesreportData(models.Model):
    """Data model for SalesReport pipeline."""
    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='data')
    data = models.TextField(blank=True)
    source_row = models.IntegerField(null=True, blank=True)
    source_file = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CustomerApp_salesreport_data'

    def __str__(self):
        return f'{self.execution.intent_name} - Record {self.id}'
