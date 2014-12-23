from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'entities-csv'

    def test(self):
        path = self.input_path('entities.csv')

        client = self.module.Client(uri=path)
        output = client.generate()

        expected_output = self.load_output('entities_csv.json')
        self.assertProvCounts(output, expected_output)
