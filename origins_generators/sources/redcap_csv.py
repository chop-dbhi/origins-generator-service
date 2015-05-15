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

    def parse(self):
        with open(self.options.uri, 'rU') as f:
            reader = csv.DictReader(f, fieldnames=FIELDS)
            printed_header = False;
            
            if not self.options.time:
                self.options.time == get_download_date(self.options.uri)

            for line in reader:
                if not printed_header:
                    printed_header = True
                    yield [
                            'operation',
                            'domain',
                            'entity',
                            'attribute',
                            'value',
                            'valid_time'
                          ]
                else:
                    for key, value in line.items():
                        if key != "field_name":
                            yield (
                                    'assert', 
                                    self.options.domain,
                                    line['field_name'], 
                                    key, 
                                    value,
                                    self.options.time
                                  )
