import os
from .base import SourceTestCase


HOST = os.environ.get('MONGODB_HOST', 'localhost')
PORT = os.environ.get('MONGODB_PORT', 27017)


class TestCase(SourceTestCase):
    generator = 'mongodb'
    output_name = 'chinook_mongodb.json'

    def generate(self):
        client = self.module.Client(database='chinook', host=HOST, port=PORT)
        return client.generate()
