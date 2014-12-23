import responses
from .base import SourceTestCase


class TestCase(SourceTestCase):
    maxDiff = None
    generator = 'harvest'

    @responses.activate
    def test(self):
        url = 'http://harvest.research.chop.edu/demo/api/'
        concepts_url = 'http://harvest.research.chop.edu/demo/api/concepts/'

        # Mock API root and concepts
        with open(self.input_path('harvest_api.json')) as f:
            responses.add(responses.GET,
                          url=url,
                          status=200,
                          body=f.read(),
                          content_type='application/json')

        with open(self.input_path('harvest_api_concepts.json')) as f:
            responses.add(responses.GET,
                          url=concepts_url,
                          status=200,
                          body=f.read(),
                          content_type='application/json')

        client = self.module.Client(url=url)
        output = client.generate()

        expected_output = self.load_output('harvest_openmrs.json')

        self.assertProvCounts(output, expected_output)
