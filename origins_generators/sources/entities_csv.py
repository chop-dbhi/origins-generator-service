import re
import csv
import codecs
import requests
from io import StringIO
from .._csv import UnicodeCsvReader
from . import base
from .. import utils


class Client(base.Client):
    name = 'Entities CSV'

    description = '''
        Simple CSV-based format for creating bare entities. A header must be
        present with the first four columns being: id, label, type, and
        description. Columns following that will be treated as properties.
        Rows with empty column values will not be added a property which
        allows for mixing different types of entities.
    '''

    options = {
        'properties': {
            'uri': {
                'description': 'A URL or local filesystem path to a file.',
                'type': 'string',
            },
            'encoding': {
                'description': 'The character encoding of the file.',
                'type': 'string',
                'default': 'utf-8',
            },
            'delimiter': {
                'description': 'The delimiter of the file.',
                'type': 'string',
                'default': ',',
            },
        }
    }

    def setup(self):
        f = utils.get_file(self.options.uri)

        sniff = 1024
        dialect = None

        # Infer various properties about the file
        # Sample the file to determine the dialect
        sample = '\n'.join([l for l in f.readlines(sniff)])
        f.seek(0)

        # Determine dialect
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)

        # Bind the reader to be parsed
        r = UnicodeCsvReader(f,
                             dialect=dialect,
                             delimiter=self.options.delimiter,
                             encoding=self.options.encoding)

        # The header contains the field names. Ignore overflow.
        # As a side effect, this also skips the header.
        self.options.keys = [v for v in next(r) if v]
        self.options.fields = list(r)

    def parse_field(self, values):
        keys = self.options.keys

        attrs = {
            'origins:id': values[0],
            'prov:label': values[1],
            'prov:type': values[2],
            'origins:description': values[3],
        }

        # Add the remaining properties
        for i, k in enumerate(keys[4:], 4):
            if values[i]:
                attrs[k] = values[i]

        return attrs

    def parse(self):
        for values in self.options.fields:
            field = self.parse_field(values)
            self.document.add('entity', field)
