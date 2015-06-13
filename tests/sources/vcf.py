from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'vcf'
    output_name = 'sample_vcf.json'

    def generate(self):
        path = self.input_path('sample.vcf')
        client = self.module.Client(uri=path)
        return client.generate()
