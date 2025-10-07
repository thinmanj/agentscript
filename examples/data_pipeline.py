# This file was automatically generated from AgentScript
# Source: examples/data_pipeline.ags
# Generated at: 2025-10-07 10:06:40
#
# AgentScript is a declarative language for agentic program creation.
# The generated code follows a specific structure to maintain clarity:
#
# - Each AgentScript 'intent' becomes a Python class
# - Pipeline operations are converted to sequential pandas operations
# - Error handling is built-in with validation_errors tracking
# - Methods are well-documented with their original intent descriptions
#
# For debugging: Line numbers in comments refer to the original .ags file

# Required imports for data processing
import csv
import json
import pandas as pd

class Processuserdata:  # Source: examples/data_pipeline.ags:4
    """
        Process user data with filtering

        This class was generated from an AgentScript 'intent' declaration.
        An intent represents a high-level data processing goal that gets
        transpiled into a sequence of pandas operations.

        Structure:
        - __init__: Initializes error tracking and validation patterns
        - process_user_data: Main processing method implementing the pipeline
        - Helper methods: Utility functions for validation and transformation

        The validation_errors list collects any data validation issues
        encountered during processing for debugging and quality assurance.
        """

    def __init__(self):
        """Initialize the data processor with error tracking and validation patterns."""
        # Track validation errors during processing for debugging
        self.validation_errors = []

    def process_user_data(self, input_file: str = None, output_file: str = None):  # Source: examples/data_pipeline.ags:4
        """
        Process user data with filtering

        This method implements the AgentScript pipeline from examples/data_pipeline.ags.
        The pipeline is executed as a series of pandas operations in sequence:

        1. Load data from CSV file
        2. Filter data based on conditions
        3. Save data to JSON file

        Args:
            input_file (str, optional): Override default input file
            output_file (str, optional): Override default output file

        Returns:
            pd.DataFrame: The processed dataset

        Raises:
            Exception: Re-raises any processing errors after logging to validation_errors
        """

        # Execute AgentScript pipeline as sequential pandas operations
        try:
            # Stage 1: Data input  # Source: examples/data_pipeline.ags:7
            df = pd.read_csv("users.csv")

            # Stage 2: Data filtering  # Source: examples/data_pipeline.ags:7
            df = df.query('age >= 18')  # Filter: user => age >= 18

            # Stage 3: Data output  # Source: examples/data_pipeline.ags:8
            df.to_json("processed_users.json", orient='records', indent=2)

            # Pipeline execution completed successfully
            return df

        except Exception as e:
            # Log error for debugging while preserving original exception
            error_info = {
                'error': str(e),
                'error_type': type(e).__name__,
                'method': 'process_user_data',
                'source_file': 'examples/data_pipeline.ags'
            }
            self.validation_errors.append(error_info)
            raise  # Re-raise for proper error handling

    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern.
    
        This method provides email validation for data quality assurance.
        It uses a standard regex pattern that covers most common email formats.
    
        Args:
            email (str): Email address to validate
        
        Returns:
            bool: True if email format is valid, False otherwise
        
        Note:
            This validation is for format checking only and doesn't verify
            if the email address actually exists or is deliverable.
        """
        if not email:
            return False
        return bool(self.email_pattern.match(email))

class Simpleaggregation:  # Source: examples/data_pipeline.ags:12
    """
        Simple data aggregation example

        This class was generated from an AgentScript 'intent' declaration.
        An intent represents a high-level data processing goal that gets
        transpiled into a sequence of pandas operations.

        Structure:
        - __init__: Initializes error tracking and validation patterns
        - simple_aggregation: Main processing method implementing the pipeline
        - Helper methods: Utility functions for validation and transformation

        The validation_errors list collects any data validation issues
        encountered during processing for debugging and quality assurance.
        """

    def __init__(self):
        """Initialize the data processor with error tracking and validation patterns."""
        # Track validation errors during processing for debugging
        self.validation_errors = []

    def simple_aggregation(self, input_file: str = None, output_file: str = None):  # Source: examples/data_pipeline.ags:12
        """
        Simple data aggregation example

        This method implements the AgentScript pipeline from examples/data_pipeline.ags.
        The pipeline is executed as a series of pandas operations in sequence:

        1. Load data from CSV file
        2. Filter data based on conditions
        3. Save data to CSV file

        Args:
            input_file (str, optional): Override default input file
            output_file (str, optional): Override default output file

        Returns:
            pd.DataFrame: The processed dataset

        Raises:
            Exception: Re-raises any processing errors after logging to validation_errors
        """

        # Execute AgentScript pipeline as sequential pandas operations
        try:
            # Stage 1: Data input  # Source: examples/data_pipeline.ags:15
            df = pd.read_csv("sales.csv")

            # Stage 2: Data filtering  # Source: examples/data_pipeline.ags:15
            df = df.query('amount > 100')  # Filter: record => amount > 100

            # Stage 3: Data output  # Source: examples/data_pipeline.ags:16
            df.to_csv("high_value_sales.csv", index=False)

            # Pipeline execution completed successfully
            return df

        except Exception as e:
            # Log error for debugging while preserving original exception
            error_info = {
                'error': str(e),
                'error_type': type(e).__name__,
                'method': 'simple_aggregation',
                'source_file': 'examples/data_pipeline.ags'
            }
            self.validation_errors.append(error_info)
            raise  # Re-raise for proper error handling

    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern.
    
        This method provides email validation for data quality assurance.
        It uses a standard regex pattern that covers most common email formats.
    
        Args:
            email (str): Email address to validate
        
        Returns:
            bool: True if email format is valid, False otherwise
        
        Note:
            This validation is for format checking only and doesn't verify
            if the email address actually exists or is deliverable.
        """
        if not email:
            return False
        return bool(self.email_pattern.match(email))
