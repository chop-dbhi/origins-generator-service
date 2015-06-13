from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'sqlite'
    output_name = 'chinook_sqlite.json'

    def generate(self):
        path = self.input_path('chinook.sqlite')
        client = self.module.Client(uri=path)
        return client.generate()
