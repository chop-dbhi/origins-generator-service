import os
import requests
from . import base
from .. import utils


DEFAULT_SECTION = 'General'


class Client(base.Client):
    options = {
        'required': ['name', 'url', 'token'],

        'properties': {
            'name': {
                'description': 'Name of the project.',
                'type': 'string',
            },
            'url': {
                'description': 'URL endpoint to the API.',
                'type': 'string',
            },
            'token': {
                'description': 'API token for authorization.',
                'type': 'string',
            },
            'verify_ssl': {
                'description': 'Require SSL certificate verfication.',
                'type': 'boolean',
                'default': True,
            },
        }
    }

    def setup(self):
        resp = requests.post(self.options.url, data={
            'token': self.options.token,
            'content': 'metadata',
            'format': 'json',
            'verify': self.options.verify_ssl,
        })
        resp.raise_for_status()

        self.metadata = resp.json()

    def parse_project(self):
        return {
            'origins:id': self.options.name,
            'prov:label': self.options.name,
            'prov:type': 'Project',
            'name': self.options.name,
        }

    def parse_form(self, project, attrs):
        name = attrs['form_name']

        return {
            'origins:id': os.path.join(project['origins:id'], name),
            'prov:label': utils.prettify_name(name),
            'prov:type': 'Form',
            'name': name,
        }

    def parse_section(self, form, attrs):
        name = attrs['section_header'] or DEFAULT_SECTION

        stripped_name = utils.strip_html(name)

        return {
            'origins:id': os.path.join(form['origins:id'], stripped_name),
            'prov:label': stripped_name,
            'prov:type': 'Section',
            'name': attrs['section_header'],
        }

    def parse_field(self, section, attrs):
        identifier = attrs['identifier'].lower() == 'y' and True or False
        required = attrs['required_field'].lower() == 'y' and True or False

        field = {
            'origins:id': os.path.join(section['origins:id'],
                                       attrs['field_name']),
            'prov:label': utils.strip_html(attrs['field_label']),
            'prov:type': 'Field',
            'name': attrs['field_name'],
            'label': attrs['field_label'],
            'note': attrs['field_note'],
            'type': attrs['field_type'],
            'choices': attrs['select_choices_or_calculations'],
            'display_logic': attrs['branching_logic'],
            'validation_type': attrs['text_validation_type_or_show_slider_number'],  # noqa
            'validation_min': attrs['text_validation_min'],
            'validation_max': attrs['text_validation_max'],
            'identifier': identifier,
            'required': required,
            'alignment': attrs['custom_alignment'],
            'survey_num': attrs['question_number'],
            'matrix': attrs['matrix_group_name'],
        }

        return field

    def parse(self):
        project = self.parse_project()
        self.document.add('entity', project)

        form = None
        section = None

        for attrs in self.metadata:
            if not form or attrs['form_name'] != form['name']:
                form = self.parse_form(project, attrs)
                self.document.add('entity', form)

                # Reset section
                section = None

                self.document.add('wasInfluencedBy', {
                    'prov:influencer': project,
                    'prov:influencee': form,
                    'prov:type': 'origins:Edge',
                })

            # An explicit section is present, switch to section. Otherwise
            # if this is the first section for the form, used the default
            # section name.
            name = attrs['section_header']

            if not section or (name and name != section['name']):
                section = self.parse_section(form, attrs)
                self.document.add('entity', section)

                self.document.add('wasInfluencedBy', {
                    'prov:influencer': form,
                    'prov:influencee': section,
                    'prov:type': 'origins:Edge',
                })

            field = self.parse_field(section, attrs)
            self.document.add('entity', field)

            self.document.add('wasInfluencedBy', {
                'prov:influencer': section,
                'prov:influencee': field,
                'prov:type': 'origins:Edge',
            })
