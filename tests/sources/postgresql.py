import os
from .base import SourceTestCase


HOST = os.environ.get('POSTGRESQL_HOST', 'localhost')
USER = os.environ.get('POSTGRESQL_USER', '')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD', '')


class TestCase(SourceTestCase):
    generator = 'postgresql'
    output_name = 'chinook_postgresql.json'

    def generate(self):
        client = self.module.Client(database='chinook',
                                    host=HOST,
                                    user=USER,
                                    password=PASSWORD)

        return client.generate()
