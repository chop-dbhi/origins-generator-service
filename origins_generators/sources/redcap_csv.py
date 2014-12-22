import re
import os
import csv
import time
from datetime import datetime
from . import base
from .. import utils


FIELDS = (
    'field_name',
    'form_name',
    'section_header',
    'field_type',
    'field_label',
    'choices_calcs_slider',
    'field_note',
    'text_validation_type',
    'text_validation_min',
    'text_validation_max',
    'identifier',
    'branching_logic',
    'required',
    'custom_alignment',
    'question_number',
    'matrix_group_name',
)


DEFAULT_SECTION = 'General'


# REDCap data dictionaries contain the date in the filename. This attempts
# to extract it.
def get_download_date(path):
    return os.path.basename(path).split('.')[0].split('_')[-1]


def rcreader(f):
    # Skip header
    next(f)

    for row in csv.reader(f):
        yield dict(zip(FIELDS, row))


class Client(base.Client):
    name = 'REDCap Data Dictionary'

    description = 'Generator for REDCap data dictionary exports.'

    options = {
        'required': ['uri', 'name'],

        'properties': {
            'uri': {
                'description': 'The local path or URL to the file',
                'type': 'string',
            },
            'name': {
                'description': 'Name of the project.',
                'type': 'string',
            },
            'id': {
                'description': 'Identifier for the project.',
                'type': 'string',
            },
        }
    }

    def parse_project(self):
        if self.options.id:
            id = self.options.id
        else:
            id = self.options.name

        # This could be a remote file, so there is no guarantee we can get this
        try:
            download_date = get_download_date(self.options.uri)
        except Exception:
            download_date = None

        return {
            'origins:id': id,
            'prov:label': self.options.name,
            'prov:type': 'Project',
            'name': self.options.name,
            'uri': os.path.abspath(self.options.uri),
            'download_date': download_date,
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
        attrs['origins:id'] = os.path.join(section['origins:id'],
                                           attrs['field_name'])
        attrs['prov:label'] = strip_html(attrs['field_label'])
        attrs['prov:type'] = 'Field'

        return attrs

    def parse(self):
        project = self.parse_project()
        self.document.add('entity', project)

        form = None
        section = None

        with open(self.options.uri, 'rU') as f:
            reader = rcreader(f)

            for attrs in reader:
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
