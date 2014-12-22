from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'sqlite'

    def test(self):
        path = self.input_path('chinook.sqlite')

        client = self.module.Client(uri=path)
        output = client.generate()

        expected_output = self.load_output('chinook_sqlite.json')

        self.assertEqual(output, expected_output)

