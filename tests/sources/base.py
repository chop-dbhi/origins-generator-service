import os
import json
import unittest
from origins_generators import sources


class SourceTestCase(unittest.TestCase):
    maxDiff = None

    generator = None

    INPUT_DIR = os.path.join(os.path.dirname(__file__), '../input')
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../output')

    @property
    def module(self):
        if not self.generator:
            raise ValueError('generator must be defined')

        try:
            return sources.get_module(self.generator)
        except ImportError as e:
            self.skipTest(str(e))

    def input_path(self, name):
        return os.path.join(self.INPUT_DIR, name)

    def output_path(self, name):
        return os.path.join(self.OUTPUT_DIR, name)

    def load_output(self, name):
        with open(self.output_path(name)) as f:
            return json.load(f)

    def assertProvCounts(self, output, expected):
        "Asserts two provenance documents has the same number of elements."
        # Ensure they have the same keys
        self.assertEqual(set(output), set(expected))

        # Ensure the number of elements are equal
        for key in output:
            self.assertEqual(len(output[key]), len(expected[key]))
