import csv
import pandas as pd

class Simpleprocessor:
    """Simple data processor"""

    def __init__(self):
        self.validation_errors = []

    def simple_processor(self, input_file: str = None, output_file: str = None):
        """Simple data processor"""

        # Process data through pipeline
        try:
            # Load data
            df = pd.read_csv("input.csv")

            return df
        except Exception as e:
            self.validation_errors.append({'error': str(e)})
            raise

    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern."""
        return bool(self.email_pattern.match(email)) if email else False
