from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'redcap-csv'
    output_name = 'redcap_demo_csv.json'

    def generate(self):
        path = self.input_path('redcap_demo.csv')
        client = self.module.Client(uri=path, name='REDCap Demo')
        return client.generate()
