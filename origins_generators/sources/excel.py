import re
import os
import openpyxl
from datetime import datetime
from . import base


OPENPYXL_MAJOR_VERSION = int(openpyxl.__version__[0])

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%Z'


def pretty_name(name):
    return re.sub(r'[-_.]+', ' ', name, re.I).title()


def _format_time(d):
    return datetime.strftime(d, DATETIME_FORMAT)


def _column_names(workbook, sheet_name):
    sheet = workbook.get_sheet_by_name(sheet_name)
    first_row = next(sheet.iter_rows())

    # Renamed attribute in version 2+
    if OPENPYXL_MAJOR_VERSION > 1:
        return [c.value for c in first_row]

    return [c.internal_value for c in first_row]

    # Fallback to indexes
    return range(len(first_row))


class Client(base.Client):
    name = 'Microsoft Excel'

    description = '''
        Generator for Microsoft Excel 2007+ files. The workbook, sheets, and
        columns form the hierarchy. Sheets are expected to be column-based
        files (like a CSV).
    '''

    options = {
        'required': ['uri'],

        'properties': {
            'uri': {
                'description': 'A URL or local filesystem path to a file.',
                'type': 'string',
            },
            'id': {
                'description': 'Identifier for the workbook.',
                'type': 'string',
            },
            'valid_time': {
                'description': 'Valid time for new facts',
                'type': 'string',
                'default': None,
            },
            'domain': {
                'description': 'Domain for new facts',
                'type': 'string',
                'default': None,
            }
        }
    }

    def parse(self):
        wb = openpyxl.load_workbook(self.options.uri, use_iterators=True)
        sheets = wb.get_sheet_names()
        name = os.path.splitext(os.path.basename(self.options.uri))[0]

        yield [
            'operation',
            'domain',
            'entity',
            'attribute',
            'value',
            'valid_time'
        ]

        for i, sheet_name in enumerate(sheets):
            columns = _column_names(wb, sheet_name)
            sheet = wb.get_sheet_by_name(sheet_name)
            for j, column_name in enumerate(columns):
                column = sheet.columns[j]
                for k, cell in enumerate(column):
                    if cell.value is not None:
                        yield [
                            'assert',
                            self.options.domain,
                            (name + '_' + sheet_name),
                            column_name + '_' + str(k),
                            cell.value,
                            self.options.valid_time
                        ]
