from io import StringIO
import csv
from ..utils import validate, IdGenerator, remove_newlines
from . import JSON_SCHEMA_NS


# List of concepts in order of dependency
ORDERED_PROV_TERMS = (
    'bundle',
    'entity',
    'activity',
    'wasGeneratedBy',
    'used',
    'wasInformedBy',
    'wasStartedBy',
    'wasEndedBy',
    'wasInvalidatedBy',
    'wasDerivedFrom',
    'agent',
    'wasAttributedTo',
    'wasAssociatedWith',
    'actedOnBehalfOf',
    'wasInfluencedBy',
    'specializationOf',
    'alternateOf',
    'hadMember',
    'mentionOf',
)


def client_option(key, option):
    if 'anyOf' in option:
        types = [o['type'] for o in option['anyOf']]
    else:
        types = [option['type']]

    toks = ['*', key, '<{}>'.format('|'.join(types)), '-']

    toks.append(remove_newlines(option['description']))

    if 'default' in option:
        toks.append('Default is {!r}.'.format(option['default']))

    return ' '.join(toks)


def client_docstring(client):
    # Spaced with two newlines
    paras = [
        remove_newlines(client.description),
    ]

    # Set of options for the client
    options = []
    props = dict(client.options['properties'])

    # Put require options first
    if 'required' in client.options:
        required = ['Required:']

        for key in client.options['required']:
            option = props.pop(key)
            opt = client_option(key, option)
            required.append(opt)

        paras.append('\n'.join(required))

    if props:
        optional = ['Optional:']

        # Remaining options are optional
        for key, option in props.items():
            opt = client_option(key, option)
            optional.append(opt)

        paras.append('\n'.join(optional))

    paras.append('\n'.join(options))

    return '\n\n'.join(paras)


class Options():
    def __init__(self, options=None):
        if options:
            self.__dict__.update(options)


class ClientMetaclass(type):
    def __new__(cls, name, bases, attrs):
        newcls = type.__new__(cls, name, bases, attrs)

        # The schema attribute adds the boilerplate properties for the
        # JSON schema format.
        if 'options' in attrs:
            schema = {
                '$schema': JSON_SCHEMA_NS,
                'additionalProperties': False,
            }

            schema.update(newcls.options)

            newcls.schema = schema

        if '__doc__' not in attrs:
            newcls.__doc__ = client_docstring(newcls)

        return newcls


class Document(dict):
    def __init__(self):
        self.idr = IdGenerator()
        self.cids = {}

    def __getitem__(self, key):
        if key not in self:
            self[key] = {}

        return dict.__getitem__(self, key)

    def add(self, concept, cid, attrs=None):
        # No CID provided, generate one
        if attrs is None:
            attrs = cid

            # Create an identifier
            if 'origins:id' in attrs:
                cid = '{}:{}'.format(concept, attrs['origins:id'])
            else:
                cid = self.idr()

            # For resolving references at the end
            self.cids[id(attrs)] = cid

        self[concept][cid] = attrs

    def resolve(self):
        doc = {}

        for concept, items in self.items():
            doc[concept] = {}

            for cid, item in items.items():
                copy = dict(item)
                doc[concept][cid] = copy

                # Map value to the identifiers
                for key, value in copy.items():
                    if value is None:
                        continue

                    # The $ check is for XSD types
                    if isinstance(value, dict):
                        if '$' not in value:
                            try:
                                copy[key] = self.cids[id(value)]
                            except KeyError:
                                raise KeyError('could not find cid for {!r}'
                                               .format(value))

        return doc


class Client(metaclass=ClientMetaclass):
    """Base client class.

    The `name` and `description` class attributes should be defined.
    Optionally `options` is JSON Schema <http://json-schema.org/> that defines
    set of options supported by the client.
    """
    name = ''

    description = ''

    version = '1.0.0'

    options = {}

    @classmethod
    def validate(cls, options):
        """Takes a dict of options and validates them against the client
        options using a JSON schema validator.
        """
        return Options(validate(options, cls.schema))

    def __init__(self, **options):
        self.options = self.validate(options)
        self.document = Document()
        self.setup()

    def setup(self):
        "Post-initialization setup."

    def parse(self):
        "Exports a resource in a JSON-serializable format."
        raise NotImplementedError('export method must be implemented')

    def generate(self):
        gen = self.parse()
        buf = StringIO()
        writer = csv.writer(buf)

        for i, fact in enumerate(gen):
            # Write the fact to the buffer
            writer.writerow(fact)

            if i % 100 == 0:
                yield buf.getvalue()

                # Remove old data for next iteration
                buf.seek(0)
                buf.truncate()

        # Yield the final bit of data
        yield buf.getvalue()
