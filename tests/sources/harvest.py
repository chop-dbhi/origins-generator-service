import responses
from .base import SourceTestCase


class TestCase(SourceTestCase):
    maxDiff = None
    generator = 'harvest'

    @responses.activate
    def test(self):
        # Mock API root and concepts
        with open(self.input_path('harvest_api.json')) as f:
            responses.add(responses.GET,
                          url='http://harvest.research.chop.edu/demo/api/',
                          status=200,
                          body=f.read(),
                          content_type='application/json')

        with open(self.input_path('harvest_api_concepts.json')) as f:
            responses.add(responses.GET,
                          url='http://harvest.research.chop.edu/demo/api/concepts/',
                          status=200,
                          body=f.read(),
                          content_type='application/json')

        client = self.module.Client(url='http://harvest.research.chop.edu/demo/api/')
        output = client.generate()

        expected_output = self.load_output('harvest_openmrs.json')

        self.assertEqual(output, expected_output)
