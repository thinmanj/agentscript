# Django views for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd
import json
import traceback

from .models import PipelineExecution
from .serializers import PipelineExecutionSerializer
from .models import CustomeranalysisData
from .serializers import CustomeranalysisDataSerializer
from .models import SalesreportData
from .serializers import SalesreportDataSerializer

# Import generated pipeline processors
import sys
from pathlib import Path

class PipelineExecutionViewSet(viewsets.ModelViewSet):
    """API ViewSet for pipeline execution management."""
    queryset = PipelineExecution.objects.all()
    serializer_class = PipelineExecutionSerializer

    @action(detail=True, methods=['post'])
    def run_pipeline(self, request, pk=None):
        """Execute a specific pipeline."""
        execution = self.get_object()
        
        try:
            # Update status to running
            execution.status = 'running'
            execution.save()
            
            # Execute the pipeline based on intent
            result = self._execute_pipeline(execution)
            
            # Update status to completed
            execution.status = 'completed'
            execution.records_processed = result.get('records_processed', 0)
            execution.save()
            
            return Response({
                'status': 'completed',
                'records_processed': execution.records_processed
            })
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            
            return Response({
                'status': 'failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _execute_pipeline(self, execution):
        """Execute pipeline based on intent name."""
        # This would import and run the generated pipeline code
        # Implementation depends on how pipelines are structured
        return {'records_processed': 0}

class CustomeranalysisDataViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for CustomerAnalysis pipeline data."""
    queryset = CustomeranalysisData.objects.all()
    serializer_class = CustomeranalysisDataSerializer

class SalesreportDataViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for SalesReport pipeline data."""
    queryset = SalesreportData.objects.all()
    serializer_class = SalesreportDataSerializer
