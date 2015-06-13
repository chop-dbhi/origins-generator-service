from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'git'
    output_name = 'origins_docker_git.json'

    def generate(self):
        path = self.input_path('origins-docker')
        client = self.module.Client(uri=path, branch='master')
        return client.generate()
