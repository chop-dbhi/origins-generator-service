import os
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from . import base
from .. import utils


class Client(base.Client):
    name = 'SQLite'

    description = '''
        Generator for a SQLite database. The database, tables, and columns
        are extracted as entities.
    '''

    options = {
        'required': ['uri'],

        'properties': {
            'uri': {
                'description': 'URI of the database.',
                'type': 'string',
            },
            'name': {
                'description': 'Name of the database.',
                'type': 'string',
            },
            'id': {
                'description': 'Identifier for the database.',
                'type': 'string',
            },
        }
    }

    def setup(self):
        uri = os.path.abspath(self.options.uri)
        # Triple slashes is not a mistake, absolute paths need four slashes
        # in total
        self.engine = create_engine('sqlite+pysqlite:///{}'.format(uri))
        self.insp = reflection.Inspector.from_engine(self.engine)

    def parse_database(self):
        uri = self.options.uri

        if self.options.id:
            id = self.options.id
        else:
            id = os.path.basename(uri)

        if self.options.name:
            name = self.options.name
        else:
            basename = os.path.splitext(os.path.basename(uri))[0]
            name = utils.prettify_name(basename)

        return {
            'origins:ident': id,
            'prov:label': name,
            'prov:type': 'Database',
            'name': name,
        }

    def parse_tables(self, db):
        tables = []

        for name in self.insp.get_table_names():
            tables.append({
                'origins:ident': os.path.join(db['origins:ident'], name),
                'prov:label': name,
                'prov:type': 'Table',
                'name': name,
                'database': db,
            })

        return tables

    def parse_columns(self, table):
        columns = []

        for attrs in self.insp.get_columns(table['name']):
            column = {
                'origins:ident': os.path.join(table['origins:ident'],
                                              attrs['name']),
                'prov:label': attrs['name'],
                'prov:type': 'Column',
                'name': attrs['name'],
                'type': str(attrs['type']),
                'nullable': attrs['nullable'],
                'default': attrs['default'],
                'table': table,
            }

            # Extract optional attributes
            if 'attrs' in attrs:
                column.update(attrs['attrs'])

            columns.append(column)

        return columns

    def parse(self):
        db = self.parse_database()
        self.document.add('entity', db)

        for table in self.parse_tables(db):
            self.document.add('entity', table)

            for column in self.parse_columns(table):
                self.document.add('entity', column)
