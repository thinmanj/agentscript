import csv
import json
import pandas as pd

class Processuserdata:
    """Process user data with filtering"""

    def __init__(self):
        self.validation_errors = []

    def process_user_data(self, input_file: str = None, output_file: str = None):
        """Process user data with filtering"""

        # Process data through pipeline
        try:
            # Load data
            df = pd.read_csv("users.csv")
            df = df.query('age >= 18')
            df.to_json("processed_users.json", orient='records', indent=2)

            return df
        except Exception as e:
            self.validation_errors.append({'error': str(e)})
            raise

    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern."""
        return bool(self.email_pattern.match(email)) if email else False

class Simpleaggregation:
    """Simple data aggregation example"""

    def __init__(self):
        self.validation_errors = []

    def simple_aggregation(self, input_file: str = None, output_file: str = None):
        """Simple data aggregation example"""

        # Process data through pipeline
        try:
            # Load data
            df = pd.read_csv("sales.csv")
            df = df.query('amount > 100')
            df.to_csv("high_value_sales.csv", index=False)

            return df
        except Exception as e:
            self.validation_errors.append({'error': str(e)})
            raise

    def is_valid_email(self, email: str) -> bool:
        """Validate email format using regex pattern."""
        return bool(self.email_pattern.match(email)) if email else False
