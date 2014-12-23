import responses
from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'github-issues'

    @responses.activate
    def test(self):
        url = self.module.GITHUB_V3_ISSUES_URL\
            .format(owner='chop-dbhi', repo='origins')

        with open(self.input_path('origins_issues.json')) as f:
            responses.add(responses.GET,
                          url=url,
                          status=200,
                          body=f.read(),
                          content_type=self.module.GITHUB_V3_ACCEPT_MIMETYPE)

        client = self.module.Client(owner='chop-dbhi', repo='origins')
        output = client.generate()

        expected_output = self.load_output('origins_issues.json')
        self.assertProvCounts(output, expected_output)
