import re
import os
import openpyxl
from datetime import datetime
from . import base
from .. import utils


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
        }
    }

    def parse_workbook(self, wb):
        uri = self.options.uri
        id = self.options.id

        # Extract filename without extension
        name = os.path.splitext(os.path.basename(uri))[0]

        attrs = dict(wb.properties.__dict__)

        if not utils.is_remote(uri):
            uri = os.path.abspath(uri)

        attrs['uri'] = uri
        attrs['created'] = _format_time(attrs['created'])
        attrs['modified'] = _format_time(attrs['modified'])

        # Use the title if it's defined, otherwise prettify the name
        if attrs['title'] != 'Untitled':
            label = attrs['title']
        else:
            label = pretty_name(name)

        if not id:
            id = name

        attrs['origins:ident'] = id
        attrs['prov:label'] = label
        attrs['prov:type'] = 'Workbook'

        return attrs

    def parse_sheet(self, name, workbook, index):
        return {
            'origins:ident': os.path.join(workbook['origins:ident'], name),
            'prov:label': name,
            'prov:type': 'Sheet',
            'index': index,
            'workbook': workbook,
        }

    def parse_column(self, name, sheet, index):
        return {
            'origins:ident': os.path.join(sheet['origins:ident'], name),
            'prov:label': name,
            'prov:type': 'Column',
            'index': index,
            'sheet': sheet,
        }

    def parse(self):
        wb = openpyxl.load_workbook(self.options.uri, use_iterators=True)

        sheets = wb.get_sheet_names()

        workbook = self.parse_workbook(wb)
        self.document.add('entity', workbook)

        for i, sheet_name in enumerate(sheets):
            sheet = self.parse_sheet(sheet_name, workbook, i)
            self.document.add('entity', sheet)

            columns = _column_names(wb, sheet_name)

            for j, column_name in enumerate(columns):
                column = self.parse_column(column_name, sheet, j)
                self.document.add('entity', column)
