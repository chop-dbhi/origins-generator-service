import os
import csv
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
            'origins:ident': id,
            'prov:label': self.options.name,
            'prov:type': 'Project',
            'name': self.options.name,
            'uri': os.path.abspath(self.options.uri),
            'download_date': download_date,
        }

    def parse_form(self, project, attrs):
        name = attrs['form_name']

        return {
            'origins:ident': os.path.join(project['origins:ident'], name),
            'prov:label': utils.prettify_name(name),
            'prov:type': 'Form',
            'name': name,
            'project': project,
        }

    def parse_section(self, form, attrs):
        name = attrs['section_header'] or DEFAULT_SECTION

        stripped_name = utils.strip_html(name)

        return {
            'origins:ident': os.path.join(form['origins:ident'],
                                          stripped_name),
            'prov:label': stripped_name,
            'prov:type': 'Section',
            'name': attrs['section_header'],
            'form': form,
        }

    def parse_field(self, section, attrs):
        attrs['origins:ident'] = os.path.join(section['origins:ident'],
                                              attrs['field_name'])
        attrs['prov:label'] = utils.strip_html(attrs['field_label'])
        attrs['prov:type'] = 'Field'
        attrs['section'] = section

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

                # An explicit section is present, switch to section. Otherwise
                # if this is the first section for the form, used the default
                # section name.
                name = attrs['section_header']

                if not section or (name and name != section['name']):
                    section = self.parse_section(form, attrs)
                    self.document.add('entity', section)

                field = self.parse_field(section, attrs)
                self.document.add('entity', field)
