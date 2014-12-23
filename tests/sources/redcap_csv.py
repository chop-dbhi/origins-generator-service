from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'redcap-csv'

    def test(self):
        path = self.input_path('redcap_demo.csv')

        client = self.module.Client(uri=path,
                                    name='REDCap Demo')
        output = client.generate()

        expected_output = self.load_output('redcap_demo_csv.json')

        self.assertProvCounts(output, expected_output)
