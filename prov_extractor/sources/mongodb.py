import os
import pymongo
from bson.code import Code
from . import base


# Map-reduce functions for getting and counting the unique fields
# across documents in a collection.
map_fields = Code('''
    function() {
        for (var key in this) {
            emit(key, 1);
        }
    }
''')

count_fields = Code('''
    function(key, values) {
        return Array.sum(values);
    }
''')


class Client(base.Client):
    name = 'MongoDB'

    description = '''
        Generator for a MongoDB database. The database, collections, and
        document fields are extracted as entities.
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
                'default': 27017
            },
        }
    }

    def setup(self):
        self.conn = pymongo.MongoClient(host=self.options.host,
                                        port=self.options.port)

        self.db = self.conn[self.options.database]

    def get_collections(self):
        "Return a list of collection dicts in the database."
        return [{
            'name': n,
        } for n in self.db.collection_names() if n != 'system.indexes']

    def get_fields(self, collection_name):
        """Return a list of field dicts in the collection.

        This performs a map-reduce job on the collection to get the unique set
        of fields across documents.
        """
        output = self.db[collection_name]\
            .inline_map_reduce(map_fields,
                               count_fields,
                               full_response=True)

        # result['value'] / output['counts']['input'] would produce the
        # occurrence of the field across documents.
        fields = []

        for result in output['results']:
            fields.append({
                'name': result['_id']
            })

        return fields

    def parse_database(self):
        name = self.options.database
        version = self.conn.server_info()['version']

        return {
            'origins:ident': name,
            'prov:label': name,
            'prov:type': 'Database',
            'version': version
        }

    def parse_collection(self, attrs, db):
        attrs['origins:ident'] = os.path.join(db['origins:ident'],
                                              attrs['name'])
        attrs['prov:label'] = attrs['name']
        attrs['prov:type'] = 'Collection'
        attrs['database'] = db

        return attrs

    def parse_field(self, attrs, col):
        attrs['origins:ident'] = os.path.join(col['origins:ident'],
                                              attrs['name'])
        attrs['prov:label'] = attrs['name']
        attrs['prov:type'] = 'Field'
        attrs['column'] = col

        return attrs

    def parse(self):
        db = self.parse_database()
        self.document.add('entity', db)

        for col in self.get_collections():
            col = self.parse_collection(col, db)
            self.document.add('entity', col)

            for field in self.get_fields(col['name']):
                field = self.parse_field(field, col)
                self.document.add('entity', field)
