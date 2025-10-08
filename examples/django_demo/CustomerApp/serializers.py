# Django REST serializers for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags

from rest_framework import serializers
from .models import PipelineExecution

from .models import CustomeranalysisData
from .models import SalesreportData

class PipelineExecutionSerializer(serializers.ModelSerializer):
    """Serializer for pipeline execution tracking."""
    
    class Meta:
        model = PipelineExecution
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class CustomeranalysisDataSerializer(serializers.ModelSerializer):
    """Serializer for CustomerAnalysis pipeline data."""
    
    class Meta:
        model = CustomeranalysisData
        fields = '__all__'

class SalesreportDataSerializer(serializers.ModelSerializer):
    """Serializer for SalesReport pipeline data."""
    
    class Meta:
        model = SalesreportData
        fields = '__all__'
