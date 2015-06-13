import os
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

    def parse_file(self):
        uri = self.options.uri

        name = os.path.splitext(os.path.basename(uri))[0]

        if not utils.is_remote(self.options.uri):
            uri = os.path.abspath(uri)

        return {
            'origins:id': name,
            'prov:label': utils.prettify_name(name),
            'prov:type': 'File',
            'uri': uri,
        }

    def parse_fields(self):
        fields = []

        keys = self.options.keys

        for values in self.options.fields:
            field = dict(zip(keys, values))

            if isinstance(self.options.id, (list, tuple)):
                _id = '/'.join([field[i] for i in self.options.id])
            else:
                _id = field[self.options.id]

            if isinstance(self.options.label, (list, tuple)):
                label = ' '.join([field[i] for i in self.options.label])
            else:
                label = field[self.options.label]

            field['origins:id'] = _id
            field['prov:label'] = label
            field['prov:type'] = 'Field'

            if self.options.description:
                field['origins:description'] = self.options.description

            fields.append(field)

        return fields

    def parse(self):
        file = self.parse_file()
        self.document.add('entity', file)

        fields = self.parse_fields()

        for field in fields:
            self.document.add('entity', field)

            self.document.add('wasInfluencedBy', {
                'prov:influencer': file,
                'prov:influencee': field,
                'prov:type': 'origins:Edge',
            })
