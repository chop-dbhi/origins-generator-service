from importlib import import_module
from ..exceptions import UnknownSource, SourceNotSupported


JSON_SCHEMA_NS = 'http://json-schema.org/draft-04/schema#'


SOURCES = {
    'sqlite': 'origins_generators.sources.sqlite',
    'postgresql': 'origins_generators.sources.postgresql',
    'delimited': 'origins_generators.sources.delimited',
    'filesystem': 'origins_generators.sources.filesystem',
    'excel': 'origins_generators.sources.excel',
    'mongodb': 'origins_generators.sources.mongodb',
    'mysql': 'origins_generators.sources.mysql',
    'oracle': 'origins_generators.sources.oracle',
    'vcf': 'origins_generators.sources.vcf',
    'redcap-mysql': 'origins_generators.sources.redcap_mysql',
    'redcap-api': 'origins_generators.sources.redcap_api',
    'redcap-csv': 'origins_generators.sources.redcap_csv',
    'harvest': 'origins_generators.sources.harvest',
    'datadict': 'origins_generators.sources.datadict',
    'github-issues': 'origins_generators.sources.github_issues',
    'git': 'origins_generators.sources.git',
    'entities-csv': 'origins_generators.sources.entities_csv',
    'links-csv': 'origins_generators.sources.links_csv',
}

SOURCE_ALIASES = {
    'redcap': {
        'source': 'redcap-mysql',
    },
    'csv': {
        'source': 'delimited',
        'options': {
            'delimiter': ',',
        }
    },
    'tab': {
        'source': 'delimited',
        'options': {
            'delimiter': '\t',
        }
    }
}


_modules = {}


def get_module(name):
    "Attempts to import a source by name."
    if name in SOURCE_ALIASES:
        name = SOURCE_ALIASES[name]['source']

    if name in _modules:
        return _modules[name]

    module = SOURCES.get(name)

    if not module:
        raise UnknownSource(name)

    try:
        module = import_module(module)
    except ImportError as e:
        raise SourceNotSupported(str(e))

    _modules[name] = module
    return module


def get(name):
    "Returns the client class of a source."
    return get_module(name).Client
