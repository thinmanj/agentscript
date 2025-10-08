# Django settings additions for CustomerApp
# Add these to your main Django settings.py file

# Add to INSTALLED_APPS:
INSTALLED_APPS = [
    # ... existing apps ...
    'CustomerApp',
    'rest_framework',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
