from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'filesystem'

    def test(self):
        path = self.input_path('filesystem')

        client = self.module.Client(path=path)
        output = client.generate()

        expected_output = self.load_output('filesystem.json')

        self.assertProvCounts(output, expected_output)
