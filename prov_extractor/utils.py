import re
import time
import codecs
import requests
import jsonschema
import dateutil.parser
from io import StringIO


def validate(instance, schema, *args, **kwargs):
    "Wraps JSON schema validator to augment default values."
    jsonschema.validate(instance, schema, *args, **kwargs)

    for prop, attrs in schema['properties'].items():
        if prop not in instance:
            instance[prop] = attrs.get('default')

    return instance


def remove_newlines(s):
    "Replaces newlines with spaces."
    return re.sub(r'\s+', ' ', s.strip())


def prettify_name(name):
    """Prettifies a variable or file name.

    Hyphens and underscores are replaced with spaces and all lowercase tokens
    are title-cased.
    """
    toks = re.sub(r'[-_]+', ' ', name, re.I).split()
    return ' '.join(t.title() if t.islower() else t for t in toks)


def timestamp():
    return int(time.time() * 1000)


def timestr_to_timestamp(s):
    "Converts a time string to a timestamp."
    if s:
        dt = dateutil.parser.parse(s)
        return dt_to_timestamp(dt)


def dt_to_timestamp(dt):
    if dt:
        return int(dt.timestamp() * 1000)

html_re = re.compile(r'<\w+(\s+("[^"]*"|\'[^\']*\'|[^>])+)?>|<\/\w+>', re.I)


# REDCap labels can contain HTML. The label must not contain any markup
# for downstream use.
def strip_html(s):
    return html_re.sub('', s)


def is_remote(s):
    return re.match(r'^https?://', s)


def get_file(uri, encoding='utf-8'):
    # URL
    if is_remote(uri):
        resp = requests.get(uri, stream=True)
        resp.raise_for_status()

        return StringIO(resp.content.decode(encoding), newline=None)

    # Filename
    if isinstance(uri, str):
        return codecs.open(uri, 'rU', encoding=encoding)

    # File-like object
    return uri


class IdGenerator():
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        return '_:x{}'.format(self.i)
