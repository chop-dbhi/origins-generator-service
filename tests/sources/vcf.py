from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'vcf'

    def test(self):
        path = self.input_path('sample.vcf')

        client = self.module.Client(uri=path)
        output = client.generate()

        expected_output = self.load_output('sample_vcf.json')

        self.assertProvCounts(output, expected_output)
