# URL configuration for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create REST API router
router = DefaultRouter()
router.register(r'executions', views.PipelineExecutionViewSet)
router.register(r'customer_analysis-data', views.CustomeranalysisDataViewSet)
router.register(r'sales_report-data', views.SalesreportDataViewSet)

app_name = 'data_pipeline'

urlpatterns = [
    path('api/', include(router.urls)),
]