from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'git'

    def test(self):
        path = self.input_path('origins-docker')

        client = self.module.Client(uri=path, branch='master')
        output = client.generate()

        expected_output = self.load_output('origins_docker_git.json')

        self.assertProvCounts(output, expected_output)
