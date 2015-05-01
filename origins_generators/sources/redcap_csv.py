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
        'required': ['uri'],

        'properties': {
            'uri': {
                'description': 'The local path or URL to the file',
                'type': 'string',
            },
            'domain': {
                'description': 'Domain to add new facts to.',
                'type': 'string',
            },
            'time': {
                'description': 'Valid Time for facts being generated',
                'type': 'string',
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

    def parse(self):
        with open(self.options.uri, 'rU') as f:
            FACT_FIELDS = ('operation', 'domain', 'entity', 'attribute',
                           'value', 'valid_time')
            reader = rcreader(f)
            printed_header = False;
          
            for line in reader:
                for key, value in line.items():
                    if key != "field_name":
                        yield ','.join([
                                       'assert', 
                                       self.options.domain,
                                       line['field_name'], 
                                       key, 
                                       value,
                                       self.options.time
                                  ]))
