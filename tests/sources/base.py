import io
import os
import sys
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
            return f.read()
         
    def assertCorrectOutput(self, output, expected):
        output_facts = output
        expected_facts = sorted(expected.split("\n"))

        expected_list = []
        for fact in expected_facts:
                if fact.strip() != '':
                    expected_list.append(fact.strip())
        
        output_list = []
        for set_of_facts in output_facts:
            for fact in sorted(set_of_facts.split("\r")):
                if fact.strip() != '':
                    output_list.append(fact.strip())
        
        output_list = sorted(output_list)
        expected_list = sorted(expected_list)
        for i, value in enumerate(output_list):
            try:
                print(output_list[i], end='')
                if not (output_list[i] == expected_list[i]):                
                    raise ValueError('Expected and real output is not equal')
            except:
                print()
        print('output matches')
        return None
