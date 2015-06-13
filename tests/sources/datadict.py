from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'datadict'
    output_name = 'chinook_tracks_datadict_csv.json'

    def generate(self):
        path = self.input_path('chinook_tracks_datadict.csv')
        client = self.module.Client(uri=path)
        return client.generate()
