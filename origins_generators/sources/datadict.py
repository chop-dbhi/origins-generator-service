import csv
from .._csv import UnicodeCsvReader
from .. import utils
from . import base


class Client(base.Client):
    name = 'Data Dictionary'

    description = '''
        Generator for data dictionary-like formats where the
        columns are the attribute keys and the rows represent
        the fields or variables in the data dictionary.
    '''

    options = {
        'required': ['uri'],

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
            'domain': {
                'description': 'Domain to add new facts to.',
                'type': 'string',
            },
            'time': {
                'description': 'Valid Time for facts being generated',
                'type': 'string',
            },
            'delimiter': {
                'description': 'The delimiter of the file.',
                'type': 'string',
                'default': ',',
            },
            'id': {
                'description': 'The field name or an array of field names representing the identifier. Defaults to the first column.',  # noqa
                'anyOf': [{
                    'type': 'string',
                }, {
                    'type': 'array',
                    'minItems': 2,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                    },
                }],
            },
            'label': {
                'description': 'The field name or an array of field names representing the label. Defaults to the second column.',  # noqa
                'anyOf': [{
                    'type': 'string',
                }, {
                    'type': 'array',
                    'minItems': 2,
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                    },
                }],
            },
            'type': {
                'description': 'The field name of the type.',  # noqa
                'type': 'string',
            },
            'description': {
                'description': 'The field name of the description.',  # noqa
                'type': 'string',
            },
        }
    }

    def setup(self):
        f = utils.get_file(self.options.uri,
                           encoding=self.options.encoding)

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

        if not self.options.id:
            self.options.id = self.options.keys[0]

        if not self.options.label:
            self.options.label = self.options.keys[1]

        self.options.fields = list(r)

    def parse(self):
        with open(self.options.uri, 'rU', newline='') as f:
            # Get header
            reader = csv.reader(f)
            FIELDS = next(reader)

            yield [
                'operation',
                'domain',
                'entity',
                'attribute',
                'value',
                'valid_time'
            ]

            reader = csv.DictReader(f, fieldnames=FIELDS)
            for line in reader:
                for key, value in line.items():
                    if key != FIELDS[0]:
                        yield [
                            'assert',
                            self.options.domain,
                            line[FIELDS[0]],
                            key,
                            value,
                            self.options.time
                        ]
