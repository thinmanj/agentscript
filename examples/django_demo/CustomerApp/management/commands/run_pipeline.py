# Django management command for CustomerApp
# Generated from AgentScript source: sample_pipeline.ags

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from CustomerApp.models import PipelineExecution

class Command(BaseCommand):
    help = 'Run AgentScript data pipeline'

    def add_arguments(self, parser):
        parser.add_argument('intent', type=str, help='Intent name to execute')
        parser.add_argument('--input', type=str, help='Input file path')
        parser.add_argument('--output', type=str, help='Output file path')
        parser.add_argument('--user', type=str, help='Username for tracking')

    def handle(self, *args, **options):
        intent_name = options['intent']
        input_file = options.get('input', '')
        output_file = options.get('output', '')
        username = options.get('user')

        # Get user for tracking
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User {username} not found'))

        # Create execution record
        execution = PipelineExecution.objects.create(
            intent_name=intent_name,
            input_file=input_file,
            output_file=output_file,
            created_by=user
        )

        try:
            # Execute pipeline (implementation would go here)
            self.stdout.write(self.style.SUCCESS(f'Pipeline {intent_name} started with execution ID {execution.id}'))

        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            raise CommandError(f'Pipeline execution failed: {e}')