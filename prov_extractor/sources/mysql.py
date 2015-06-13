import os
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.engine.url import URL
from . import base


class Client(base.Client):
    name = 'MySQL'

    description = '''
        Generator for a MySQL database. The database, tables, and columns
        are extracted as entities.
    '''

    options = {
        'required': ['database'],

        'properties': {
            'database': {
                'description': 'Name of the database.',
                'type': 'string',
            },
            'host': {
                'description': 'Host of the server.',
                'type': 'string',
                'default': 'localhost',
            },
            'port': {
                'description': 'Port of the server.',
                'type': 'number',
                'default': 3306,
            },
            'user': {
                'description': 'Username for authentication.',
                'type': 'string',
            },
            'password': {
                'description': 'Password for authentication',
                'type': 'string',
            }
        }
    }

    def setup(self):
        # Construct engine URL
        url = URL('mysql+pymysql',
                  username=self.options.user,
                  password=self.options.password,
                  host=self.options.host,
                  port=self.options.port,
                  database=self.options.database)

        self.engine = create_engine(url)
        self.insp = reflection.Inspector.from_engine(self.engine)

    def parse_database(self):
        return {
            'origins:ident': self.options.database,
            'prov:label': self.options.database,
            'prov:type': 'Database',
            'name': self.options.database,
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
