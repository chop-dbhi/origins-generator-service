import responses
from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'harvest'
    output_name = 'harvest_openmrs.json'

    @responses.activate
    def generate(self):
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

        return client.generate()
