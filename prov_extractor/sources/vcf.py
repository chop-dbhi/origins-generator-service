import os
import vcf
from . import base
from .. import utils


FIXED_FIELDS = (
    ('CHROM', 'Chromosome'),
    ('POS', 'Position'),
    ('ID', 'Unique identifier'),
    ('REF', 'Reference base(s)'),
    ('ALT', 'Alternate non-reference alleles'),
    ('QUAL', 'Phred-scale quality score for assertion made in ALT'),
    ('FILTER', 'PASS or filters that have not passed'),
)


class Client(base.Client):
    name = 'VCF'

    description = '''
        Generator for Variant Call Format (VCF) text files. The pre-defined
        fields, INFO fields, and FORMAT fields are parsed as entities.
    '''

    options = {
        'properties': {
            'uri': {
                'description': 'A URL or local filesystem path to a file.',
                'type': 'string',
            },
        }
    }

    def setup(self):
        f = utils.get_file(self.options.uri)

        self.reader = vcf.Reader(f)

    def parse_file(self):
        uri = self.options.uri

        name = os.path.splitext(os.path.basename(uri))[0]

        if not utils.is_remote(self.options.uri):
            uri = os.path.abspath(uri)

        attrs = {
            'origins:id': name,
            'prov:label': utils.prettify_name(name),
            'prov:type': 'VCF File',
            'uri': uri,
        }

        attrs.update(self.reader.metadata)

        return attrs

    def parse_fields(self, parent):
        index = 0
        fields = []
        parent_id = parent['origins:id']

        # Fixed fields
        for name, desc in FIXED_FIELDS:
            fields.append({
                'origins:id': os.path.join(parent_id, name),
                'prov:label': name,
                'prov:type': 'Field',
                'name': name,
                'description': desc,
                'index': index,
            })

            index += 1

        keys = ('name', 'num_values', 'type', 'description')

        # INFO fields
        for row in self.reader.infos.values():
            attrs = dict(zip(keys, row))

            attrs['origins:id'] = os.path.join(parent_id, name)
            attrs['prov:label'] = name
            attrs['prov:type'] = 'Field'
            attrs['index'] = index

            fields.append(attrs)
            index += 1

        # FORMAT fields
        for row in self.reader.formats.values():
            attrs = dict(zip(keys, row))

            attrs['origins:id'] = os.path.join(parent_id, name)
            attrs['prov:label'] = name
            attrs['prov:type'] = 'Field'
            attrs['index'] = index

            fields.append(attrs)
            index += 1

        return fields

    def parse(self):
        _file = self.parse_file()
        self.document.add('entity', _file)

        for field in self.parse_fields(_file):
            self.document.add('entity', field)

            self.document.add('wasInfluencedBy', {
                'prov:influencer': _file,
                'prov:influencee': field,
                'prov:type': 'origins:Edge',
            })
