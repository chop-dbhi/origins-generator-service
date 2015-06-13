import os
import unittest
from .base import SourceTestCase


HOST = os.environ.get('ORACLE_HOST', 'localhost')
USER = os.environ.get('ORACLE_USER', '')
PASSWORD = os.environ.get('ORACLE_PASSWORD', '')


@unittest.skip
class TestCase(SourceTestCase):
    generator = 'oracle'
    output_name = 'chinook_oracle.json'

    def generate(self):
        client = self.module.Client(database='chinook',
                                    host=HOST,
                                    user=USER,
                                    password=PASSWORD)

        return client.generate()
