from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'delimited'

    def test(self):
        path = self.input_path('chinook_tracks.csv')

        client = self.module.Client(uri=path)
        output = client.generate()

        expected_output = self.load_output('chinook_tracks_csv.json')

        self.assertProvCounts(output, expected_output)
