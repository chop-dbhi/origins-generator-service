from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'harvest'

    def test(self):
        client = self.module.Client(url='http://harvest.research.chop.edu/demo/api/')
        output = client.generate()

        expected_output = self.load_output('harvest_openmrs.json')

        self.assertEqual(output, expected_output)
