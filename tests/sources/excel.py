from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'excel'

    def test(self):
        uri = self.input_path('chinook.xlsx')

        client = self.module.Client(uri=uri)
        output = client.generate()

        expected_output = self.load_output('chinook_xlsx.json')
        self.assertProvCounts(output, expected_output)
