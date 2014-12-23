import responses
from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'redcap-api'

    @responses.activate
    def test(self):
        url = 'http://redcap-api.org'
        token = 'abc123'
        name = 'Test'

        with open(self.input_path('redcap_api.json')) as f:
            responses.add(responses.POST,
                          url=url,
                          status=200,
                          body=f.read())

        client = self.module.Client(url=url,
                                    token=token,
                                    name=name)
        output = client.generate()

        expected_output = self.load_output('redcap_api.json')

        self.assertProvCounts(output, expected_output)
