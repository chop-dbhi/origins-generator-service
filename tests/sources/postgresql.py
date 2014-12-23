import os
from .base import SourceTestCase


HOST = os.environ.get('POSTGRESQL_HOST', 'localhost')
USER = os.environ.get('POSTGRESQL_USER', '')
PASSWORD = os.environ.get('POSTGRESQL_PASSWORD', '')


class TestCase(SourceTestCase):
    generator = 'postgresql'

    def test(self):
        client = self.module.Client(database='chinook',
                                    host=HOST,
                                    user=USER,
                                    password=PASSWORD)
        output = client.generate()

        expected_output = self.load_output('chinook_postgresql.json')

        self.assertProvCounts(output, expected_output)
