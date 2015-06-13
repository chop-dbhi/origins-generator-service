from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'filesystem'
    output_name = 'filesystem.json'

    def generate(self):
        path = self.input_path('filesystem')
        client = self.module.Client(path=path)
        return client.generate()
