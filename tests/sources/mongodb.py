from .base import SourceTestCase


class TestCase(SourceTestCase):
    generator = 'mongodb'

    def test(self):
        client = self.module.Client(database='chinook')
        output = client.generate()

        expected_output = self.load_output('chinook_mongodb.json')
        self.assertProvCounts(output, expected_output)
