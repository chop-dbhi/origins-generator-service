from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'filesystem'

    def test(self):
        path = self.input_path('filesystem')

        client = self.module.Client(path=path)
        output = client.generate()

        expected_output = self.load_output('filesystem.csv')

        self.assertCorrectOutput(output, expected_output)
