import os
import unittest
from .base import SourceTestCase


HOST = os.environ.get('REDCAP_MYSQL_HOST')
PORT = os.environ.get('REDCAP_MYSQL_PORT', 3306)
USER = os.environ.get('REDCAP_MYSQL_USER')
PASSWORD = os.environ.get('REDCAP_MYSQL_PASSWORD')


@unittest.skipUnless(HOST, 'connection settings not available')
class TestCase(SourceTestCase):
    generator = 'redcap-mysql'

    def test(self):
        client = self.module.Client(host=HOST,
                                    port=PORT,
                                    user=USER,
                                    password=PASSWORD,
                                    project='redcap_demo')

        output = client.generate()

        expected_output = self.load_output('redcap_mysql.json')

        self.assertEqual(output, expected_output)
