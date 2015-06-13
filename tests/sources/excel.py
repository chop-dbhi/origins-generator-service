from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'excel'
    output_name = 'chinook_xlsx.json'

    def generate(self):
        uri = self.input_path('chinook.xlsx')
        client = self.module.Client(uri=uri)
        return client.generate()
