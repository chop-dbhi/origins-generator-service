from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'datadict'

    def test(self):
        path = self.input_path('chinook_tracks_datadict.csv')

        client = self.module.Client(uri=path)
        output = client.generate()

        expected_output = self.load_output('chinook_tracks_datadict_csv.csv')

        self.assertCorrectOutput(output, expected_output)
