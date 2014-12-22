import os
from .base import SourceTestCase


HOST = os.environ.get('MYSQL_HOST', 'localhost')
USER = os.environ.get('MYSQL_USER', '')
PASSWORD = os.environ.get('MYSQL_PASSWORD', '')


class TestCase(SourceTestCase):
    generator = 'mysql'

    def test(self):
        client = self.module.Client(database='chinook',
                                    host=HOST,
                                    user=USER,
                                    password=PASSWORD)
        output = client.generate()

        expected_output = self.load_output('chinook_mysql.json')

        self.assertEqual(output, expected_output)
