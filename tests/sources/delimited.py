from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'delimited'
    output_name = 'chinook_tracks_csv.json'

    def generate(self):
        path = self.input_path('chinook_tracks.csv')
        client = self.module.Client(uri=path)
        return client.generate()
