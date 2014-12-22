import requests
from urllib.parse import urljoin
from . import base


class Client(base.Client):
    name = 'Harvest'

    description = 'Generator for Harvest metadata.'

    options = {
        'required': ['url'],

        'properties': {
            'url': {
                'description': 'URL of the Harvest API endpoint.',
                'type': 'string',
            },
            'token': {
                'description': 'Authentication token for Harvest.',
                'type': 'string',
            }
        }
    }

    def setup(self):
        self._urls = self.send_request(path='/')

        # Get the concepts
        url = self._urls['_links']['concepts']['href']
        self._concepts = self.send_request(url, params={'embed': 1})

    def send_request(self, url=None, path=None, params=None, data=None):
        headers = {
            'Accept': 'application/json',
        }

        if self.options.token:
            headers['Api-Token'] = self.options.token

        if not url:
            url = self.options.url

        if path:
            url = urljoin(url, path.lstrip('/'))

        response = requests.get(url, params=params, data=data, headers=headers)
        response.raise_for_status()

        return response.json()

    def parse_service(self):
        return {
            'origins:id': self.options.url,
            'prov:label': self.options.url,
            'prov:type': 'Service',
            'url': self.options.url,
            'version': self._urls['version'],
        }

    def parse_categories(self):
        categories = []
        unique = set()

        for concept in self._concepts:
            category = concept['category']

            if category and category['id'] not in unique:
                unique.add(category['id'])

                categories.append({
                    'origins:id': 'category:{}'.format(category['id']),
                    'prov:label': category['name'],
                    'prov:type': 'Category',
                    'id': category['id'],
                    'name': category['name'],
                    'order': category['order'],
                })

        return categories

    def parse_concepts(self, category):
        concepts = []

        category_id = category['id']

        for attrs in self._concepts:
            if not category and attrs['category']:
                continue

            if category and not attrs['category'] \
                    or attrs['category']['id'] != category_id:
                continue

            attrs = dict(attrs)

            attrs['origins:id'] = 'concept:{}'.format(attrs['id'])
            attrs['prov:label'] = attrs['name']
            attrs['prov:type'] = 'Concept'

            # Remove embedded data
            attrs.pop('_links')
            attrs.pop('fields')
            attrs.pop('category')

            concepts.append(attrs)

        return concepts

    def parse_fields(self, concept):
        fields = []

        concept_id = concept['id']

        for attrs in self._concepts:
            if concept_id != attrs['id']:
                continue

            for field in attrs['fields']:
                field = field.copy()

                field['origins:id'] = 'field:{}'.format(field['id'])
                field['prov:label'] = field['name']
                field['prov:type'] = 'Field'

                # Remove embedded data
                field.pop('_links')
                field.pop('operators')

                fields.append(field)

            break

        return fields

    def parse(self):
        service = self.parse_service()
        self.document.add('entity', service)

        for cat in self.parse_categories():
            self.document.add('entity', cat)

            self.document.add('wasInfluencedBy', {
                'prov:influencer': service,
                'prov:influencee': cat,
            })

            for concept in self.parse_concepts(cat):
                self.document.add('entity', concept)

                self.document.add('wasInfluencedBy', {
                    'prov:influencer': cat,
                    'prov:influencee': concept,
                })

                for field in self.parse_fields(concept):
                    self.document.add('entity', field)

                    self.document.add('wasInfluencedBy', {
                        'prov:influencer': concept,
                        'prov:influencee': field,
                    })
